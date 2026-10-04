import os
import requests
from bs4 import BeautifulSoup

LINE_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.environ.get("LINE_USER_ID")

LIST_URL = (
    "https://www.hermes.com/jp/ja/category/"
    "leather-goods/bags-and-clutches/womens-bags-and-clutches/"
    "?facet_category=sacs_a_main"
)

TARGETS = [
    "H056289CK18",
    "H056289CC18",
    "ピコタン・ロック",
    "ピコタン ロック",
]


def send_line(message):
    if not LINE_TOKEN or not LINE_USER_ID:
        print("LINE settings missing.")
        return

    response = requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={
            "Authorization": f"Bearer {LINE_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "to": LINE_USER_ID,
            "messages": [
                {
                    "type": "text",
                    "text": message,
                }
            ],
        },
        timeout=30,
    )

    print("LINE status:", response.status_code)


def check_list():
    print("Checking Hermes bag list...")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ja-JP,ja;q=0.9",
    }

    try:
        response = requests.get(
            LIST_URL,
            headers=headers,
            timeout=30,
        )
    except requests.RequestException as e:
        print("Connection error:", e)
        return "ERROR", []

    print("HTTP status:", response.status_code)
    print("Final URL:", response.url)

    if response.status_code == 403:
        print("Hermes blocked this request.")
        return "BLOCKED", []

    if response.status_code != 200:
        print("Unexpected HTTP status:", response.status_code)
        return "ERROR", []

    soup = BeautifulSoup(response.text, "html.parser")

    text = soup.get_text(" ", strip=True)

    found = []

    for target in TARGETS:
        if target.lower() in text.lower():
            found.append(target)

    if found:
        print("PICOTIN FOUND:", found)
        return "FOUND", found

    print("Picotin not found in current list.")
    return "NOT_FOUND", []


def main():
    print("=== PICOTIN JOHNNY SP LIST MONITOR ===")

    result, found = check_list()

    print("RESULT:", result)

    if result == "FOUND":

        message = (
            "🚨🚨 ピコジョニSP 🚨🚨\n\n"
            "エルメスのバッグ一覧に"
            "ピコタンが出現しました！\n\n"
            f"検出：{', '.join(found)}\n\n"
            "今すぐ確認👇\n"
            f"{LIST_URL}"
        )

        send_line(message)

    elif result == "NOT_FOUND":
        print("No Picotin currently listed.")

    elif result == "BLOCKED":
        print("Cloud request was blocked. No judgment made.")

    else:
        print("Could not determine status.")

    print("=== FINISHED ===")


if __name__ == "__main__":
    main()
