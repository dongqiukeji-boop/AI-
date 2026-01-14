import os
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import google.generativeai as genai

# --- 1. 自动对接 GitHub 保险箱 (Secrets) ---
# 这里的变量名必须与你的 main.yml 中的 env 部分保持一致
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
DING_SECRET = os.getenv('DING_SECRET')

# --- 2. 钉钉安全验证逻辑 (必填，否则会被钉钉拦截) ---
def get_signed_url():
    timestamp = str(round(time.time() * 1000))
    secret_enc = DING_SECRET.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, DING_SECRET)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote(base64.b64encode(hmac_code))
    return f"{WEBHOOK_URL}&timestamp={timestamp}&sign={sign}"

# --- 3. 配置 Gemini AI ---
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

def main():
    try:
        # --- 这里替换为你原本的新闻爬取代码逻辑 ---
        # 示例：假设这是你抓取到的新闻
        news_content = "今日 AI 行业重大更新：Gemini 模型能力大幅提升..." 
        
        # 调用 AI 进行总结
        response = model.generate_content(f"请简要总结以下新闻：{news_content}")
        summary = response.text
        
        # --- 4. 发送到钉钉 ---
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": "AI 每日新闻总结",
                "text": f"### 🤖 每日 AI 新闻总结 \n\n {summary} \n\n > 推送时间：{time.strftime('%Y-%m-%d %H:%M:%S')}"
            }
        }
        res = requests.post(get_signed_url(), json=payload)
        print(f"发送状态: {res.text}")
        
    except Exception as e:
        print(f"程序运行出错: {e}")

if __name__ == "__main__":
    main()
