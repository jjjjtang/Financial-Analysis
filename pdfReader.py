import pdfplumber
import pytesseract
def extract_text_from_pdf(file_path, lang='chi_sim'):
    """
    改进版 PDF 文本提取函数：
    1. 遍历每一页
    2. 先用 pdfplumber 提取文字
    3. 如果文字为空，则用 OCR 补充
    """
    text = ""

    with pdfplumber.open(file_path) as pdf:
        print(f"PDF 总页数: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text and page_text.strip():
                text += page_text + "\n"
            else:
                # 没有文字就用 OCR
                pil_img = page.to_image(resolution=300).original
                ocr_text = pytesseract.image_to_string(pil_img, lang=lang)
                text += ocr_text + "\n"

    print("PDF内容提取完成")
    return text