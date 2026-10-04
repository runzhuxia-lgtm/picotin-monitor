import os
import requests
from bs4 import BeautifulSoup

URL = os.environ.get("PICOTIN_URL")
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

    if not URL:
        raise RuntimeError("PICOTIN_URL is not set")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    response = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    print("Hermes status:", response.status_code)

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)

    print("Page received successfully.")

    sold_out_words = [
        "在庫なし",
        "現在オンラインでは購入いただけません",
        "在庫切れ",
        "SOLD OUT",
    ]

    in_stock_words = [
        "カートに入れる",
        "バッグに追加",
        "購入する",
    ]

    for word in in_stock_words:
        if word in text:
            print("Possible stock found:", word)
            return True

    for word in sold_out_words:
        if word in text:
            print("Sold out:", word)
            return False

    print("Stock status could not be confirmed.")
    return False


def main():
    print("=== PICOTIN MONITOR START ===")

    if not URL:
        raise RuntimeError("PICOTIN_URL is missing")

    if not LINE_TOKEN:
        raise RuntimeError("LINE_CHANNEL_ACCESS_TOKEN is missing")

    if not LINE_USER_ID:
        raise RuntimeError("LINE_USER_ID is missing")

    print("Secrets are configured.")
    print("Checking:", URL)

    stock = check_stock()

    if stock:
        print("STOCK FOUND!")

        send_line(
            "👜 ピコタン・ロック 18\n"
            "在庫がある可能性があります！\n\n"
            f"{URL}"
        )

        print("LINE notification sent.")

    else:
        print("No stock found.")


if __name__ == "__main__":
    main()
