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
        # --- 核心：官方标准接口 ---
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        
        headers = {'Content-Type': 'application/json'}
        data = {"contents": [{"parts": [{"text": "请以'AI日报'为开头，总结一句话：今天AI技术发展非常迅猛。"}]}]}
        
        # 发送请求，增加超时保护
        response = requests.post(url, headers=headers, json=data, timeout=30)
        res_json = response.json()
        
        # 稳健的解析逻辑
        if 'candidates' in res_json and len(res_json['candidates']) > 0:
            summary = res_json['candidates'][0]['content']['parts'][0]['text']
        elif 'error' in res_json:
            summary = f"Google 接口反馈：{res_json['error'].get('message', '未知地区限制')}"
        else:
            summary = "AI 暂时没有返回有效内容，请检查 API Key 状态。"

        # 推送到钉钉
        payload = {
            "msgtype": "markdown",
            "markdown": {"title": "AI日报", "text": f"# AI日报 \n\n {summary} \n\n > 推送时间：{time.strftime('%H:%M:%S')}"}
        }
        requests.post(get_signed_url(), json=payload)
        print("任务完成，请查看钉钉消息")
        
    except Exception as e:
        print(f"程序运行出错: {e}")

if __name__ == "__main__":
    main()
