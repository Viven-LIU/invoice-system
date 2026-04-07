from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
import requests
from datetime import datetime
from werkzeug.utils import secure_filename
import openpyxl

app = Flask(__name__)
CORS(app)

# 配置
UPLOAD_FOLDER = 'images'
EXCEL_FILE = 'invoices.xlsx'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 智谱 AI API 配置
ZHIPU_API_KEY = "9ef184d1f91a45998113b2ca783f46e5.J17zin65bOIpLi5g"
ZHIPU_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ocr_with_zhipu(image_path):
    """使用智谱 AI glm-4.6v-flash 识别发票"""
    with open(image_path, 'rb') as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')

    headers = {
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "glm-4.6v-flash",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                    },
                    {
                        "type": "text",
                        "text": """你是一个发票信息提取助手。请从这张发票图片中提取以下信息，返回 JSON 格式：
{
    "date": "开票日期",
    "invoice_no": "发票号码",
    "seller": "销售方名称",
    "buyer": "购买方名称",
    "item": "项目名称",
    "total": "价税合计金额"
}
请只返回 JSON，不要有其他内容。"""
                    }
                ]
            }
        ],
        "thinking": {"type": "enabled"},
        "max_tokens": 500
    }

    try:
        response = requests.post(ZHIPU_API_URL, headers=headers, json=payload, timeout=60)
        result = response.json()

        if result.get("choices"):
            content = result["choices"][0]["message"].get("content", "")
            import json
            try:
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0].strip()
                else:
                    json_str = content.strip()
                return json.loads(json_str)
            except:
                return {"raw": content}
    except Exception as e:
        return {"error": str(e)}

    return None

def save_to_excel(info, image_path):
    """保存发票信息到 Excel"""
    headers = ['发票号码', '开票日期', '购买方', '销售方', '项目名称', '价税合计', '图片路径']
    row = [
        info.get('invoice_no', ''),
        info.get('date', ''),
        info.get('buyer', ''),
        info.get('seller', ''),
        info.get('item', ''),
        info.get('total', ''),
        image_path
    ]

    # 获取项目根目录的绝对路径
    project_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(project_dir, EXCEL_FILE)

    # 如果文件不存在，创建并写入表头
    if not os.path.exists(excel_path):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "发票记录"
        ws.append(headers)
        wb.save(excel_path)

    # 打开现有文件追加数据
    wb = openpyxl.load_workbook(excel_path)
    ws = wb.active
    ws.append(row)
    wb.save(excel_path)

    return excel_path

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有文件'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'})

    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{timestamp}.{ext}'

        # 获取项目根目录的绝对路径
        project_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(project_dir, UPLOAD_FOLDER, filename)

        file.save(filepath)

        # OCR 识别
        info = ocr_with_zhipu(filepath)
        if info and not info.get("error"):
            # 保存到 Excel
            excel_path = save_to_excel(info, filepath)

            return jsonify({
                'success': True,
                'message': '上传成功',
                'filename': filename,
                'info': info,
                'excel': excel_path
            })
        else:
            return jsonify({
                'success': True,
                'message': '上传成功，但识别失败',
                'filename': filename,
                'info': info
            })

    return jsonify({'success': False, 'message': '不支持的文件类型'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
