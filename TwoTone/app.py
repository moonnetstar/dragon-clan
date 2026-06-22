# -*- coding: utf-8 -*-
"""TwoTone Shop — LINE Bot 龍族電商系統 v2.0"""
from __future__ import annotations
import os
import json
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify

from linebot import (
    LineBotApi,
    WebhookHandler,
)
from linebot.models import (
    MessageEvent,
    PostbackEvent,
    TextMessage,
    TextSendMessage,
    QuickReply,
    QuickReplyButton,
    TemplateSendMessage,
    CarouselTemplate,
    CarouselColumn,
    URITemplateAction,
    PostbackAction,
    MessageAction,
)

# ── env ────────────────────────────────────────────────
load_dotenv()

LINE_CHANNEL_ID = os.environ.get('LINE_CHANNEL_ID', '').strip()
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET', '').strip()
LINE_CHANNEL_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '').strip()

# ── Flask ─────────────────────────────────────────────
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

line_bot_api: LineBotApi | None = None
if LINE_CHANNEL_TOKEN:
    line_bot_api = LineBotApi(LINE_CHANNEL_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


# ── 資料 ──────────────────────────────────────────────
def load_products() -> list[dict]:
    """從 products.json 讀取商品清單."""
    path = os.path.join(os.path.dirname(__file__), 'products.json')
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_price(n: int | float) -> str:
    """NT$ 格式化."""
    return f'NT${n:,}'


def build_carousel(products: list[dict]) -> CarouselTemplate:
    """建立 carousel template."""
    columns = [
        CarouselColumn(
            thumb_image_url=f'https://via.placeholder.com/320x256?text={p["name"]}',
            action=PostbackAction(
                label='立即購買',
                data=f'action=buy&id={p["id"]}&name={p["name"]}&price={p["price"]}',
                text=f'我要買【{p["name"]}】NT${p["price"]:,.0f}！',
            ),
        )
        for p in products
    ]
    return CarouselTemplate(columns=columns, alt_text='龍族商城商品')


# ── 訊息組建 ──────────────────────────────────────────
WELCOME_MSG = TextSendMessage(
    text=(
        '👋 你好！歡迎來到「龍族商城」\n'
        '🛍️ 點擊下方快速入口或傳送關鍵字查詢商品：\n'
        '「商品」查看 catalog\n'
        '「客服」聯繫人工服務'
    ),
    quickreply=QuickReply(
        items=[
            QuickReplyButton(
                action=PostbackAction(
                    label='🛍️ 查看商品',
                    data='action=view_products',
                    text='請給我商品目錄！'
                )
            ),
            QuickReplyButton(
                action=MessageAction(
                    label='💬 聯繫客服',
                    text='客服'
                )
            ),
        ]
    )
)


def product_list_message(products: list[dict]) -> str:
    """商品列表文字訊息."""
    lines = ["🛍️ **龍族商城商品清單**\n"]
    for p in products:
        lines.append(f"• {p['name']} — {format_price(p['price'])}")
    lines.append(f"\n💡 總共 {len(products)} 款 / 點下方入口購買 →")
    return "\n".join(lines)


# ── Webhook 端點 ──────────────────────────────────────
@app.route("/callback", methods=["POST"])
def webhook():
    """LINE Webhook callback."""
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    logger.info(f"Received {len(body)} bytes")

    try:
        handler.handle(body, signature)
    except Exception as exc:
        logger.error("Webhook dispatch error: %s", exc, exc_info=True)
        return jsonify({"error": "webhook_dispatch_failed"}), 502

    return jsonify({"status": "ok"}), 200


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """文字訊息回覆."""
    text = event.message.text.strip().lower()

    # ── fallback: reply welcome + carousel to "hello"/hi ──
    if text in ("你好", "嗨", "hi", "hello"):
        products = load_products()
        msgs = [WELCOME_MSG]
        if products and line_bot_api:
            msgs.append(
                TemplateSendMessage(
                    alt_text=f'商品目錄 ({len(products)} 款)',
                    template=build_carousel(products)
                )
            )
        line_bot_api.reply_message(event.reply_token, msgs)
        return

    # ── 關鍵字路由 ───────────────────────────────────────
    if text == "商品":
        products = load_products()
        if not line_bot_api:
            return
        
        msgs = [TextSendMessage(text=product_list_message(products))]
        if products:
            msgs.append(
                TemplateSendMessage(
                    alt_text='商品目錄',
                    template=build_carousel(products)
                )
            )
        line_bot_api.reply_message(event.reply_token, msgs)

    elif text == "客服":
        if not line_bot_api:
            return
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(
                text=(
                    "📞 聯繫客服 \n"
                    "我們會在收到訊息後儘快回覆您 😊\n"
                    "#email: service@twotone-shop.com\n"
                    "#line: @twotone"
                )
            )
        ])

    else:
        # unknown keyword → welcome back + carousel
        products = load_products()
        if not line_bot_api:
            return
        
        msgs = [TextSendMessage(text="🤖 試試「商品」、「客服」等關鍵字！")]
        if products:
            msgs.append(
                TemplateSendMessage(
                    alt_text='龍族商城歡迎',
                    template=build_carousel(products)
                )
            )
        line_bot_api.reply_message(event.reply_token, msgs)


# ── POSTBACK (buy action) ─────────────────────────────
@handler.add(PostbackEvent)
def handle_postback(event):
    """處理 buy 動作."""
    data = event.postback.data  # e.g. action=buy&id=1&name=xxx&price=1280
    params = {}
    for part in data.split('&'):
        if '=' in part:
            k, v = part.split('=', 1)
            params[k] = v

    product_name = params.get('name', '?')
    price_str = format_price(params.get('price', 0))

    if params.get('action') == 'buy':
        if not line_bot_api:
            return
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(
                text=(
                    f'✅ 購買成功！\n'
                    f'📦 商品：{product_name} ({price_str})\n'
                    f'💳 訂單編號：TXN_{params["id"]:09}'
                )
            ),
        ])
    elif params.get('action') == 'view_products':
        products = load_products()
        if not line_bot_api:
            return
        
        if products:
            cols = [
                CarouselColumn(
                    thumb_image_url=f'https://via.placeholder.com/320x256?text={p["name"]}',
                    action=PostbackAction(
                        label='立即購買',
                        data=f'action=buy&id={p["id"]}&name={p["name"]}&price={p["price"]}',
                        text=f'我要買【{p["name"]}】NT${p["price"]:,.0f}！',
                    ),
                )
                for p in products
            ]
            template = CarouselTemplate(columns=cols, alt_text='龍族商城商品')
            msgs = [
                TextSendMessage(text=product_list_message(products)),
                TemplateSendMessage(alt_text='商品目錄', template=template),
            ]
        else:
            msgs = [TextSendMessage(text="目前沒有商品")]
        line_bot_api.reply_message(event.reply_token, msgs)


# ── health check for cron ───────────────────────────────
@app.route("/healthz", methods=["GET"])
def healthcheck():
    """簡單健康檢查 endpoint."""
    products = load_products()
    return jsonify({
        'services': 'LINE Bot is running',
        'product_count': len(products)
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
