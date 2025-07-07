import matplotlib
import os
import argparse
from PIL import Image
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from torchvision.models import resnet34, ResNet34_Weights

matplotlib.use('Agg')  # 非交互式后端，避免 plt.show() 报错

# --------- MixUp 函数定义 ---------
def mixup_data(x, y, alpha=1.0):
    '''Returns mixed inputs, pairs of targets, and lambda'''
    if alpha > 0:
        lam = np.random.beta(alpha, alpha) ## 从Beta分布中随机采样混合系数
    else:
        lam = 1 # 如果alpha<=0，则不混合

    batch_size = x.size()[0]
    index = torch.randperm(batch_size).to(x.device) #生成一个随机排列的索引，用于选择另一批样本与当前批混合。

    mixed_x = lam * x + (1 - lam) * x[index, :] #混合图像 = λ * 原图像 + (1-λ) * 随机另一图像
    y_a, y_b = y, y[index]
    return mixed_x, y_a, y_b, lam

# --------- Focal Loss 定义 ---------
class FocalLoss(nn.Module):
    def __init__(self, alpha=0.25, gamma=2.0, reduction='mean'):
        super(FocalLoss, self).__init__()
        self.alpha = alpha  # 正样本的权重因⼦，⽤于调整类别不平衡
        self.gamma = gamma  # 调节因⼦，控制对难易样本的关注度
        self.reduction = reduction  # 指定返回的损失形式：均值、求和或⽆归约
        self.ce = nn.CrossEntropyLoss(reduction='none')  # 计算交叉熵损失，返回每个样本的损失，不做聚合

    def forward(self, inputs, targets):
        ce_loss = self.ce(inputs, targets)  # 计算每个样本的交叉熵损失
        pt = torch.exp(-ce_loss)   # 计算预测正确类别的概率 pt，因为 CE = -log(pt)，故 pt = exp(-CE)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        # 对交叉熵损失加权：
        # 1. (1 - pt)^gamma：对容易分类（pt ⼤）的样本降低权重，对难分类（pt ⼩）的样本提升权重
        # 2. alpha：平衡正负样本⽐例，防⽌类别不平衡
        # 3. ce_loss：原始的交叉熵损失，保证损失的基本形式

        # 根据 reduction 参数返回不同形式的损失结果
        if self.reduction == 'mean':
            return focal_loss.mean() # 返回所有样本损失的平均值
        elif self.reduction == 'sum':
            return focal_loss.sum() # 返回所有样本损失的和
        else:
            return focal_loss # 返回每个样本的损失，不做聚合

# --------- 数据集定义 ---------
class MaskDataset(Dataset):
    def __init__(self, root_dir, phase='train', img_size=128):
        self.images = [] #存储图片路径
        self.labels = [] #存储对应标签
        self.transform = transforms.Compose([
            transforms.Resize((img_size, img_size)), #将图像调整为统一尺寸
            transforms.RandomHorizontalFlip(),#随机翻转，为了提升模型泛化能力
            transforms.RandomRotation(15),#随机旋转，模拟头部轻微倾斜
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),#调整图像亮度等参数
            transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),#随机平移图像，模拟视角变化
            transforms.ToTensor(),#转换为张量并归一
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])#标准化
        ])
        classes = ['NG-mask', 'OK-mask']
        for label, cls in enumerate(classes):
            folder = os.path.join(root_dir, phase, cls) #构建类别目录路径
            for fname in sorted(os.listdir(folder)):
                if fname.lower().endswith(('.jpg', '.png')):#文件名转小写后过滤图像文件
                    self.images.append(os.path.join(folder, fname)) #存储路径
                    self.labels.append(label) #存储标签

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img = Image.open(self.images[idx]).convert('RGB')
        img = self.transform(img)
        lbl = self.labels[idx]
        return img, lbl

# --------- 模型定义 ---------
class BaseMaskNet(nn.Module):
    def __init__(self, pretrained=True, num_classes=2):
        super().__init__()
        #如果pretrained=True，则加载在ImageNet上预训练的权重；否则随机初始化
        weights = ResNet34_Weights.DEFAULT if pretrained else None #获取ResNet34的默认预训练权重
        self.backbone = resnet34(weights=weights) #创建标准的ResNet34模型
        in_feats = self.backbone.fc.in_features #获取原模型全连接层的输入特征维度
        self.backbone.fc = nn.Linear(in_feats, num_classes)#将原来的1000类分类器（针对ImageNet）替换为新的全连接层
    #前向传播
    def forward(self, x):
        return self.backbone(x)

# --------- 验证函数 ---------
def validate(model, loader, device):
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for imgs, labels in loader:
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs)
            preds = outputs.argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    return correct / total if total > 0 else 0


