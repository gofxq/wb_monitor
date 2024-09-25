import requests
import json
import os
import time
import yaml
from bs4 import BeautifulSoup

from app.plog.logger import setup_logger
from app.utils import lark, lark_boot_webhook_msg


log = setup_logger(name="monitor")

# 读取配置文件
with open("config.yml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

USER_IDS = config.get("user_ids", [])
LARK_WEBHOOK_URL = config.get("lark", {}).get("webhook_url", "")
LARK_WEBHOOK_SECRET = config.get("lark", {}).get("webhook_secret", "")
SENT_IDS_FILE = config.get("sent_ids_file", "sent_ids.json")
APP_ID = config.get("lark", {}).get("app_id", "")
APP_SECRET = config.get("lark", {}).get("app_secret", "")

client = lark.LarkClient(APP_ID, APP_SECRET)


def fetch_latest_posts(user_id):
    """获取指定微博用户的最新博文。"""
    container_id = f"107603{user_id}"
    weibo_api_url = f"https://m.weibo.cn/api/container/getIndex?type=uid&value={user_id}&containerid={container_id}"
    log.info(weibo_api_url)

    response = requests.get(weibo_api_url)
    if response.status_code == 200:
        data = response.json()
        cards = data.get("data", {}).get("cards", [])

        posts = []
        for card in cards:
            username = (
                card.get("mblog", {}).get("user", {}).get("screen_name", "未知用户")
            )

            if card.get("card_type") == 9:
                mblog = card.get("mblog", {})
                post_id = mblog.get("id")
                text = mblog.get("text")
                # 清理文本，移除HTML标签
                soup = BeautifulSoup(text, "html.parser")
                plain_text = soup.get_text()

                # 提取 large_url
                image_urls = []
                if mblog.get("pics") is not None:
                    image_urls = [pic["large"]["url"] for pic in mblog.get("pics")]

                posts.append(
                    {
                        "id": post_id,
                        "text": plain_text,
                        "username": username,
                        "image_urls": image_urls,
                        "link": card.get("scheme", weibo_api_url),
                    }
                )
        return posts
    else:
        log.warning(f"获取用户 {user_id} 的微博失败，状态码 {response.status_code}")
        return []


def load_sent_ids():
    """加载已发送的消息ID字典。"""
    if os.path.exists(SENT_IDS_FILE):
        with open(SENT_IDS_FILE, "r", encoding="utf-8") as f:
            sent_ids = json.load(f)
            # 将列表转换为集合
            for user_id in sent_ids:
                sent_ids[user_id] = set(sent_ids[user_id])
    else:
        sent_ids = {}
    return sent_ids


def save_sent_ids(sent_ids):
    """保存已发送的消息ID字典。"""
    # 将集合转换为列表以便JSON序列化
    serializable_sent_ids = {user_id: list(ids) for user_id, ids in sent_ids.items()}
    with open(SENT_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable_sent_ids, f, ensure_ascii=False, indent=4)


def check():
    lark_bot = lark_boot_webhook_msg.LarkBot(LARK_WEBHOOK_URL, LARK_WEBHOOK_SECRET)
    sent_ids = load_sent_ids()
    for user_id_i in USER_IDS:
        user_id = str(user_id_i)
        latest_posts = fetch_latest_posts(user_id)
        user_sent_ids = sent_ids.get(user_id, set())
        new_posts = [post for post in latest_posts if post["id"] not in user_sent_ids]
        for post in new_posts:
            log.info(post)
            img_keys = []
            if post["image_urls"] is not None:
                img_keys = client.upload_images_from_urls(image_urls=post["image_urls"])

            log.info(user_id, post)
            lark_bot.send_card_msg(
                card=lark_boot_webhook_msg.build_card_message(
                    post["username"],
                    f"{post['text']}\n[快速链接]({post['link']})",
                    img_keys,
                )
            )
            time.sleep(1)
            user_sent_ids.add(post["id"])
        sent_ids[user_id] = user_sent_ids
    save_sent_ids(sent_ids)


if __name__ == "__main__":
    check()
