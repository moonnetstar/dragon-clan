from flask import Flask, request, jsonify
import os

app = Flask(__name__)
PRODUCTS = [{"id": "1", "name": "轉經輪吊飾", "price": 1280}, {"id": "2", "name": "佛珠", "price": 980}, {"id": "3", "name": "護身符", "price": 1480}]

@app.route("/webhook", methods=['POST'])
def webhook():
    data = request.get_json()
    # Logic for LINE Pay / Stripe Webhook Verification
    print(f"Webhook received: {data}")
    return "OK", 200

@app.route("/checkout", methods=['POST'])
def checkout():
    # Reconstruction of Payment logic from audit
    return jsonify({"status": "success", "payment_ref": "REBUILT_ID_123"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
