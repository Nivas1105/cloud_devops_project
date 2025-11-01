import logging
from flask import Flask, redirect, url_for, session, jsonify, request
from authlib.integrations.flask_client import OAuth
from flask_cors import CORS
import os

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY")

CORS(app, supports_credentials=True, origins=["http://localhost:8080"])
COGNITO_DOMAIN = ""
COGNITO_USERPOOL_ID = ""
COGNITO_CLIENT_ID = ""
COGNITO_CLIENT_SECRET = ""  
COGNITO_REDIRECT_URI = "http://localhost:5050/callback"
COGNITO_LOGOUT_REDIRECT = "http://localhost:8080/"
COGNITO_SCOPES = "openid email phone" 

oauth = OAuth(app)
oauth.register(
    name="cognito",
    client_id=COGNITO_CLIENT_ID,
    client_secret=COGNITO_CLIENT_SECRET,
    server_metadata_url=f"https://cognito-idp.us-east-1.amazonaws.com/{COGNITO_USERPOOL_ID}/.well-known/openid-configuration",
    client_kwargs={"scope": COGNITO_SCOPES},
)
@app.route("/login")
def login():
    return oauth.cognito.authorize_redirect(COGNITO_REDIRECT_URI)

@app.route("/callback")
def callback():
    try:
        token = oauth.cognito.authorize_access_token()
    except Exception as e:
        app.logger.exception("Error exchanging code for token")
        return f"Token exchange failed: {e}", 400

    access_token = token.get("access_token")
    id_token = token.get("id_token")
    session["access_token"] = access_token
    session["id_token"] = id_token

    try:
        resp = oauth.cognito.get("userinfo", token=access_token)
        userinfo = resp.json()
        session["user"] = userinfo
        app.logger.info("Logged in user: %s", userinfo.get("email"))
    except Exception as e:
        app.logger.exception("Failed to fetch userinfo")
        session["user"] = {}

    return redirect("http://localhost:8080/index.html")


@app.route("/userinfo")
def userinfo():
    if "access_token" not in session:
        return jsonify({"error": "unauthorized"}), 401
    return jsonify(session.get("user", {}))


@app.route("/logout")
def logout():
    session.clear()
    logout_url = (
        f"{COGNITO_DOMAIN}/logout"
        f"?client_id={COGNITO_CLIENT_ID}"
        f"&logout_uri={COGNITO_LOGOUT_REDIRECT}"
    )
    return redirect(logout_url)


@app.route("/forecast")
def forecast_proxy():
    import requests
    API_GATEWAY_URL = ""
    try:
        r = requests.get(API_GATEWAY_URL, timeout=10)
        r.raise_for_status()
        return jsonify(r.json())
    except Exception as e:
        app.logger.exception("Forecast proxy failed")
        return jsonify({"error": "failed to fetch forecast", "detail": str(e)}), 502


@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.config.update(
        SESSION_COOKIE_SAMESITE="None",  
        SESSION_COOKIE_SECURE=False  
    )
    app.run(host="0.0.0.0", port=5050, debug=True)