# --------- 训练和验证 ---------
def train_and_validate(args):
    train_ds = MaskDataset(args.data_root, 'train', args.img_size)
    val_ds   = MaskDataset(args.data_root, 'val', args.img_size)
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=4)
    val_loader   = DataLoader(val_ds,   batch_size=args.batch_size, shuffle=False, num_workers=4)

    # 设备选择
    if torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    print(f"Using device: {device}")

    model = BaseMaskNet(pretrained=args.pretrained).to(device)
    # 损失函数
    criterion = FocalLoss(alpha=0.25, gamma=2.0)
    # 优化器
    optimizer = getattr(torch.optim, args.optimizer)(model.parameters(), lr=0.00015, weight_decay=args.weight_decay)

    best_acc = 0.0
    train_losses, train_accs = [], []
    val_losses, val_accs = [], []

    for epoch in range(1, args.epochs + 1):
        model.train()
        running_loss, correct, total = 0.0, 0, 0

        for imgs, labels in train_loader:
            imgs, labels = imgs.to(device), labels.to(device)

            # 应用 MixUp 数据增强
            imgs, targets_a, targets_b, lam = mixup_data(imgs, labels, alpha=1.0)

            outputs = model(imgs)
            loss = lam * criterion(outputs, targets_a) + (1 - lam) * criterion(outputs, targets_b)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * labels.size(0)

            # 计算预测准确率（按预测值与 labels 匹配）
            preds = outputs.argmax(dim=1)
            correct += (lam * (preds == targets_a).sum().item()
                        + (1 - lam) * (preds == targets_b).sum().item())
            total += labels.size(0)

        epoch_loss = running_loss / total
        epoch_acc = correct / total
        train_losses.append(epoch_loss)
        train_accs.append(epoch_acc)
        # val_acc = validate(model, val_loader, device)
        # val_accs.append(val_acc)
        # 验证阶段加上 loss 统计
        model.eval()
        val_loss, correct, total = 0.0, 0, 0
        with torch.no_grad():
            for imgs, labels in val_loader:
                imgs, labels = imgs.to(device), labels.to(device)
                outputs = model(imgs)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * labels.size(0)
                preds = outputs.argmax(dim=1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)
        val_acc = correct / total
        val_loss = val_loss / total  # 平均验证损失
        val_accs.append(val_acc)
        val_losses.append(val_loss)  # ✅ 关键补充

        current_lr = optimizer.param_groups[0]['lr']
        print(f'Epoch {epoch}/{args.epochs} | '
              f'Train Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f} | '
              f'Val Acc: {val_acc:.4f} | LR: {current_lr:.6f}')

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), args.checkpoint_path)

    # 训练曲线图表
    # df = pd.DataFrame({'Epoch': list(range(1, args.epochs + 1)),
    #                    'Train Loss': train_losses,
    #                    'Val Loss': val_losses,
    #                    'Train Acc': train_accs,
    #                    'Val Acc': val_accs})
    #
    # plt.rcParams.update({
    #     'font.size': 12,  # 统一基础字号
    #     'axes.titlesize': 12,  # 标题字号
    #     'axes.labelsize': 12,  # 坐标轴标签
    #     'xtick.labelsize': 11,  # X轴刻度
    #     'ytick.labelsize': 11  # Y轴刻度
    # })
    #
    # plt.figure(figsize=(8, 6))
    # sns.set_style("whitegrid")
    #
    # ax1 = sns.lineplot(data=df, x='Epoch', y='Train Loss', marker='o', label='Train Loss',linewidth=2)#损失曲线
    # sns.lineplot(data=df, x='Epoch', y='Train Acc', marker='s', label='Train Acc',linewidth=2) #准确率曲线
    # ax2 = sns.lineplot(data=df, x='Epoch', y='Val Loss', marker='o', label='Val Loss',linewidth=2) #损失曲线
    # sns.lineplot(data=df, x='Epoch', y='Val Acc', marker='s', label='Val Acc',linewidth=2) #准确率曲线
    #
    # ax1.set_title("Training Loss and Accuracy over Epochs")
    # ax2.set_title("Testing Loss and Accuracy over Epochs")
    # ax1.set_ylabel('Loss Value')
    # ax1.set_xlabel('Epoch')
    #
    # plt.tight_layout()
    # plt.savefig(os.path.join(args.output_dir, 'training_curves_seaborn.png'), dpi=300,bbox_inches='tight')
    # plt.show()
    #
    # ax2.set_ylabel('Accuracy')
    # ax2.set_xlabel('Epoch')
    # ax2.ylim(0, 1.0) # 留出顶部空间
    # plt.legend()
    #
    # plt.tight_layout()
    # plt.savefig(os.path.join(args.output_dir, 'accuracy_curves_seaborn.png'), dpi=300,bbox_inches='tight')
    # plt.show()

    # 训练结果可视化
    df = pd.DataFrame({
        'Epoch': list(range(1, args.epochs + 1)),
        'Train Loss': train_losses,
        'Val Loss': val_losses,
        'Train Acc': train_accs,
        'Val Acc': val_accs
    })

    # 设置统一样式
    plt.rcParams.update({
        'font.size': 12,
        'axes.titlesize': 12,
        'axes.labelsize': 12,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11
    })
    sns.set_style("whitegrid")

    # ----------- 1. 训练曲线图 -----------
    plt.figure(figsize=(8, 6))
    plt.plot(df['Epoch'], df['Train Loss'], marker='o', label='Train Loss', linewidth=2)
    plt.plot(df['Epoch'], df['Train Acc'], marker='s', label='Train Accuracy', linewidth=2)
    plt.title("Training Loss and Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Value")
    plt.ylim(0, 1.0)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(args.output_dir, 'train_curves.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # ----------- 2. 验证曲线图 -----------
    plt.figure(figsize=(8, 6))
    plt.plot(df['Epoch'], df['Val Loss'], marker='o', label='Validation Loss', linewidth=2)
    plt.plot(df['Epoch'], df['Val Acc'], marker='s', label='Validation Accuracy', linewidth=2)
    plt.title("Validation Loss and Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Value")
    plt.ylim(0, 1.0)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(args.output_dir, 'val_curves.png'), dpi=300, bbox_inches='tight')
    plt.close()

