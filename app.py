from flask import Flask, request, jsonify, render_template
from flask_httpauth import HTTPBasicAuth
import urllib.request
import json
import os

app = Flask(__name__)
auth = HTTPBasicAuth()

# --- Config ---
OPTIPLEX_URL = os.environ.get("OPTIPLEX_URL", "https://195b-2601-98d-c082-7e60-c57e-3275-1f8-b562.ngrok-free.app")
API_KEY      = os.environ.get("KENBOT_API_KEY", "KENNY2012may30!")

USERS = {
   "kenbot": "KENBOT6501"
}

@auth.verify_password
def verify_password(username, password):
   if username in USERS and USERS[username] == password:
       return username
   return None

# --- Helper: forward request to Optiplex ---
def forward(path, method="GET", body=None):
   url = OPTIPLEX_URL + path
   headers = {
       "Content-Type": "application/json",
       "X-API-Key": API_KEY
   }
   print(f"Forwarding {method} to {url}")
   try:
       if method == "POST":
           data = json.dumps(body).encode("utf-8")
           req = urllib.request.Request(url, data=data, headers=headers, method="POST")
       else:
           req = urllib.request.Request(url, headers=headers, method="GET")

       with urllib.request.urlopen(req, timeout=120) as resp:
           result = json.loads(resp.read().decode("utf-8"))
           print(f"Got response: {result}")
           return result, resp.status
   except Exception as e:
       print(f"Forward error: {e}")
       return {"error": str(e)}, 500


# --- Routes ---

@app.route("/")
@auth.login_required
def index():
   return render_template("index.html")


@app.route("/chat", methods=["POST"])
@auth.login_required
def chat():
   data = request.get_json(force=True)
   result, status = forward("/chat", method="POST", body=data)
   return jsonify(result), status


@app.route("/reset", methods=["GET"])
@auth.login_required
def reset():
   result, status = forward("/reset")
   return jsonify(result), status


@app.route("/ping", methods=["GET"])
def ping():
   result, status = forward("/ping")
   return jsonify(result), status


@app.route("/version", methods=["GET"])
def version():
   result, status = forward("/version")
   return jsonify(result), status


if __name__ == "__main__":
   app.run(host="0.0.0.0", port=8080)
