import base64
import requests
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

image_path = 'images/test.jpg'

with open(image_path, 'rb') as f:
    img_base64 = base64.b64encode(f.read()).decode()

url = 'https://api.ocr.space/parse/image'
payload = {'base64Image': f'data:image/jpeg;base64,{img_base64}', 'language': 'chs'}
headers = {'apikey': 'helloworld'}

response = requests.post(url, data=payload, headers=headers)
result = response.json()

if result.get('ParsedResults'):
    text = result['ParsedResults'][0]['ParsedText']
    print("=== 识别原始文本 ===")
    print(text)
    print("\n=== 提取关键信息 ===")

    # 开票日期
    date_match = re.search(r'开票日期[：:]\s*(\d{4}年\d{2}月\d{2}日)', text)
    date = date_match.group(1) if date_match else '未识别'

    # 名称（销售方）
    name_match = re.search(r'名称[：:]\s*(.+)', text)
    name = name_match.group(1).strip() if name_match else '未识别'

    # 项目名称
    item_match = re.search(r'机动车[*×x](.+)', text)
    item = item_match.group(1).strip() if item_match else '未识别'

    # 价税合计
    total_match = re.search(r'[（(]小写[）)]\s*[Y¥￥]?\s*([\d,.]+)', text)
    total = total_match.group(1) if total_match else '未识别'

    print(f"开票日期: {date}")
    print(f"销售方: {name}")
    print(f"项目名称: {item}")
    print(f"价税合计: {total}")
else:
    print("识别失败:", result)
