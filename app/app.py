from flask import Flask, jsonify
import time

app = Flask(__name__)

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "message": "Zayzoon rocking here!",
        "timestamp": int(time.time())
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": int(time.time())
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
