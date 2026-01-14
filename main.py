import os, time, hmac, hashlib, base64, urllib.parse, requests

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
        # 使用 beta 版本的 API 路径，并加上中转域名（此处以常见公益代理为例，若你有自己的代理可替换）
        gemini_url = f"https://proxy.onesrc.cc/google/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        
        headers = {'Content-Type': 'application/json'}
        data = {"contents": [{"parts": [{"text": "请以'AI日报'为开头，总结一句话：今天AI技术发展非常迅猛。"}]}]}
        
        response = requests.post(gemini_url, headers=headers, json=data, timeout=30)
        res_json = response.json()
        
        if 'candidates' in res_json:
            summary = res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            summary = f"AI 获取失败，原因：{res_json.get('error', {}).get('message', '未知地区限制')}"

        payload = {
            "msgtype": "markdown",
            "markdown": {"title": "AI日报", "text": f"# AI日报 \n\n {summary} \n\n > 推送时间：{time.strftime('%H:%M:%S')}"}
        }
        requests.post(get_signed_url(), json=payload)
        print("任务完成")
        
    except Exception as e:
        print(f"程序终极报错: {e}")

if __name__ == "__main__":
    main()
