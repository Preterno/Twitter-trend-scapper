from flask import Flask, jsonify, request
from flask_cors import CORS
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pymongo import MongoClient
from datetime import datetime
import uuid
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv("MONGODB_URI"))
db = client['twitter_trends']
collection = db['trending_topics']

# Flask app
app = Flask(__name__)
CORS(app)

# ProxyMesh settings
proxy_user = os.getenv("PROXY_USER")
proxy_password = os.getenv("PROXY_PASSWORD")
proxy_url = f"http://{proxy_user}:{proxy_password}@in.proxymesh.com:31280"

# Proxy options
options = {
    'proxy': {
        'http': proxy_url,
        'https': proxy_url,
        'no_proxy': 'localhost,127.0.0.1'
    }
}

# Enhanced Chrome options for better headless operation
chrome_options = Options()
chrome_options.add_argument("--headless=new")  
chrome_options.add_argument("--window-size=1920,1080")  
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--enable-javascript")
chrome_options.add_argument("--lang=en-US,en;q=0.9")
chrome_options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')

# Add required capabilities
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.notifications": 2,
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
    "profile.default_content_settings.popups": 0,
})

chrome_driver_path = os.getenv("CHROMEDRIVER_PATH")
service = Service(executable_path=chrome_driver_path)

def login_and_get_trends(browser):
    """Handle Twitter login and immediately get trends"""
    try:
        # Execute stealth JS before loading page
        browser.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        })
        
        # Mask webdriver presence
        browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Load login page
        browser.get("https://x.com/i/flow/login?mx=2")
        time.sleep(2)
        
        # Username
        username = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        username.send_keys(os.getenv("TWITTER_USERNAME"))
        time.sleep(1)
        
        next_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']/ancestor::button"))
        )
        next_button.click()
        time.sleep(1)
        
        try:
            # Handle additional verification if needed
            span_element = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Enter your phone number or username')]"))
            )
            
            if span_element:
                input_field = WebDriverWait(browser, 5).until(
                    EC.presence_of_element_located((By.NAME, "text"))
                )
                input_field.send_keys(os.getenv("TWITTER_HANDLE"))
                
                next_button = WebDriverWait(browser, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']/ancestor::button"))
                )
                next_button.click()
                time.sleep(1)
        except TimeoutException:
            pass
        
        # Password
        password = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password.send_keys(os.getenv("TWITTER_PASSWORD"))
        
        login_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='LoginForm_Login_Button']"))
        )
        login_button.click()
        
        # Navigate to trending page
        for_you_button = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.XPATH, "//a[@role='link' and @href='/explore/tabs/for-you']//span[contains(text(), 'Show more')]"))
        )
        for_you_button.click()
        time.sleep(1)

        trending_button = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.XPATH, "//a[@role='tab' and @href='/explore/tabs/trending']//span[contains(text(), 'Trending')]"))
        )
        trending_button.click()
        time.sleep(1)
        
        # Get trending topics
        WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="trend"]'))
        )
        
        time.sleep(3)
        
        trends = []
        trend_elements = browser.find_elements(By.CSS_SELECTOR, '[data-testid="trend"]')
        
        for element in trend_elements[:5]:
            try:
                topic = element.find_element(
                    By.CSS_SELECTOR, 
                    'div[class*="r-b88u0q"]'
                ).text
                trends.append(topic)
            except Exception as e:
                print(f"Error extracting trend: {str(e)}")
                continue
        
        return trends
        
    except Exception as e:
        print(f"Error during login or getting trends: {str(e)}")
        raise

@app.route('/scrape-trends', methods=['GET'])
def scrape_twitter_trends():
    browser = None
    unique_id = str(uuid.uuid4())
    
    try:
        browser = webdriver.Chrome(service=service, seleniumwire_options=options, options=chrome_options)
        browser.set_page_load_timeout(30)
        
        values = login_and_get_trends(browser)
        
        if not values:
            raise Exception("No trending topics found")
        
        # Get IP address
        browser.get("https://api.ipify.org?format=text")
        ip_address = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//pre"))
        ).text
        
        result = {
            "unique_id": unique_id,
            "trending_topics": values,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip_address": ip_address
        }
        
        inserted_result = collection.insert_one(result)
        result["_id"] = str(inserted_result.inserted_id)
        
        return jsonify({"message": "Data saved successfully", "data": result}), 200
        
    except Exception as e:
        error_message = f"Error during scraping: {str(e)}"
        print(error_message)
        return jsonify({"error": error_message}), 500
        
    finally:
        if browser:
            browser.quit()

if __name__ == '__main__':
    app.run(debug=True)