import os, time, hmac, hashlib, base64, urllib.parse, requests

# --- 1. 获取 Secrets ---
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
DING_SECRET = os.getenv('DING_SECRET')

# --- 2. 钉钉加签逻辑 ---
def get_signed_url():
    timestamp = str(round(time.time() * 1000))
    secret_enc = DING_SECRET.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, DING_SECRET)
    hmac_code = hmac.new(secret_enc, string_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote(base64.b64encode(hmac_code))
    return f"{WEBHOOK_URL}&timestamp={timestamp}&sign={sign}"

def main():
    try:
        # --- 3. 官方接口 (使用最稳定的 v1beta 路径) ---
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        
        headers = {'Content-Type': 'application/json'}
        # 简化 Prompt，确保能快速返回
        data = {
            "contents": [{
                "parts": [{"text": "请以'AI日报'为开头，总结一句话：今日AI技术有新的进展。"}]
            }]
        }
        
        # 增加重试机制和更长的超时时间
        response = requests.post(url, headers=headers, json=data, timeout=60)
        res_json = response.json()
        
        # 精准解析内容
        if 'candidates' in res_json and len(res_json['candidates']) > 0:
            summary = res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            # 如果失败，直接在钉钉里显示完整的错误信息，方便我们调试
            error_msg = res_json.get('error', {}).get('message', '未知接口错误')
            summary = f"AI 获取失败，请检查 API Key。错误详情：{error_msg}"
            print(f"Debug JSON: {res_json}")

        # --- 4. 推送到钉钉 ---
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": "AI日报", 
                "text": f"# AI日报 \n\n {summary} \n\n > 推送时间：{time.strftime('%H:%M:%S')}"
            }
        }
        res = requests.post(get_signed_url(), json=payload)
        print(f"钉钉推送状态: {res.text}")
        
    except Exception as e:
        print(f"程序终极报错: {e}")

if __name__ == "__main__":
    main()
