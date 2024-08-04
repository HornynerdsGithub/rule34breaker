import requests
import xml.etree.ElementTree as ET
import os
import datetime
from urllib.parse import urljoin

def download_images():
    keyword = input("Enter the keyword: ")
    limit = int(input("Enter the number of images: "))

    base_url = "https://rule34.xxx"
    url = f"{base_url}/index.php?page=dapi&s=post&q=index&tags={keyword}&limit={limit}"
    headers = {"User-Agent": "My User Agent 1.0"}

    response = requests.get(url, headers=headers)
    print("Sending request to server...")
    print("Received response from server.")

    if response.status_code!= 200:
        print(f"Error: {response.status_code} - {response.reason}")
        return

    print("API Response:")
    print(response.text)

    try:
        data = ET.fromstring(response.content)
    except ET.ParseError:
        print("Error: Unable to parse XML response")
        return

    posts = data.findall("post")
    if not posts:
        print("Error: Response does not contain expected data")
        return

    main_folder = "scraped"
    if not os.path.exists(main_folder):
        os.makedirs(main_folder)

    now = datetime.datetime.now()
    subfolder = f"scraped/{now.strftime('%Y-%m-%d-%H-%M-%S')}"
    os.makedirs(subfolder)

    print("Image URLs:")
    image_urls = []
    for post in posts:
        file_url = post.attrib.get("file_url")
        if file_url:
            image_urls.append(file_url)
            print(image_urls[-1])

    for i, url in enumerate(image_urls):
        filename = os.path.basename(url)
        filepath = os.path.join(subfolder, filename)
        try:
            response = requests.get(url, stream=True)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded {filename}")
        except Exception as e:
            print(f"Error downloading {filename}: {e}")

    print("Scrape complete!")

download_images()