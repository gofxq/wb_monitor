import requests


def fetch_image(url, headers=None):
    """
    Fetches an image from a URL using optional HTTP headers.

    Parameters:
    url (str): URL to the image to be fetched.
    headers (dict, optional): HTTP headers to be used in the request.

    Returns:
    bytes: The binary content of the image if the request is successful, None otherwise.
    """
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.content
    except requests.RequestException as e:
        print(f"Error fetching image: {e}")
        return None


def fetch_wb_image(url):
    headers = {
        # 'Referer': 'https://m.weibo.cn/',
    }
    return fetch_image(url, headers)


def save_image_to_file(image_bytes, file_path):
    """
    Saves binary image data to a file.

    Parameters:
    image_bytes (bytes): Binary data of the image to be saved.
    file_path (str): Path where the image should be saved.

    Returns:
    bool: True if the image is saved successfully, False otherwise.
    """
    if image_bytes:
        try:
            with open(file_path, "wb") as file:
                file.write(image_bytes)
            return True
        except IOError as e:
            print(f"Error saving image: {e}")
            return False
    else:
        print("No image data to save.")
        return False


if __name__ == "__main__":
    # 使用例子
    url = "https://wx2.sinaimg.cn/orj360/002OppCngy1hqc92lj800j61kc9wwb2a02.jpg"
    image_bytes = fetch_wb_image(url)
    if image_bytes:
        print("Image fetched successfully.")
        save_image_to_file(image_bytes=image_bytes, file_path="test.jpg")
    else:
        print("Failed to fetch image.")
