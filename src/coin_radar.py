import os
import time
import requests
import openai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Function to clean text and remove unsupported characters
def clean_text(text):
    return ''.join(c for c in text if ord(c) <= 0xFFFF)

# Retrieve OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("⚠️ OpenAI API key not found. Set it in your PC's environment variables.")
openai.api_key = OPENAI_API_KEY

print("🚀 Coin Radar Automation Started!")

# Configure Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--disable-dev-shm-usage")  # Stabilize memory usage
options.add_argument("--no-sandbox")            # Run without sandboxing
options.add_argument("--disable-extensions")    # Disable browser extensions
options.add_argument("--disable-gpu")           # Reduce GPU usage
options.add_argument("--remote-debugging-port=9222")
options.add_argument("--log-level=0")
options.add_argument("--verbose")

# Ensure correct profile path
profile_path = "C:/Users/Halma/Projects/Selenium/automation_profile"
if os.path.exists(profile_path):
    print(f"✅ Profile path exists: {profile_path}")
else:
    print(f"⚠️ Profile path does not exist: {profile_path}. Creating...")
    os.makedirs(profile_path)

options.add_argument(f"user-data-dir={profile_path}")

chromedriver_path = "C:/Users/Halma/Projects/Selenium/drivers/chromedriver.exe"

# Initialize WebDriver
try:
    print("⏳ Initializing WebDriver...")
    service = Service(chromedriver_path, service_args=["--verbose", "--log-path=chromedriver.log"])
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ WebDriver initialized successfully!")

    # Navigate directly to tweet composition
    print("🔗 Navigating to tweet composition...")
    driver.get("https://twitter.com/compose/tweet")

    # Wait for the tweet composition box to appear (indicating login is complete)
    print("⏳ Waiting for tweet composition box to load...")
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '//div[@role="textbox"]'))
    )
    print("✅ Login detected and tweet composition box is ready!")
except Exception as e:
    print(f"⚠️ Error initializing WebDriver: {e}")
    driver = None

# Function to fetch relevant crypto insights
def fetch_crypto_insights():
    print("📡 Fetching market-relevant crypto insights...")
    try:
        response = requests.get("https://api.coingecko.com/api/v3/global")
        response.raise_for_status()
        data = response.json()
        active_cryptos = data['data']['active_cryptocurrencies']
        market_cap = round(data['data']['total_market_cap']['usd'] / 1e9, 2)  # Convert to billions
        volume_24h = round(data['data']['total_volume']['usd'] / 1e9, 2)  # Convert to billions
        print(f"✅ Insights: Active Cryptos - {active_cryptos}, Market Cap - ${market_cap}B, Volume 24H - ${volume_24h}B")
        return f"There are currently {active_cryptos} active cryptocurrencies. The total market cap is ${market_cap}B, with a 24-hour trading volume of ${volume_24h}B."
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error fetching insights: {e}")
        return None

# Function to generate tweets using OpenAI
def generate_relevant_tweet():
    crypto_insights = fetch_crypto_insights()
    if not crypto_insights:
        return "⚠️ Unable to fetch market insights. Please try again later."

    print("✍️ Generating tweet with market relevance...")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Create an engaging tweet relevant to current cryptocurrency market and smart investing ideas."},
                {"role": "user", "content": f"Market data: {crypto_insights}"}
            ],
            temperature=0.7,
            max_tokens=100
        )
        tweet_text = response.choices[0].message.content.strip()
        print(f"✅ Tweet Generated: {tweet_text}")
        return tweet_text
    except Exception as e:
        print(f"⚠️ Error generating tweet: {e}")
        return "Crypto markets are thriving. Stay updated and make smart investment decisions! 🚀"

# Function to post tweet via Selenium
def post_tweet_selenium(tweet_text):
    if not tweet_text:
        print("⚠️ No tweet text provided!")
        return

    tweet_text = clean_text(tweet_text)
    print(f"DEBUG: Cleaned tweet text: {tweet_text}")

    print("🐦 Posting tweet to Twitter...")
    try:
        # Locate the tweet box
        print("DEBUG: Locating tweet box...")
        tweet_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@role="textbox"]'))
        )
        tweet_box.clear()  # Ensure the box is cleared
        tweet_box.send_keys(tweet_text)
        print("✅ Tweet text entered.")

        # Add delay for stabilization
        time.sleep(5)
        print("DEBUG: Locating Post button...")

        # Locate and click the "Post" button
        try:
            tweet_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="tweetButton" and not(@disabled)]'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", tweet_button)
            time.sleep(2)  # Stabilize
            tweet_button.click()
            print("✅ Post button clicked successfully!")
        except Exception as click_error:
            print(f"⚠️ Default click failed: {click_error}. Trying JavaScript click...")
            driver.execute_script("arguments[0].click();", tweet_button)
            print("✅ Post button clicked successfully using JavaScript!")
    except Exception as e:
        print(f"⚠️ Error posting tweet: {e}")
        driver.save_screenshot("post_error_screenshot.png")
        print("⚠️ Screenshot saved for debugging.")

# Main script logic
def run_coin_radar():
    if not driver:
        print("⚠️ WebDriver is not initialized. Exiting.")
        return
    print("🔄 Running Coin Radar automation cycle...")
    tweet_text = generate_relevant_tweet()
    if tweet_text:
        post_tweet_selenium(tweet_text)
        print("🛑 Automation cycle complete. Exiting.")

if __name__ == "__main__":
    print("DEBUG: Starting Immediate Test")
    run_coin_radar()
    print("DEBUG: Test Execution Completed")
    if driver:
        driver.quit()
        print("🛑 WebDriver closed.")
