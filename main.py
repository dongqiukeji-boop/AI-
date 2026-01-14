import os, time, hmac, hashlib, base64, urllib.parse, requests

# 获取 Secrets
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
        # 使用 v1 正式版接口，这是目前兼容性最强的路径
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        
        headers = {'Content-Type': 'application/json'}
        data = {"contents": [{"parts": [{"text": "请以'AI日报'为开头，写一句今日AI技术的简短鼓励语。"}]}]}
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        res_json = response.json()
        
        # 成功解析内容
        if 'candidates' in res_json and res_json['candidates']:
            summary = res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            # 如果出错，抓取具体报错原因
            error_info = res_json.get('error', {}).get('message', '未知错误')
            summary = f"状态提示：{error_info}"

        # 推送到钉钉
        payload = {
            "msgtype": "markdown",
            "markdown": {"title": "AI日报", "text": f"# AI日报 \n\n {summary}"}
        }
        requests.post(get_signed_url(), json=payload)
        
    except Exception as e:
        print(f"执行出错: {e}")

if __name__ == "__main__":
    main()
