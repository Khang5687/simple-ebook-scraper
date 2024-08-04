import os
import re
import json


def save_cookies(cookie_value):
    # Open the cookies.json file in write mode
    with open("cookies.json", "w") as file:
        # Write the cookie_value to the file
        json.dump(cookie_value, file, indent=4)


def load_cookies():
    # Check if the cookies.json file exists
    if not os.path.exists("cookies.json"):
        return None

    # Open the cookies.json file in read mode
    with open("cookies.json", "r") as file:
        # Load the cookie data
        cookie_data = json.load(file)

    return cookie_data


def convert_cookies(cookies):
    cookies_str = "; ".join([f"{key}={value}" for key, value in cookies.items()])
    return cookies_str


def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', "", filename).strip()
