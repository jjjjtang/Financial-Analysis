from flask import Flask, request, jsonify
import deepseek
from entity import User
from mapper import userMapper

app = Flask(__name__)

# 查询所有用户接口
@app.route('/api/users', methods=['GET'])
def get_all_users():
    result = userMapper.selectAllUser()
    return jsonify(result),200

# 注册用户接口
@app.route('/api/register', methods=['POST'])
def insert_user():
    try:
        data = request.get_json()
        if not data or 'user_id' not in data or 'username' not in data or 'password' not in data:
            return jsonify({'error': '缺少字段'}), 400

        user = User(
            user_id=int(data['user_id']),
            username=data['username'],
            password=data['password']
        )

        result = userMapper.insertUser(user)
        if result == "success":
            return jsonify({'message': '✅ 用户插入成功'}), 201
        else:
            return jsonify({'error': '插入失败'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# deepseek分析PDF接口
# {
#   "file_path": "/Users/fantant/Desktop/TASK.pdf"
# }
@app.route('/api/deepseek/analysis', methods=['POST'])
def deepseekAnalysis():
    print("请求收到")
    print("Headers:", request.headers)
    print("Body:", request.get_data())
    try:
        data = request.get_json()
        if not data or 'file_path' not in data:
            return jsonify({'error': '缺少文件路径'}), 400

        file_path = data['file_path']
        result = deepseek.pdfAnalysis(file_path)
        return jsonify({'reply': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500



def run():
    print("Flask App is running")
    app.run(debug=True)
