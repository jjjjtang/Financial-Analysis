from flask import Flask, request, jsonify
from flask_cors import CORS
import deepseek
import hiThink
from entity import User
from mapper import userMapper
from mapper import annualReportMapper
import re

app = Flask(__name__)
CORS(app)

# 查询所有用户接口
@app.route('/api/users', methods=['GET'])
def get_all_users():
    result = userMapper.selectAllUser()
    return jsonify(result),200

# 注册用户接口
# {
#   "user_id": 1,
#   "username": "testuser",
#   "password": "testpass"
# }
@app.route('/api/users/register', methods=['POST'])
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

# 用户登录接口
# {
#   "username": "testuser",
#   "password": "testpass"
# }
@app.route('/api/users/login', methods=['POST'])
def user_login():
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': '缺少字段'}), 400

        username = data['username']
        password = data['password']

        users = userMapper.selectAllUser()
        for user in users:
            if user['username'] == username and user['password'] == password:
                return jsonify({'message': '登录成功'}), 200

        return jsonify({'error': '用户名或密码错误'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 获取所有年报接口
@app.route('/api/annualReports/getAll', methods=['GET'])
def get_all_annual_reports():
    result = annualReportMapper.selectAllAnnualReport()
    return jsonify(result),200

# 根据公司代码和年份获取年报接口
# 例: /api/annualReports/getByCompanyCodeAndYear?company_code=000001&year=2021
@app.route('/api/annualReports/getByCompanyCodeAndYear', methods=['GET'])
def get_annual_report_by_company_code_and_year():
    company_code = request.args.get('company_code')
    year = request.args.get('year')

    if not company_code or not year:
        return jsonify({'error': '缺少公司代码或年份参数'}), 400

    result = annualReportMapper.selectAnnualReportByCompanyCodeAndYearOrId(company_code=company_code, year=year)
    if result:
        return jsonify(result), 200
    else:
        return jsonify({'error': '未找到对应的年报'}), 404

# 根据ID获取年报接口
# 例: /api/annualReports/getById?id=1
@app.route('/api/annualReports/getById', methods=['GET'])
def get_annual_report_by_id():
    id = request.args.get('id')

    if not id:
        return jsonify({'error': '缺少ID参数'}), 400

    try:
        id = int(id)
    except ValueError:
        return jsonify({'error': 'ID必须是整数'}), 400

    result = annualReportMapper.selectAnnualReportByCompanyCodeAndYearOrId(id=id)
    if result:
        return jsonify(result), 200
    else:
        return jsonify({'error': '未找到对应的年报'}), 404

# deepseek分析PDF接口
# {
#   "file_path": "annualReportTools/annualFiles/2021/pdf_Format/000001_平安银行_2021.pdf"
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


# deepseek聊天接口
# {
#   "file_path": "annualReportTools/annualFiles/2021/pdf_Format/000001_平安银行_2021.pdf",
#   "message": "帮我总结一下这份年报的内容"
# }
@app.route('/api/deepseek/chat', methods=['POST'])
def deepseekChat():
    print("请求收到")
    print("Headers:", request.headers)
    print("Body:", request.get_data())
    try:
        data = request.get_json()
        if not data or 'file_path' not in data or 'message' not in data:
            return jsonify({'error': '缺少字段'}), 400

        file_path = data['file_path']
        message = data['message']
        result = deepseek.chat(message, file_path)
        return jsonify({'reply': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 要点总结接口
# {
#   "file_path": "annualReportTools/annualFiles/2021/pdf_Format/000001_平安银行_2021.pdf"
# }
@app.route('/api/deepseek/synopsis', methods=['POST'])
def deepseekSynopsis():
    print("请求收到")
    print("Headers:", request.headers)
    print("Body:", request.get_data())
    try:
        data = request.get_json()
        if not data or 'file_path' not in data:
            return jsonify({'error': '缺少文件路径'}), 400

        file_path = data['file_path']
        raw_result = deepseek.fileSynopsis(file_path)

        # 正则解析
        points = {}
        for match in re.finditer(r"(要点\d+)\s*[:：]\s*(.*?)(?=(要点\d+[:：]|$))", raw_result, re.S):
            key = match.group(1).strip()
            value = match.group(2).strip().replace("\n", " ")
            points[key] = value

        return jsonify(points), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Hithink分析PDF接口
# {
#   "file_path": "annualReportTools/annualFiles/2021/pdf_Format/000001_平安银行_2021.pdf"
# }
@app.route('/api/hithink/analysis', methods=['POST'])
def hithinkAnalysis():
    print("请求收到")
    print("Headers:", request.headers)
    print("Body:", request.get_data())
    try:
        data = request.get_json()
        if not data or 'file_path' not in data:
            return jsonify({'error': '缺少文件路径'}), 400

        file_path = data['file_path']
        result = hiThink.pdfAnalysis(file_path)
        return jsonify({'reply': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Hithink财务助手接口
# {
#   "file_path": "annualReportTools/annualFiles/2021/pdf_Format/000001_平安银行_2021.pdf",
#   "question": "这是哪一年的年报"
# }
@app.route('/api/hithink/financialAssistant', methods=['POST'])
def hithinkFinancialAssistant():
    print("请求收到")
    print("Headers:", request.headers)
    print("Body:", request.get_data())
    try:
        data = request.get_json()
        if not data or 'file_path' not in data or 'question' not in data:
            return jsonify({'error': '缺少字段'}), 400

        file_path = data['file_path']
        question = data['question']
        result = hiThink.fincialAssistant(file_path, question)
        return jsonify({'reply': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def run():
    print("Flask App is running")
    app.run(debug=True)
