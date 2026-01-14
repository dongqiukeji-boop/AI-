import os
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import google.generativeai as genai

# --- 1. 获取 Secret ---
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
DING_SECRET = os.getenv('DING_SECRET')

# --- 2. 钉钉加签 ---
def get_signed_url():
    timestamp = str(round(time.time() * 1000))
    secret_enc = DING_SECRET.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, DING_SECRET)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote(base64.b64encode(hmac_code))
    return f"{WEBHOOK_URL}&timestamp={timestamp}&sign={sign}"

# --- 3. 配置 Gemini (修正模型名称) ---
genai.configure(api_key=GEMINI_KEY)
# 使用最新的 1.5-flash 模型，避免 404 错误
model = genai.GenerativeModel('gemini-1.5-flash')

def main():
    try:
        # 模拟抓取的新闻内容
        news_content = "今日全球AI技术取得突破性进展，多模态模型能力进一步提升..." 
        
        # 调用 AI 总结
        response = model.generate_content(f"请简要总结以下新闻：{news_content}")
        summary = response.text
        
        # --- 4. 发送到钉钉 (添加关键词：AI日报) ---
        payload = {
            "msgtype": "markdown",
            "markdown": {
                # 标题和内容都加上关键词，确保钉钉安全验证通过
                "title": "AI日报-新闻总结", 
                "text": f"# AI日报 \n\n {summary} \n\n > 推送时间：{time.strftime('%Y-%m-%d %H:%M:%S')}"
            }
        }
        
        res = requests.post(get_signed_url(), json=payload)
        print(f"钉钉返回结果: {res.text}")
        
    except Exception as e:
        print(f"程序运行出错: {e}")

if __name__ == "__main__":
    main()
