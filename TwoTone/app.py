from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

# Load products from external JSON (Foundation Task)
JSON_PATH = os.path.join(os.path.dirname(__file__), "products.json")
def load_products():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

@app.route("/webhook", methods=['POST'])
def webhook():
    """LINE Webhook 端點 - 實作 Carousel 商品卡片邏輯 (Task 1)"""
    event = request.get_json()
    print(f"Received event from LINE: {event}")
    
    # Logic to prepare a Carousel/Flex Message
    products = load_products()
    carousel_contents = []
    for p in products:
        carousel_contents.append({
            "type": "bubble",
            "hero": {"type": "image", "url": "https://via.placeholder.com/150", "size": "full", "aspectRatio": "20:13"},
            "body": {
                "type": "box", "layout": "vertical", "contents": [
                    {"type": "text", "text": p['name'], "weight": "bold", "size": "xl"},
                    {"type": "text", "text": f"${p['price']}", "size": "md", "color": "#999999"}
                ]
            },
            "footer": {
                "type": "box", "layout": "vertical", "contents": [
                    {"type": "button", "action": {"type": "postback", "label": "立即購買", "data": f"action=buy&id={p['id']}"}}
                ]
            }
        })

    # In a real scenario, you would reply to LINE via Messaging API here.
    # For now, we return the carousel structure as a placeholder response.
    return jsonify({
        "message_type": "carousel",
        "contents": carousel_contents
    }), 200

@app.route("/products", methods=['GET'])
def get_products():
    """提供前端 Carousel 展示商品清單"""
    return jsonify(load_products()), 200

@app.route("/checkout", methods=['POST'])
def checkout():
    """模擬 Stripe / LINE Pay 金流處理 (Task 2)"""
    data = request.get_json()
    product_id = data.get("product_id")
    payment_method = data.get("payment_method", "stripe") # stripe or linepay
    
    # Mock processing logic
    success = True # In real life, this would call an external API like Stripe
    if success:
        return jsonify({
            "status": "success",
            "message": f"Order for product {product_id} processed via {payment_method}!",
            "transaction_id": "TXN_123456789"
        }), 200
    else:
        return jsonify({"status": "fail", "message": "Payment failed!"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
