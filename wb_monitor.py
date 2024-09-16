import requests
import json
import os
import time
import hashlib
import hmac
import base64
import yaml
from bs4 import BeautifulSoup


demo_webhook_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/your_webhook_url_here'

# 读取配置文件
with open('config.yml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

USER_IDS = config.get('user_ids', [])
LARK_WEBHOOK_URL = config.get('lark', {}).get('webhook_url', '')
LARK_WEBHOOK_SECRET = config.get('lark', {}).get('webhook_secret', '')
SENT_IDS_FILE = config.get('sent_ids_file', 'sent_ids.json')

def fetch_latest_posts(user_id):
    """获取指定微博用户的最新博文。"""
    container_id = f'107603{user_id}'
    weibo_api_url = f'https://m.weibo.cn/api/container/getIndex?type=uid&value={user_id}&containerid={container_id}'
    print(weibo_api_url)

    response = requests.get(weibo_api_url)
    if response.status_code == 200:
        data = response.json()
        cards = data.get('data', {}).get('cards', [])

        posts = []
        for card in cards:
            username = card.get('mblog',{}).get('user', {}).get('screen_name','未知用户')

            if card.get('card_type') == 9:
                mblog = card.get('mblog', {})
                post_id = mblog.get('id')
                text = mblog.get('text')
                # 清理文本，移除HTML标签
                soup = BeautifulSoup(text, 'html.parser')
                plain_text = soup.get_text()
                posts.append({
                    'id': post_id,
                    'text': plain_text,
                    'username': username
                })
        return posts
    else:
        print(f"获取用户 {user_id} 的微博失败，状态码 {response.status_code}")
        return []

def load_sent_ids():
    """加载已发送的消息ID字典。"""
    if os.path.exists(SENT_IDS_FILE):
        with open(SENT_IDS_FILE, 'r', encoding='utf-8') as f:
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
    with open(SENT_IDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(serializable_sent_ids, f, ensure_ascii=False, indent=4)



def gen_sign(timestamp, secret):
    # 拼接timestamp和secret
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    # 对结果进行base64处理
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign


def send_lark_message(username, text, webhook_url, secret=None):
    """通过飞书Webhook发送卡片消息，支持签名校验。"""
    timestamp = str(int(time.time()))
    headers = {'Content-Type': 'application/json'}
    # 构建卡片内容
    card = {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": username
            }
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "plain_text",
                    "content": text
                }
            }
        ]
    }
    data = {
        "timestamp": timestamp,
        "msg_type": "interactive",
        "card": card
    }
    # 如果提供了密钥，计算签名
    if secret:
        data['sign'] = gen_sign(timestamp=timestamp,secret=secret)

    if webhook_url == demo_webhook_url:
        print(json.dumps(data, ensure_ascii=False))
        return
    
    response = requests.post(webhook_url, headers=headers, data=json.dumps(data))

    print(json.dumps(data), response.content)

    if response.status_code == 200:
        print(f"来自 {username} 的消息发送成功。")
    else:
        print(f"发送来自 {username} 的消息失败，状态码 {response.status_code}，响应内容: {response.text}")

def main():
    sent_ids = load_sent_ids()
    print(sent_ids)
    for user_id_i in USER_IDS:
        user_id = str(user_id_i)
        latest_posts = fetch_latest_posts(user_id)
        user_sent_ids = sent_ids.get(user_id, set())
        new_posts = [post for post in latest_posts if post['id'] not in user_sent_ids]
        for post in new_posts:
            send_lark_message(post['username'], post['text'], LARK_WEBHOOK_URL, LARK_WEBHOOK_SECRET)
            user_sent_ids.add(post['id'])
        sent_ids[user_id] = user_sent_ids
    save_sent_ids(sent_ids)

if __name__ == '__main__':
    main()
