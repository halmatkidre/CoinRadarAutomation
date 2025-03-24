import os
import time
import requests
import openai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Retrieve credentials
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWITTER_USER = os.getenv("TWITTER_USER")
TWITTER_PASS = os.getenv("TWITTER_PASS")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found.")
if not TWITTER_USER or not TWITTER_PASS:
    raise ValueError("Twitter credentials not found.")

openai.api_key = OPENAI_API_KEY

# Configure Chromium options for headless GitHub Actions
options = Options()
options.binary_location = "/usr/bin/chromium-browser"  # for GitHub's Ubuntu runner
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    # 1. Go to Twitter login page
    driver.get("https://twitter.com/login")

    # 2. Enter username/email
    username_field = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.NAME, "text"))
    )
    username_field.send_keys(TWITTER_USER)

    # 3. Click 'Next'
    next_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]/ancestor::div[@role="button"]'))
    )
    next_button.click()

    # 4. Enter password
    password_field = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.NAME, "password"))
    )
    password_field.send_keys(TWITTER_PASS)

    # 5. Click 'Log In'
    login_button = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, '//span[text()="Log in"]/ancestor::div[@role="button"]'))
    )
    login_button.click()

    # 6. Wait until login is successful (e.g., presence of home link)
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '//a[@href="/home" or @href="/compose/tweet"]'))
    )
    print("✅ Successfully logged in!")
except Exception as e:
    print(f"⚠️ Login failed: {e}")
    driver.quit()
    exit(1)

# Now navigate to tweet composition page and proceed as before:
driver.get("https://twitter.com/compose/tweet")
# ... your existing code to generate tweet text and post tweet follows ...

# Finally, clean up:
driver.quit()
