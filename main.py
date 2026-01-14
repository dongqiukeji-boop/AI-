import os, time, hmac, hashlib, base64, urllib.parse, requests

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DING_SECRET = os.getenv("DING_SECRET")

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-001")  # ✅ 稳定版
API_VERSION = os.getenv("GEMINI_API_VERSION", "v1beta")

def must_env(name: str, val: str | None):
    if not val:
        raise RuntimeError(f"缺少环境变量：{name}（GitHub Secrets/Variables 没注入成功）")

def get_signed_url():
    timestamp = str(round(time.time() * 1000))
    secret_enc = DING_SECRET.encode("utf-8")
    string_to_sign = f"{timestamp}\n{DING_SECRET}"
    hmac_code = hmac.new(secret_enc, string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote(base64.b64encode(hmac_code))
    return f"{WEBHOOK_URL}&timestamp={timestamp}&sign={sign}"

def list_models():
    url = f"https://generativelanguage.googleapis.com/{API_VERSION}/models?key={GEMINI_KEY}"
    r = requests.get(url, timeout=30)
    return r.status_code, r.text[:1200]  # 截断，避免日志太长

def generate_daily():
    url = f"https://generativelanguage.googleapis.com/{API_VERSION}/models/{MODEL}:generateContent?key={GEMINI_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {"parts": [{"text": "AI日报：用中文写一句今天AI领域值得关注的新变化，尽量口语化，不要太长。"}]}
        ]
    }
    r = requests.post(url, headers=headers, json=data, timeout=30)
    try:
        j = r.json()
    except Exception:
        return f"Google 返回非 JSON：HTTP {r.status_code}\n{r.text[:800]}"

    if "candidates" in j:
        return j["candidates"][0]["content"]["parts"][0]["text"]
    if "error" in j:
        return f"Google 错误反馈：{j['error'].get('message', '未知错误')}（HTTP {r.status_code}）"
    return f"Google 返回结构异常：HTTP {r.status_code}\n{str(j)[:800]}"

def push_to_ding(summary: str):
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": "AI日报",
            "text": f"# AI日报\n\n{summary}\n\n> 推送时间：{time.strftime('%H:%M:%S')}"
        }
    }
    requests.post(get_signed_url(), json=payload, timeout=30)

def main():
    must_env("GEMINI_API_KEY", GEMINI_KEY)
    must_env("WEBHOOK_URL", WEBHOOK_URL)
    must_env("DING_SECRET", DING_SECRET)

    # ✅ 可选：先验一下 Key 是否能列出模型（强烈建议你先开着跑一次）
    code, head = list_models()
    if code != 200:
        push_to_ding(f"ListModels 失败：HTTP {code}\n{head}")
        return

    summary = generate_daily()
    push_to_ding(summary)

if __name__ == "__main__":
    main()
