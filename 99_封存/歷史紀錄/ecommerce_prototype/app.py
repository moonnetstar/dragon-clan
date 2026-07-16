
from flask import Flask, render_template, jsonify, request
import os

app = Flask(__name__)

# Mock Database
products_db = {
    1: {"name": "轉經輪吊飾", "price": 1280},
    2: {"name": "佛珠", "price": 980}
}

@app.route('/')
def index():
    # Renders the Frontend
    return render_template('index.html')

@app.route('/api/add_to_cart', methods=['POST'])
def add_to_cart():
    # THE BACKEND LOGIC (The 'Brain' of Bruce)
    data = request.json
    p_id = data.get('product_id')
    product = products_db.get(int(p_id))
    if product:
        return jsonify({"status": "success", "msg": f"已加入 {product['name']} 到購物車！"})
    return jsonify({"status": "error", "msg": "找不到商品"}), 404

if __name__ == '__main__':
    print("🚀 Bruce's Prototype Backend is running on http://127.0.0.1:5000")
    app.run(debug=True)
