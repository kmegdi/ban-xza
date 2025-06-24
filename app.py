from flask import Flask, request, Response
import requests
import json

app = Flask(__name__)

VALID_API_KEYS = {
    "XZA": "active"
}

def validate_api_key(api_key):
    if not api_key:
        return {"error": "API key is missing", "status_code": 401}
    if api_key not in VALID_API_KEYS:
        return {"error": "Invalid API key", "status_code": 401}
    
    status = VALID_API_KEYS[api_key]
    if status == "inactive":
        return {"error": "API key is changed", "status_code": 403}
    if status == "banned":
        return {"error": "API key is banned", "status_code": 403}
    
    return {"valid": True}

# ✅ جلب اسم اللاعب والمنطقة
def get_player_info(player_id):
    url = "https://shop2game.com/api/auth/player_id_login"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://shop2game.com",
        "Referer": "https://shop2game.com/app",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    payload = {
        "app_id": 100067,
        "login_id": f"{player_id}",
        "app_server_id": 0,
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            nickname = data.get('nickname', 'غير متوفر')
            region = data.get('region', 'غير متوفر')
            return nickname, region
        else:
            return "غير معروف", "غير معروف"
    except:
        return "غير معروف", "غير معروف"

# ✅ دمج فحص الحظر + جلب الاسم والمنطقة
@app.route("/bancheck", methods=["GET"])
def bancheck():
    api_key = request.args.get("key", "")
    player_id = request.args.get("uid", "")

    key_validation = validate_api_key(api_key)
    if "error" in key_validation:
        return Response(json.dumps(key_validation), mimetype="application/json")

    if not player_id:
        return Response(json.dumps({"error": "Player ID is required", "status_code": 400}), mimetype="application/json")

    # فحص الحظر
    try:
        ban_url = f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={player_id}"
        ban_headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
            "Accept": "application/json",
            "referer": "https://ff.garena.com/en/support/",
            "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"
        }

        response = requests.get(ban_url, headers=ban_headers)
        if response.status_code != 200:
            return Response(json.dumps({"error": "Failed to fetch ban data", "status_code": 500}), mimetype="application/json")

        ban_data = response.json().get("data", {})
        is_banned = ban_data.get("is_banned", 0)
        period = ban_data.get("period", 0)
    except Exception as e:
        return Response(json.dumps({"error": str(e), "status_code": 500}), mimetype="application/json")

    # جلب اسم اللاعب والمنطقة
    nickname, region = get_player_info(player_id)

    result = {
        "uid": player_id,
        "nickname": nickname,
        "region": region,
        "status": "BANNED" if is_banned else "NOT BANNED",
        "ban_period": period if is_banned else 0,
        "is_banned": bool(is_banned),
        "credits": "@XZA-NJA"
    }

    return Response(json.dumps(result, ensure_ascii=False), mimetype="application/json")

# ✅ فحص مفتاح الـ API
@app.route("/check_key", methods=["GET"])
def check_key():
    api_key = request.args.get("key", "")
    key_validation = validate_api_key(api_key)

    if "error" in key_validation:
        return Response(json.dumps(key_validation), mimetype="application/json")

    return Response(json.dumps({"status": "valid", "key_status": VALID_API_KEYS.get(api_key, "unknown")}), mimetype="application/json")

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)