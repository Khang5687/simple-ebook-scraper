import json
import os


def save_cookie(cookie_value, expired=False):
    # Create a dictionary with the cookie value and expired status
    cookie_data = {"value": cookie_value, "expired": expired}

    # Open the cookies.json file in append mode
    with open("cookies.json", "w") as file:
        # Write the cookie_data to the file
        json.dump(cookie_data, file)
        file.write("\n")  # Ensure each cookie is on a new line


def load_cookie():
    # Check if the cookies.json file exists
    if not os.path.exists("cookies.json"):
        return None

    # Open the cookies.json file in read mode
    with open("cookies.json", "r") as file:
        # Read all lines
        lines = file.readlines()

    # Iterate over the lines in reverse order to find the most recent non-expired cookie
    for line in reversed(lines):
        cookie_data = json.loads(line)
        if not cookie_data.get("expired", True):
            return cookie_data

    # Return None if no non-expired cookie is found
    return None
