from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import shutil
import time

def fetch_chrome_blog_posts():
    """
    Fetches post titles and URLs using Selenium, handling cookie banners and dynamic content.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--ignore-certificate-errors')


    # Manually create and manage a temp directory
    temp_dir = os.path.abspath("chrome_temp_data")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    chrome_options.add_argument(f"--user-data-dir={temp_dir}")

    blog_posts = []
    driver = None
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        URL = "https://developer.chrome.com/blog/"
        driver.get(URL)

        # --- SOLUTION: HANDLE COOKIE BANNER ---
        try:
            # Wait up to 5 seconds for the cookie notification bar's button to be clickable
            cookie_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//devsite-cookie-notification-bar//button"))
            )
            cookie_button.click()
            # Give a moment for the banner to disappear
            time.sleep(1)
        except Exception:
            # If the banner is not found, just continue
            print("Cookie banner not found, proceeding...")
            pass
        # -----------------------------------------

        # Wait for the dynamically loaded cards to be present
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "devsite-card-wrapper"))
        )

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        
        # Find the new card elements
        posts = soup.find_all("div", class_="devsite-card-wrapper", limit=5)
        for post in posts:
            # The title and URL are available as attributes on the wrapper element.
            if 'displaytitle' in post.attrs and 'url' in post.attrs:
                title = post['displaytitle']
                url = post['url']
                # Ensure the URL is absolute
                if not url.startswith('http'):
                    url = f"https://developer.chrome.com{url}"
                blog_posts.append({'title': title, 'url': url})

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        if driver:
            # Save the page source for debugging when an error occurs
            try:
                # Fix: Save the debug file inside the script's directory
                script_dir = os.path.dirname(os.path.abspath(__file__))
                debug_file_path = os.path.join(script_dir, "debug_page_source.html")
                with open(debug_file_path, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print(f"Saved page source to {debug_file_path} for analysis.")
            except Exception as write_e:
                print(f"Failed to write debug file: {write_e}")
    finally:
        if driver:
            driver.quit()
        # Clean up the manually created directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    return blog_posts