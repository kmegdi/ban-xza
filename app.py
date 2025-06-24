from flask import Flask, request, jsonify
import requests
from functools import wraps

app = Flask(__name__)

API_KEYS = {
    "XZA": "active"
}

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.args.get('key')
        if not api_key:
            return jsonify({"error": "API key is missing"}), 401
        if api_key not in API_KEYS:
            return jsonify({"error": "Invalid API key"}), 401
        if API_KEYS[api_key] != "active":
            return jsonify({"error": "API key is inactive"}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/checkbanned', methods=['GET'])
@require_api_key
def check_banned():
    try:
        player_id = request.args.get('id')
        if not player_id:
            return jsonify({"error": "Player ID is required"}), 400

        url = f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={player_id}"
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            'Accept': "application/json, text/plain, */*",
            'authority': "ff.garena.com",
            'accept-language': "en-GB,en-US;q=0.9,en;q=0.8",
            'referer': "https://ff.garena.com/en/support/",
            'sec-ch-ua': "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\"",
            'sec-ch-ua-mobile': "?1",
            'sec-ch-ua-platform': "\"Android\"",
            'sec-fetch-dest': "empty",
            'sec-fetch-mode': "cors",
            'sec-fetch-site': "same-origin",
            'x-requested-with': "B6FksShzIgjfrYImLpTsadjS86sddhFH",
            'Cookie': "_ga_8RFDT0P8N9=GS1.1.1706295767.2.0.1706295767.0.0.0; apple_state_key=8236785ac31b11ee960a621594e13693; datadome=bbC6XTzUAS0pXgvEs7u",
        }

        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            is_banned = result.get('data', {}).get('is_banned', 0)
            period = result.get('data', {}).get('period', 0)

            return jsonify({
                "player_id": player_id,
                "is_banned": bool(is_banned),
                "ban_period": period if is_banned else 0,
                "status": "BANNED" if is_banned else "NOT BANNED"
            })
        else:
            return jsonify({"error": "Failed to fetch data from server"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/check_key', methods=['GET'])
def check_key():
    api_key = request.args.get('key')
    if not api_key:
        return jsonify({"error": "API key is missing"}), 401
    if api_key in API_KEYS:
        return jsonify({
            "status": "valid",
            "key_status": API_KEYS[api_key]
        })
    return jsonify({"status": "invalid"}), 401

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)