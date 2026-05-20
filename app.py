from flask import Flask, request, jsonify, render_template_string
import urllib.request
import json
import os

app = Flask(__name__)

# --- Config ---
# Set these as environment variables on Render
OPTIPLEX_URL = os.environ.get("OPTIPLEX_URL", "https://6fca-2601-98d-c082-7e60-c57e-3275-1f8-b562.ngrok-free.app")
API_KEY      = os.environ.get("KENBOT_API_KEY", "KENNY2012may30!")

# --- Helper: forward request to Optiplex ---
def forward(path, method="GET", body=None):
    url = OPTIPLEX_URL + path
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    try:
        if method == "POST":
            data = json.dumps(body).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        else:
            req = urllib.request.Request(url, headers=headers, method="GET")

        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8")), resp.status
    except Exception as e:
        return {"error": str(e)}, 500


# --- Chat page HTML ---
CHAT_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=windows-1252">
<title>KenBot - Ken Technologies Inc.</title>
<style>
body {
    background-color: #008080;
    background-image: url('/static/images/bg.gif');
    font-family: "MS Sans Serif", Arial, sans-serif;
    font-size: 11px;
    margin: 0;
    padding: 20px;
}

.window {
    background: #d4d0c8;
    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #808080;
    border-bottom: 2px solid #808080;
    width: 500px;
    margin: 0 auto;
}

.titlebar {
    background: #000080;
    color: #ffffff;
    font-weight: bold;
    padding: 3px 5px;
    font-size: 11px;
    display: block;
}

.window-body {
    padding: 8px;
}

.chatbox {
    width: 100%;
    height: 300px;
    background: #ffffff;
    border-top: 1px solid #808080;
    border-left: 1px solid #808080;
    border-right: 1px solid #ffffff;
    border-bottom: 1px solid #ffffff;
    font-family: "Fixedsys", "Courier New", monospace;
    font-size: 11px;
    overflow-y: scroll;
    padding: 4px;
    box-sizing: border-box;
    resize: none;
}

.input-row {
    margin-top: 6px;
    display: block;
}

.inputbox {
    width: 370px;
    border-top: 1px solid #808080;
    border-left: 1px solid #808080;
    border-right: 1px solid #ffffff;
    border-bottom: 1px solid #ffffff;
    background: #ffffff;
    font-family: "MS Sans Serif", Arial, sans-serif;
    font-size: 11px;
    padding: 2px;
}

.btn {
    background: #d4d0c8;
    border-top: 2px solid #ffffff;
    border-left: 2px solid #ffffff;
    border-right: 2px solid #808080;
    border-bottom: 2px solid #808080;
    font-family: "MS Sans Serif", Arial, sans-serif;
    font-size: 11px;
    padding: 2px 10px;
    cursor: pointer;
    margin-left: 4px;
}

.btn:active {
    border-top: 2px solid #808080;
    border-left: 2px solid #808080;
    border-right: 2px solid #ffffff;
    border-bottom: 2px solid #ffffff;
}

.statusbar {
    background: #d4d0c8;
    border-top: 1px solid #808080;
    margin-top: 6px;
    padding: 2px 4px;
    font-size: 10px;
    color: #000000;
}
</style>
</head>
<body>

<div class="window">
  <span class="titlebar">KenBot - Ken Technologies Inc.</span>
  <div class="window-body">
    <textarea class="chatbox" id="chatbox" readonly>KenBot Web Client
(c) Ken Technologies Inc. 1982-2001. All rights reserved.
================================
Type a message and press Send or Enter.

</textarea>
    <div class="input-row">
      <input class="inputbox" type="text" id="inputbox" maxlength="500">
      <input class="btn" type="button" value="Send" id="btnSend">
      <input class="btn" type="button" value="Reset" id="btnReset">
    </div>
    <div class="statusbar" id="status">Ready.</div>
  </div>
</div>

<script type="text/javascript">
function appendChat(text) {
    var box = document.getElementById('chatbox');
    box.value = box.value + text + '\\n';
    box.scrollTop = box.scrollHeight;
}

function setStatus(text) {
    document.getElementById('status').innerHTML = text;
}

function doSend() {
    var input = document.getElementById('inputbox');
    var msg = input.value;
    if (msg == null || msg == '') return;

    appendChat('You: ' + msg);
    input.value = '';
    setStatus('Waiting for KenBot...');

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/chat', false);
    xhr.setRequestHeader('Content-Type', 'application/json');
    try {
        xhr.send('{"message":"' + msg.replace(/\\\\/g, '\\\\\\\\').replace(/"/g, '\\\\"') + '"}');
        if (xhr.status == 200) {
            var resp = xhr.responseText;
            var start = resp.indexOf('"response":"');
            if (start != -1) {
                start = start + 12;
                var end = resp.indexOf('"', start);
                var response = resp.substring(start, end);
                response = response.replace(/\\\\n/g, '\\n');
                appendChat('KenBot: ' + response);
                setStatus('Connected.');
            } else {
                appendChat('KenBot: [Could not parse response]');
                setStatus('Parse error.');
            }
        } else {
            appendChat('KenBot: [No response - check connection]');
            setStatus('Error: HTTP ' + xhr.status);
        }
    } catch(e) {
        appendChat('KenBot: [Connection failed]');
        setStatus('Connection failed.');
    }
}

function doReset() {
    setStatus('Resetting memory...');
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/reset', false);
    try {
        xhr.send();
        if (xhr.status == 200) {
            appendChat('*** Memory cleared. ***');
            setStatus('Memory cleared.');
        } else {
            setStatus('Reset failed.');
        }
    } catch(e) {
        setStatus('Reset failed.');
    }
}

document.getElementById('btnSend').onclick = doSend;
document.getElementById('btnReset').onclick = doReset;

document.getElementById('inputbox').onkeypress = function(e) {
    var key = e ? e.which : window.event.keyCode;
    if (key == 13) { doSend(); }
}
</script>

</body>
</html>"""


# --- Routes ---

@app.route("/")
def index():
    return render_template_string(CHAT_PAGE)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    result, status = forward("/chat", method="POST", body=data)
    return jsonify(result), status


@app.route("/reset", methods=["GET"])
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
