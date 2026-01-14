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
        # 使用 v1beta 中转路径
        url = f"https://api.geren.ai/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        
        headers = {'Content-Type': 'application/json'}
        data = {"contents": [{"parts": [{"text": "请以'AI日报'为开头，总结一句话：今日AI技术有了长足进步。"}]}]}
        
        # 发送请求
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        # 检查是否请求成功
        if response.status_code != 200:
            summary = f"接口连接失败，状态码：{response.status_code}"
        else:
            res_json = response.json()
            if 'candidates' in res_json:
                summary = res_json['candidates'][0]['content']['parts'][0]['text']
            else:
                summary = f"AI 获取失败，原因：{res_json.get('error', {}).get('message', '未知错误')}"

        # 发送到钉钉
        payload = {
            "msgtype": "markdown",
            "markdown": {"title": "AI日报", "text": f"# AI日报 \n\n {summary} \n\n > 推送时间：{time.strftime('%H:%M:%S')}"}
        }
        requests.post(get_signed_url(), json=payload)
        print("任务完成")
        
    except Exception as e:
        print(f"程序运行出错: {e}")

if __name__ == "__main__":
    main()
