import os
import requests
from bs4 import BeautifulSoup

PICOTIN_URL = os.environ.get("PICOTIN_URL")
LINE_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")


def send_line(message):
    url = "https://api.line.me/v2/bot/message/push"

    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json",
    }

    data = {
        "to": LINE_USER_ID,
        "messages": [
            {
                "type": "text",
                "text": message,
            }
        ],
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=30
    )

    print("LINE status:", response.status_code)
    print("LINE response:", response.text)

    response.raise_for_status()


def check_stock():
    print("Hermes page checking...")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    response = requests.get(
        PICOTIN_URL,
        headers=headers,
        timeout=30
    )

    print("Hermes status:", response.status_code)
    print("Final URL:", response.url)

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    print("Page received successfully.")
    print("Page text length:", len(text))

    # ---------------------------------
    # 1. 在庫なし判定を最優先
    # ---------------------------------

    sold_out_words = [
        "現在在庫がございません",
        "このアイテムは現在在庫がございません",
        "現在オンラインでは購入いただけません",
        "在庫なし",
        "在庫切れ",
        "SOLD OUT",
    ]

    for word in sold_out_words:
        if word.lower() in text.lower():
            print("SOLD OUT detected:", word)
            return False

    # ---------------------------------
    # 2. ピコタンの商品ページか確認
    # ---------------------------------

    product_words = [
        "ピコタン・ロック",
        "ピコタン ロック",
        "Picotin Lock",
    ]

    product_found = False

    for word in product_words:
        if word.lower() in text.lower():
            print("Product confirmed:", word)
            product_found = True
            break

    if not product_found:
        print("Picotin product page could not be confirmed.")
        return False

    # ---------------------------------
    # 3. 購入可能表示を確認
    # ---------------------------------

    buy_words = [
        "カートに追加",
        "カートに入れる",
        "バッグに追加",
        "購入する",
    ]

    for word in buy_words:
        if word.lower() in text.lower():
            print("BUY BUTTON detected:", word)
            return True

    print("Buy button not detected.")
    return False


def main():
    print("=== PICOTIN JOHNNY SP START ===")

    if not PICOTIN_URL:
        raise RuntimeError("PICOTIN_URL is missing")

    if not LINE_TOKEN:
        raise RuntimeError(
            "LINE_CHANNEL_ACCESS_TOKEN is missing"
        )

    if not LINE_USER_ID:
        raise RuntimeError(
            "LINE_USER_ID is missing"
        )

    print("Secrets are configured.")
    print("Checking:", PICOTIN_URL)

    stock = check_stock()

    if stock:
        print("STOCK FOUND!")

        send_line(
            "🚨🚨 ピコジョニSP 🚨🚨\n\n"
            "ピコタン・ロック18が購入可能になった可能性があります！\n"
            "今すぐ確認してください👇\n\n"
            f"{PICOTIN_URL}"
        )

        print("LINE notification sent.")

    else:
        print("NO STOCK - No notification.")


if __name__ == "__main__":
    main()
