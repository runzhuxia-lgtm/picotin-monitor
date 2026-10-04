import os
import requests
from bs4 import BeautifulSoup

PICOTIN_URL = os.environ.get("PICOTIN_URL")
LINE_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")


def send_line(message):
    if not LINE_TOKEN or not LINE_USER_ID:
        print("LINE settings are missing.")
        return

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
        timeout=30,
    )

    print("LINE status:", response.status_code)


def check_stock():
    print("Checking Hermes page...")

    if not PICOTIN_URL:
        print("PICOTIN_URL is missing.")
        return "ERROR"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    try:
        response = requests.get(
            PICOTIN_URL,
            headers=headers,
            timeout=30,
            allow_redirects=True,
        )
    except requests.RequestException as e:
        print("Connection error:", e)
        return "ERROR"

    print("HTTP status:", response.status_code)
    print("Final URL:", response.url)

    # エルメス側に拒否された場合
    if response.status_code == 403:
        print("ACCESS BLOCKED: Hermes returned HTTP 403.")
        print("Stock status cannot be determined.")
        return "BLOCKED"

    if response.status_code != 200:
        print("Unexpected HTTP status:", response.status_code)
        return "ERROR"

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True).lower()

    # 在庫なしを先に判定
    sold_out_words = [
        "現在在庫がございません",
        "このアイテムは現在在庫がございません",
        "現在オンラインでは購入いただけません",
        "在庫なし",
        "在庫切れ",
        "sold out",
    ]

    for word in sold_out_words:
        if word.lower() in text:
            print("NO STOCK:", word)
            return "NO_STOCK"

    # ピコタンの商品ページか確認
    product_words = [
        "ピコタン ロック",
        "ピコタン・ロック",
        "picotin lock",
    ]

    if not any(word.lower() in text for word in product_words):
        print("Picotin product page could not be confirmed.")
        return "UNKNOWN"

    # 購入可能表示
    buy_words = [
        "カートに追加",
        "カートに入れる",
        "バッグに追加",
        "購入する",
    ]

    for word in buy_words:
        if word.lower() in text:
            print("STOCK FOUND:", word)
            return "STOCK"

    print("Product page found, but purchase button not detected.")
    return "UNKNOWN"


def main():
    print("=== PICOTIN JOHNNY SP CLOUD START ===")

    result = check_stock()

    print("RESULT:", result)

    if result == "STOCK":
        send_line(
            "🚨🚨 ピコジョニSP 🚨🚨\n\n"
            "ピコタン・ロック18が購入可能になった可能性があります！\n\n"
            "今すぐ確認してください👇\n"
            f"{PICOTIN_URL}"
        )

    elif result == "BLOCKED":
        # 403は在庫なしとは判定しない
        print("Hermes blocked this cloud request.")
        print("No stock judgment was made.")

    elif result == "NO_STOCK":
        print("No stock.")

    else:
        print("Stock status could not be determined.")

    # 403でもGitHub Actions自体は正常終了
    print("=== FINISHED ===")


if __name__ == "__main__":
    main()
