
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import shutil

def fetch_chrome_blog_titles():
    """
    Fetches titles using Selenium, managing the user data directory manually.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Manually create and manage a temp directory within the project
    temp_dir = os.path.abspath("chrome_temp_data")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    chrome_options.add_argument(f"--user-data-dir={temp_dir}")

    post_titles = []
    driver = None
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        URL = "https://developer.chrome.com/blog/"
        driver.get(URL)

        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "dgc-card"))
        )

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        posts = soup.find_all("div", class_="dgc-card", limit=5)
        for post in posts:
            title_element = post.find("h2", class_="dgc-card__title")
            if title_element:
                post_titles.append(title_element.get_text(strip=True))
            
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
    finally:
        if driver:
            driver.quit()
        # Clean up the manually created directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    return post_titles
