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
        # 使用最高兼容性的 gemini-pro 接口
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"
        
        headers = {'Content-Type': 'application/json'}
        data = {"contents": [{"parts": [{"text": "请以'AI日报'为开头，写一句激励人心的话，证明你已经连接成功了。"}]}]}
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        res_json = response.json()
        
        # 解析返回内容
        if 'candidates' in res_json and len(res_json['candidates']) > 0:
            summary = res_json['candidates'][0]['content']['parts'][0]['text']
        elif 'error' in res_json:
            summary = f"Google 错误反馈：{res_json['error'].get('message', '未知模型权限问题')}"
        else:
            summary = "AI 返回了空数据，请尝试重新生成 API Key。"

        # 推送到钉钉
        payload = {
            "msgtype": "markdown",
            "markdown": {"title": "AI日报", "text": f"# AI日报 \n\n {summary} \n\n > 推送时间：{time.strftime('%H:%M:%S')}"}
        }
        requests.post(get_signed_url(), json=payload)
        
    except Exception as e:
        print(f"运行出错: {e}")

if __name__ == "__main__":
    main()