# --------- 测试函数 ---------
# def test(args):
#     device = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
#     model = BaseMaskNet(pretrained=False).to(device)
#     model.load_state_dict(torch.load(args.checkpoint_path, map_location=device))
#     model.eval()
#
#     val_ds = MaskDataset(args.data_root, 'val', args.img_size)
#     loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=4)
#
#     all_preds, all_labels = [], []
#     with torch.no_grad():
#         for imgs, labels in loader:
#             imgs = imgs.to(device)
#             outputs = model(imgs)
#             preds = outputs.argmax(dim=1).cpu().tolist()
#             all_preds.extend(preds)
#             all_labels.extend(labels.tolist())
#
#     print("\nClassification Report:")
#     print(classification_report(all_labels, all_preds, target_names=['NG-mask', 'OK-mask']))
#     print("Confusion Matrix:")
#     print(confusion_matrix(all_labels, all_preds))
def test(args):
    device = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
    model = BaseMaskNet(pretrained=False).to(device)
    model.load_state_dict(torch.load(args.checkpoint_path, map_location=device))
    model.eval()

    val_ds = MaskDataset(args.data_root, 'val', args.img_size)
    loader = DataLoader(val_ds, batch_size=1, shuffle=False, num_workers=4)

    all_preds, all_labels = [], []
    wrong_dir = os.path.join(args.output_dir, "wrong_samples")
    os.makedirs(wrong_dir, exist_ok=True)

    # 反归一化
    inv_normalize = transforms.Normalize(
        mean=[-m / s for m, s in zip([0.485, 0.456, 0.406],
                                     [0.229, 0.224, 0.225])],
        std=[1 / s for s in [0.229, 0.224, 0.225]]
    )

    with torch.no_grad():
        for idx, (img_tensor, label) in enumerate(loader):
            img_tensor = img_tensor.to(device)
            output = model(img_tensor)
            pred = output.argmax(dim=1).item()
            true = label.item()
            all_preds.append(pred)
            all_labels.append(true)

            if pred != true:
                # 保存错误图片
                img = inv_normalize(img_tensor.squeeze(0).cpu()).clamp(0, 1)
                img = transforms.ToPILImage()(img)
                filename = f"{idx:03d}_true-{['NG-mask', 'OK-mask'][true]}_pred-{['NG-mask', 'OK-mask'][pred]}.jpg"
                img.save(os.path.join(wrong_dir, filename))

    # 打印分类报告
    print("\nClassification Report:")
    print(classification_report(all_labels, all_preds, target_names=['NG-mask', 'OK-mask']))

    # 混淆矩阵
    cm = confusion_matrix(all_labels, all_preds)
    print("Confusion Matrix:")
    print(cm)

    # 可视化混淆矩阵
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['NG-mask', 'OK-mask'],
                yticklabels=['NG-mask', 'OK-mask'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.tight_layout()
    plt.savefig(os.path.join(args.output_dir, 'confusion_matrix.png'))
    plt.close()

    # 分析错误
    ng_miss = cm[0][1]  # NG-mask 实际为 NG，但预测成 OK
    ok_false_alarm = cm[1][0]  # OK-mask 实际为 OK，但预测成 NG
    print(f"\n分析结果：\n← NG-mask 漏检 {ng_miss} 例")
    print(f"→ OK-mask 误杀 {ok_false_alarm} 例")
    print(f"\n错误样本保存在：{wrong_dir}")

# --------- 主函数入口 ---------
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_root',      type=str,   default='Face-Mask-Classification-Dataset')
    parser.add_argument('--img_size',       type=int,   default=224)
    parser.add_argument('--batch_size',     type=int,   default=32)
    parser.add_argument('--epochs',         type=int,   default=10)
    parser.add_argument('--lr',             type=float, default=0.000150)
    parser.add_argument('--optimizer',      type=str,   default='Adam')  # 支持 Adam, SGD 等
    parser.add_argument('--weight_decay',   type=float, default=1e-4)
    parser.add_argument('--pretrained',     type=bool,  default=True)
    parser.add_argument('--checkpoint_path',type=str,   default='best_mask_model.pth')
    parser.add_argument('--output_dir',     type=str,   default='outputs')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    train_and_validate(args)
    test(args)