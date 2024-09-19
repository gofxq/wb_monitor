import requests
import json
import time
import hashlib
import hmac
import base64
import yaml


demo_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/your_webhook_url_here"


class LarkBot:
    def __init__(self, webhook_url, webhook_secret=None):
        self.webhook_url = webhook_url
        self.webhook_secret = webhook_secret

    def send_msg(self, title, body):
        card = build_card_message(title, body)
        rsp = None
        try:
            rsp = self.send_card_msg(card)
        except Exception as e:
            print(f"send lark msg failed:{title},{body},{e}")

        return rsp

    def send_card_msg(self, card):
        """通过飞书Webhook发送卡片消息，支持签名校验。"""
        timestamp = str(int(time.time()))
        headers = {"Content-Type": "application/json"}
        data = {"timestamp": timestamp, "msg_type": "interactive", "card": card}

        if self.webhook_secret:
            data["sign"] = gen_sign(timestamp=timestamp, secret=self.webhook_secret)

        if self.webhook_url == "demo_webhook_url":
            return {"status": "debug_mode", "data": data}

        try:
            response = requests.post(self.webhook_url, headers=headers, json=data)
            response.raise_for_status()  # 触发HTTPError，如果状态不是200
            return {"code": 0, "msg": ""}
        except requests.exceptions.HTTPError as err_h:
            return {"code": 1, "msg": str(err_h)}
        except requests.exceptions.ConnectionError as err_c:
            return {"code": 2, "msg": str(err_c)}
        except requests.exceptions.Timeout as err_t:
            return {"code": 3, "msg": str(err_t)}
        except requests.exceptions.RequestException as err:
            return {"code": 4, "msg": str(err)}


def gen_sign(timestamp, secret):
    # 拼接timestamp和secret
    string_to_sign = "{}\n{}".format(timestamp, secret)
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    # 对结果进行base64处理
    sign = base64.b64encode(hmac_code).decode("utf-8")
    return sign


def build_card_message(title, text, image_keys=None):
    """
    构建卡片消息的内容。

    参数：
    - username: 用户名，作为卡片消息的标题。
    - text: 消息内容。
    - image_keys: 图片的 image_key 列表。

    返回值：
    - card: 卡片消息的内容。
    """
    # 构建卡片消息的头部
    card = {
        "header": {"title": {"tag": "plain_text", "content": title}},
        "elements": [
            {
                "tag": "markdown",
                "content": text,
                "text_align": "left",
                "text_size": "normal",
            }
        ],
        "config": {"wide_screen_mode": True},
    }

    # 如果有图片
    if image_keys:
        # 每组最多9张图片
        max_images_per_group = 9
        # 计算需要几个图片组
        num_groups = (
            len(image_keys) + max_images_per_group - 1
        ) // max_images_per_group

        for i in range(num_groups):
            # 获取当前组的图片 keys
            group_image_keys = image_keys[
                i * max_images_per_group : (i + 1) * max_images_per_group
            ]

            # 创建当前组的图片列表
            img_list = [{"img_key": img_key} for img_key in group_image_keys]

            # 创建一个新的 image_group
            image_group = {
                "tag": "img_combination",
                "combination_mode": "trisect",
                "corner_radius": "12px",  # 设置图片的圆角半径
                "img_list": img_list,
            }

            # 将当前的 image_group 添加到卡片的 elements 中
            card["elements"].append(image_group)

    return card


if __name__ == "__main__":

    # 读取配置文件
    with open("config.yml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    USER_IDS = config.get("user_ids", [])
    LARK_WEBHOOK_URL = config.get("lark", {}).get("webhook_url", "")
    LARK_WEBHOOK_SECRET = config.get("lark", {}).get("webhook_secret", "")
    SENT_IDS_FILE = config.get("sent_ids_file", "sent_ids.json")

    test_img_key = "img_v3_02er_d7754fcf-5c88-4680-a647-2470d0d2f4bh"

    lark_bot = LarkBot(LARK_WEBHOOK_URL, LARK_WEBHOOK_SECRET)
    lark_bot.send_msg("hello", "world")
    # send_lark_message(
    #     card=build_card_message(
    #         "username",
    #         "text",
    #         [
    #             test_img_key,
    #             test_img_key,
    #             test_img_key,
    #             test_img_key,
    #             test_img_key,
    #             test_img_key,
    #             test_img_key,
    #             test_img_key,
    #             test_img_key,
    #             test_img_key,
    #             test_img_key,
    #         ],
    #     ),
    #     webhook_url=LARK_WEBHOOK_URL,
    #     secret=LARK_WEBHOOK_SECRET,
    # )
