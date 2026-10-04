import os
import requests
from bs4 import BeautifulSoup

URL = os.environ["PICOTIN_URL"]
LINE_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_USER_ID = os.environ["LINE_USER_ID"]


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

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()


def check_stock():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)

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

    if any(word in text for word in in_stock_words):
        return True

    if any(word in text for word in sold_out_words):
        return False

    return False


if __name__ == "__main__":
    if check_stock():
        send_line(
            "👜 ピコタン・ロック 18\n"
            "在庫がある可能性があります！\n\n"
            f"{URL}"
        )
        print("在庫あり → LINE通知しました")
    else:
        print("在庫なし")
