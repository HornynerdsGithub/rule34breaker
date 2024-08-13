import requests
import xml.etree.ElementTree as ET
import os
import datetime
from urllib.parse import urljoin
import json

class Scraper:
    def __init__(self):
        self.settings_file = "settings.json"
        self.load_settings_from_file()
        self.custom_location_path = ""

    def load_settings_from_file(self):
        try:
            with open(self.settings_file, "r") as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {
                "custom_location": False,
                "gifs_only": False,
                "exclude_tags": [],
                "exclude_downloaded": False,
            }
            self.save_settings_to_file()

    def save_settings_to_file(self):
        with open(self.settings_file, "w") as f:
            json.dump(self.settings, f, indent=4)

    def load_settings(self):
        while True:
            print("Settings:")
            for key, value in self.settings.items():
                print(f"{key}: {value}")
            print("1. Custom files location (optional)")
            print("2. Gifs only mode")
            print("3. Exclude certain content")
            print("4. Exclude already downloaded")
            print("5. Start scraping")
            choice = input("Choose a setting to toggle (or 5 to start scraping): ")
            if choice == "1":
                self.settings["custom_location"] = not self.settings["custom_location"]
                if self.settings["custom_location"]:
                    self.custom_location_path = input("Enter custom files location: ")
                else:
                    self.custom_location_path = ""
            elif choice == "2":
                self.settings["gifs_only"] = not self.settings["gifs_only"]
            elif choice == "3":
                self.settings["exclude_tags"] = input("Enter tags to exclude (comma separated): ").split(",")
            elif choice == "4":
                self.settings["exclude_downloaded"] = not self.settings["exclude_downloaded"]
            elif choice == "5":
                break
            else:
                print("Invalid choice. Please try again.")
            self.save_settings_to_file()

    def download_images(self):
        self.load_settings()

        keyword = input("Enter the keyword: ")
        limit = int(input("Enter the number of images: "))

        base_url = "https://rule34.xxx"
        url = f"{base_url}/index.php?page=dapi&s=post&q=index&tags={keyword}&limit={limit}"
        headers = {"User-Agent": "My User Agent 1.0"}

        response = requests.get(url, headers=headers)
        print("Sending request to server...")
        print("Received response from server.")

        if response.status_code != 200:
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

        main_folder = "scraped" if not self.settings["custom_location"] else self.custom_location_path
        if not os.path.exists(main_folder):
            os.makedirs(main_folder)

        now = datetime.datetime.now()
        subfolder = f"{main_folder}/{now.strftime('%Y-%m-%d-%H-%M-%S')}"
        os.makedirs(subfolder)

        print("Image URLs:")
        image_urls = []
        for post in posts:
            file_url = post.attrib.get("file_url")
            if file_url:
                if self.settings["gifs_only"] and not file_url.endswith(".gif"):
                    continue
                if self.settings["exclude_tags"] and any(tag in post.attrib.get("tags") for tag in self.settings["exclude_tags"]):
                    continue
                image_urls.append(file_url)
                print(image_urls[-1])

        for i, url in enumerate(image_urls):
            filename = os.path.basename(url)
            filepath = os.path.join(subfolder, filename)
            if self.settings["exclude_downloaded"] and os.path.exists(filepath):
                print(f"Skipping {filename} as it has already been downloaded")
                continue
            try:
                response = requests.get(url, stream=True)
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"Downloaded {filename}")
            except Exception as e:
                print(f"Error downloading {filename}: {e}")

        print("Scrape complete!")

if __name__ == "__main__":
    scraper = Scraper()
    while True:
        scraper.download_images()
        choice = input("Do you want to scrape again? (y/n): ")
        if choice.lower() != "y":
            break
    print("Goodbye!")