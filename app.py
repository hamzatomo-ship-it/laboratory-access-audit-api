
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "Laboratory Access Audit API is running"
    })

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "laboratory-access-audit-api"
    })

if __name__ == "__main__":
    app.run(debug=True)
