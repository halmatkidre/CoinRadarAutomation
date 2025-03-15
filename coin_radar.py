import time
import requests
import xml.etree.ElementTree as ET
import openai
import schedule
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# ======================================
# 🔑 API KEYS (REPLACE WITH YOURS)
# ======================================
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# ======================================
# 📡 RSS FEEDS (Market News Sources)
# ======================================
RSS_FEEDS = ["https://rss.app/feeds/_j9uGglnrYRY9l99u.xml"]

# ======================================
# 🏷️ HASHTAGS & ACCOUNTS
# ======================================
CRYPTO_HASHTAGS = ["#Bitcoin", "#Crypto", "#Ethereum", "#DeFi", "#NFT"]
MARKET_HASHTAGS = ["#StockMarket", "#Investing", "#Finance"]
EMOJIS = ["📈", "📉", "💰", "🚀", "💎", "🔥"]

# ======================================
# 🤖 OpenAI API
# ======================================
openai.api_key = OPENAI_API_KEY

# ======================================
# 📰 Fetch Latest Market News from RSS
# ======================================
def get_latest_news():
    entries = []
    for feed_url in RSS_FEEDS:
        try:
            response = requests.get(feed_url, timeout=10)
            response.raise_for_status()
            tree = ET.fromstring(response.content)

            for item in tree.findall('.//item'):
                entry = {
                    "title": item.findtext('title'),
                    "link": item.findtext('link'),
                    "summary": item.findtext('description', ""),
                }
                entries.append(entry)
        except Exception as e:
            print(f"⚠️ Error fetching RSS feed: {e}")
    return entries[:5]

# ======================================
# 🤖 Generate Tweet with OpenAI
# ======================================
def generate_tweet(news_item):
    prompt = f"""
    Generate a short, engaging tweet (<270 chars) about this market update:

    Title: {news_item['title']}
    Summary: {news_item['summary']}

    - Keep it urgent, like breaking news.
    - Add 1-2 relevant hashtags from {CRYPTO_HASHTAGS + MARKET_HASHTAGS}.
    - Include an emoji from {EMOJIS}.
    - Make traders feel like they need to act now.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Error generating tweet: {e}")
        return None

# ======================================
# 🐦 Twitter Posting with Selenium
# ======================================
def post_tweet_selenium(tweet_text):
    driver = webdriver.Chrome()

    try:
        # Open Twitter login page
        driver.get("https://twitter.com/login")
        input("🔵 Please log in manually, then press Enter to continue...")

        print("✅ Twitter Login successful!")

        # Open tweet box
        driver.get("https://twitter.com/compose/tweet")
        time.sleep(5)

        # Locate tweet input field
        tweet_input = driver.find_element(By.XPATH, "//div[@aria-label='Tweet text']")
        tweet_input.send_keys(tweet_text)

        # Post the tweet
        tweet_input.send_keys(Keys.CONTROL, Keys.ENTER)
        time.sleep(3)

        print("✅ Tweet posted successfully!")
        driver.quit()

    except Exception as e:
        print(f"⚠️ Error: {e}")
        driver.quit()

# ======================================
# 🚀 Main Posting Function
# ======================================
def post_market_update():
    print("🚀 Fetching latest market news...")
    news_items = get_latest_news()

    if news_items:
        news_item = news_items[0]
        tweet_text = generate_tweet(news_item)

        if tweet_text:
            post_tweet_selenium(f"{tweet_text} {news_item['link']}")
        else:
            print("⚠️ Tweet generation failed.")
    else:
        print("⚠️ No fresh market news found.")

# ======================================
# ⏰ Scheduling Market Updates (3x daily)
# ======================================
schedule.every().day.at("09:20").do(post_market_update)
schedule.every().day.at("13:00").do(post_market_update)
schedule.every().day.at("21:20").do(post_market_update)

print("✅ Coin Radar Automation Running! 🚀")

# ======================================
# 🔄 Run Scheduler Loop
# ======================================
while True:
    schedule.run_pending()
    time.sleep(60)
