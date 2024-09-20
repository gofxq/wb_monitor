import requests
import time

from tenacity import retry, stop_after_attempt, wait_fixed


class LarkClient:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.token_info = {
            "tenant_access_token": None,
            "expire_time": 0,  # Token 过期的时间戳
        }

    # 使用装饰器
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def get_tenant_access_token(self):
        current_time = time.time()
        if (
            self.token_info["tenant_access_token"] is None
            or current_time >= self.token_info["expire_time"]
        ):
            # 如果 Token 不存在或已过期，重新获取
            url = (
                "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
            )
            headers = {"Content-Type": "application/json; charset=utf-8"}
            data = {"app_id": self.app_id, "app_secret": self.app_secret}
            response = requests.post(url, json=data, headers=headers)
            res_data = response.json()
            print(res_data)
            if res_data.get("code") == 0:
                self.token_info["tenant_access_token"] = res_data["tenant_access_token"]
                expires_in = res_data["expire"]  # Token 有效期（秒）
                # 设置过期时间，留出 60 秒的缓冲
                self.token_info["expire_time"] = current_time + expires_in - 60
            else:
                raise Exception(f"获取 Token 失败: {res_data.get('msg')}")
        return self.token_info["tenant_access_token"]

    def upload_images_from_urls(self, image_urls, image_type="message"):
        """
        上传多张图片到飞书，从给定的图片URL列表。

        参数：
        - image_urls: 图片URL列表
        - image_type: 图片类型，默认为 'message'

        返回值：
        - image_keys: 成功上传的图片的 image_key 列表
        """
        image_keys = []
        for url in image_urls:
            image_key = self.upload_image_from_url(url, image_type)
            image_keys.append(image_key)
        return image_keys

    def upload_image_from_url(self, image_url, image_type="message"):
        """
        通过图片 URL 上传图片，获取 image_key。

        :param image_url: 图片的网络 URL
        :param image_type: 图片类型，可选值为 "message", "avatar", "group_avatar"
        :return: image_key
        """
        # 下载图片
        response = requests.get(image_url)
        if response.status_code != 200:
            raise Exception(f"无法下载图片，状态码: {response.status_code}")

        token = self.get_tenant_access_token()
        url = "https://open.feishu.cn/open-apis/im/v1/images"
        headers = {"Authorization": f"Bearer {token}"}
        files = {
            "image_type": (None, image_type),
            "image": ("image", response.content, "application/octet-stream"),
        }
        response = requests.post(url, headers=headers, files=files)
        res_data = response.json()
        if res_data.get("code") == 0:
            image_key = res_data["data"]["image_key"]
            return image_key
        else:
            raise Exception(f"上传图片失败: {res_data.get('msg')}")

    def upload_image(
        self,
        image_path  # The `, image_type='message'` in the
        # `upload_image_by_path` method signature is a default
        # parameter value.
        ,
        image_type="message",
    ):
        """
        上传图片到 Lark，获取 image_key。

        :param image_path: 本地图片路径
        :param image_type: 图片类型，可选值为 "message", "avatar", "group_avatar"
        :return: image_key
        """
        token = self.get_tenant_access_token()
        url = "https://open.feishu.cn/open-apis/im/v1/images"
        headers = {"Authorization": f"Bearer {token}"}
        files = {
            "image_type": (None, image_type),
            "image": ("image.jpg", open(image_path, "rb"), "image/jpeg"),
        }
        response = requests.post(url, headers=headers, files=files)
        res_data = response.json()
        if res_data.get("code") == 0:
            image_key = res_data["data"]["image_key"]
            return image_key
        else:
            raise Exception(f"上传图片失败: {res_data.get('msg')}")

    def get_image_info(self, image_key):
        """
        获取图片信息。

        :param image_key: 上传图片返回的 image_key
        :return: 图片信息的字典
        """
        token = self.get_tenant_access_token()
        url = f"https://open.feishu.cn/open-apis/im/v1/images/{image_key}"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        res_data = response.json()
        if res_data.get("code") == 0:
            return res_data["data"]
        else:
            raise Exception(f"获取图片信息失败: {res_data.get('msg')}")


# 使用示例
if __name__ == "__main__":
    # 请替换为您的 app_id 和 app_secret
    # 读取配置文件
    with open("config.yml", "r", encoding="utf-8") as f:
        import yaml

        config = yaml.safe_load(f)

    APP_ID = config.get("lark", {}).get("app_id", "")
    APP_SECRET = config.get("lark", {}).get("app_secret", "")

    print(APP_ID, APP_SECRET)
    client = LarkClient(APP_ID, APP_SECRET)

    # 上传图片并获取 image_key
    image_key = client.upload_image_from_url(
        "https://wx2.sinaimg.cn/large/002OppCngy1hqc92lj800j61kc9wwb2a02.jpg"
    )
    print(f"上传成功，image_key: {image_key}")

    # 获取图片信息
    image_info = client.get_image_info(image_key)
    print(f"图片信息: {image_info}")
