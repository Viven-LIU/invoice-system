import requests
import json
import sys
import base64

MINIMAX_API_KEY = ""
MINIMAX_API_URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"

# 用之前成功的 stock chart URL
STOCK_CHART_URL = "https://pic.5tu.cn/uploads/allimg/2408/pic_5tu_big_6672913_66ab56cc1c241-thumb-650.jpg"

def test_stock_chart_invoice():
    """用 stock chart URL 测试发票提取"""
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }

    content = f"""![image]({STOCK_CHART_URL})

你是一个发票信息提取助手。请从这张发票图片中提取以下信息，返回 JSON 格式：
{{
    "date": "开票日期",
    "seller": "销售方名称",
    "buyer": "购买方名称",
    "item": "项目名称",
    "total": "价税合计金额"
}}
请只返回 JSON。"""

    payload = {
        "model": "MiniMax-M2.7",
        "messages": [{"role": "user", "content": content}],
        "max_tokens": 500
    }

    response = requests.post(MINIMAX_API_URL, headers=headers, json=payload)
    return response.json()

if __name__ == "__main__":
    result = test_stock_chart_invoice()

    if result.get("choices"):
        content = result["choices"][0]["message"].get("content", "")
        print(f"content length: {len(content)}")
        print(f"\n=== 回复 ===\n{content}")
    else:
        print(f"Error: {result.get('base_resp', {}).get('status_msg', 'unknown')}")
