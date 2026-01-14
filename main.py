import os
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import google.generativeai as genai

# --- 1. 获取 Secret (确保与 GitHub Secrets 一致) ---
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
DING_SECRET = os.getenv('DING_SECRET')

# --- 2. 钉钉加签函数 ---
def get_signed_url():
    timestamp = str(round(time.time() * 1000))
    secret_enc = DING_SECRET.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, DING_SECRET)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote(base64.b64encode(hmac_code))
    return f"{WEBHOOK_URL}&timestamp={timestamp}&sign={sign}"

# --- 3. 配置 Gemini (切换到最兼容的 1.0 模型) ---
genai.configure(api_key=GEMINI_KEY)
# 尝试使用兼容性最好的 gemini-1.0-pro
model = genai.GenerativeModel('gemini-1.0-pro')

def main():
    try:
        # 这里是你想要总结的内容
        news_content = "AI日报：今日科技头条，多模态大模型技术在医疗领域取得重大进展。" 
        
        # 调用 AI 总结
        response = model.generate_content(f"请简要总结以下新闻：{news_content}")
        summary = response.text
        
        # --- 4. 发送到钉钉 (包含关键词：AI日报) ---
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": "AI日报", 
                "text": f"# AI日报 \n\n {summary} \n\n > 推送时间：{time.strftime('%H:%M:%S')}"
            }
        }
        
        res = requests.post(get_signed_url(), json=payload)
        print(f"钉钉返回结果: {res.text}")
        
    except Exception as e:
        # 如果 1.0 报错，自动尝试 1.5-flash 的标准写法
        print(f"尝试 1.0 出错，正在切换 1.5... 错误详情: {e}")
        try:
            model_flash = genai.GenerativeModel('models/gemini-1.5-flash')
            response = model_flash.generate_content(f"总结：{news_content}")
            # ... 发送逻辑同上 ...
            res = requests.post(get_signed_url(), json={"msgtype": "markdown", "markdown": {"title": "AI日报", "text": f"# AI日报\n\n{response.text}"}})
            print(f"切换 1.5 后结果: {res.text}")
        except Exception as e2:
            print(f"终极失败: {e2}")

if __name__ == "__main__":
    main()
