import os, time, hmac, hashlib, base64, urllib.parse, requests

# 1. 获取 Secrets
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
DING_SECRET = os.getenv('DING_SECRET')

def get_signed_url():
    timestamp = str(round(time.time() * 1000))
    secret_enc = DING_SECRET.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, DING_SECRET)
    hmac_code = hmac.new(secret_enc, string_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote(base64.b64encode(hmac_code))
    return f"{WEBHOOK_URL}&timestamp={timestamp}&sign={sign}"

def main():
    try:
        # 使用 Google 官方目前最通用的 v1 路径
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_KEY}"
        
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{"text": "请以'AI日报'为开头，总结一句话：今日AI技术有突破性进展。"}]
            }]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        res_json = response.json()
        
        # 精准匹配 Google API 返回的结构
        if 'candidates' in res_json and res_json['candidates']:
            summary = res_json['candidates'][0]['content']['parts'][0]['text']
        elif 'error' in res_json:
            summary = f"Google 官方报错：{res_json['error'].get('message', '未知错误')}"
        else:
            summary = f"接口返回异常，详细信息：{str(res_json)[:100]}"

        # 推送到钉钉
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": "AI日报", 
                "text": f"# AI日报 \n\n {summary} \n\n > 推送时间：{time.strftime('%H:%M:%S')}"
            }
        }
        requests.post(get_signed_url(), json=payload)
        
    except Exception as e:
        print(f"执行出错: {e}")

if __name__ == "__main__":
    main()
