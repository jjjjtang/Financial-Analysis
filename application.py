from flask import Flask, request, jsonify

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



def run():
    print("Flask App is running")
    app.run(debug=True)
