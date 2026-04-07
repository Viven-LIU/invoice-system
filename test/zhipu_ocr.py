import base64
import requests
import json
import sys

API_KEY = "9ef184d1f91a45998113b2ca783f46e5.J17zin65bOIpLi5g"
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

def ocr_with_zhipu(image_path: str) -> dict:
    """使用智谱 AI glm-4.6v-flash 识别发票"""

    with open(image_path, 'rb') as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')

    headers = {
        "Authorization": f"Bearer {API_KEY}",
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
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": """你是一个发票信息提取助手。请从这张发票图片中提取以下信息，返回 JSON 格式：
{
    "date": "开票日期",
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

    print(f"发送请求，base64长度: {len(img_base64)}...", file=sys.stderr)
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    result = ocr_with_zhipu("images/20260407_214126.jpg")

    if result.get("choices"):
        content = result["choices"][0]["message"].get("content", "")
        print(f"\n=== 识别结果 ===")
        print(content)
    else:
        print(f"\n=== 错误 ===")
        print(json.dumps(result, ensure_ascii=False, indent=2))
