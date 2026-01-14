import os
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests

# --- 1. 获取 GitHub Secrets ---
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
DING_SECRET = os.getenv('DING_SECRET')

# --- 2. 钉钉安全验证逻辑 ---
def get_signed_url():
    timestamp = str(round(time.time() * 1000))
    secret_enc = DING_SECRET.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, DING_SECRET)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote(base64.b64encode(hmac_code))
    return f"{WEBHOOK_URL}&timestamp={timestamp}&sign={sign}"

def main():
    try:
        # --- 3. 使用最简单的 API 方式调用 Gemini ---
        # 这种方式不依赖特定的 API 版本，兼容性最强
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        
        headers = {'Content-Type': 'application/json'}
        prompt = "你是一个专业的新闻助手。请以'AI日报'为标题，用一句话总结：今日AI领域技术更新飞速，多模态应用正在改变各行各业。"
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        # 调用 AI
        response = requests.post(gemini_url, headers=headers, json=data)
        res_json = response.json()
        
        # 解析 AI 返回的内容
        if 'candidates' in res_json:
            summary = res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            summary = "AI 暂时开小差了，请检查 API Key 权限。"
            print(f"AI 错误详情: {res_json}")

        # --- 4. 发送到钉钉 (包含关键词：AI日报) ---
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": "AI日报", 
                "text": f"# AI日报 \n\n {summary} \n\n > 推送时间：{time.strftime('%H:%M:%S')}"
            }
        }
        
        res = requests.post(get_signed_url(), json=payload)
        print(f"钉钉推送结果: {res.text}")
        
    except Exception as e:
        print(f"程序终极报错: {e}")

if __name__ == "__main__":
    main()
