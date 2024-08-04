import pathlib
from utils import save_cookies
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def format_cookies(cookies):
    """Format cookies into a string

    Args:
        cookies (_list_): List of cookies

    Returns:
        _str_: Formatted cookies
    """
    cookies = [
        cookie
        for cookie in cookies
        if cookie["name"] == "Drupal_visitor_sigma_known_user"
        or cookie["name"].startswith("SSESS")
    ]

    # Create a dictionary to store the desired cookies
    cookie_dict = {}

    # Iterate through the cookies and add them to the dictionary
    for cookie in cookies:
        cookie_dict[cookie["name"]] = cookie["value"]

    # Assign the dictionary to the "cookies" variable
    return cookie_dict


def login(email, password):
    # Initialize WebDriver, allocating a user-data-dir to store cookies
    # user-data-dir: .\selenium
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={pathlib.Path().absolute()}\\web_cache")
    chrome_options.add_argument("log-level=3")
    chrome_options.add_argument("no-sandbox")
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to target URL
    # This URL is the RMIT Library database, used as a placeholder to trigger the Microsoft login page
    driver.get(
        "https://rmitlibraryvn.rmit.edu.vn/view/action/uresolver.do?operation=resolveService&package_service_id=5097042330006821&institutionId=6821&customerId=6820&VE=true"
    )

    # Wait for redirection to Microsoft Authentication login page
    try:
        WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.ID, "Ecom_User_ID"))
        )
    except:
        print("Already logged in")
        # Retrieve all cookies
        cookies = driver.get_cookies()

        driver.quit()

        # Return or print the cookie value
        if cookies:
            return format_cookies(cookies)
        else:
            return None

    # Input email
    email_input = driver.find_element(By.ID, "Ecom_User_ID")
    email_input.send_keys(email)

    # Wait for password input to be visible
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "Ecom_Password"))
    )

    # Input password and submit
    password_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "Ecom_Password"))
    )
    password_input.send_keys(password)

    # Click login button
    login_button = driver.find_element(By.NAME, "loginButton2")
    login_button.click()

    # Wait for cookies to have 2 keys "Drupal_visitor_sigma_known_user" and anything starts with "SSESS"
    try:
        WebDriverWait(driver, 20).until(
            lambda driver: len(
                [
                    cookie
                    for cookie in driver.get_cookies()
                    if cookie["name"] == "Drupal_visitor_sigma_known_user"
                ]
            )
            >= 1
            and any(
                cookie["name"].startswith("SSESS") for cookie in driver.get_cookies()
            )
        )
    except:
        print("Login failed")
        driver.quit()
        return None

    # Retrieve all cookies
    cookies = driver.get_cookies()
    cookies = format_cookies(cookies)

    driver.quit()

    # Return or print the cookie value
    if cookies:
        save_cookies(cookies)
        return cookies
    else:
        return None
