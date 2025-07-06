from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def extract_imdb_reviews(url, waiting_timeout=8):
    """
    Scrapes IMDB user reviews from the given URL.

    Args:
        url (str): The URL of the IMDB reviews page.
        waiting_timeout (int): Maximum number of seconds to wait after clicking the "All" button,
                               allowing all reviews to fully load.

    Returns:
        List[str]: A list of extracted review texts.
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-features=VizDisplayCompositor")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)

        wait = WebDriverWait(driver, 10)

        all_button_clicked = False

        # Try to locate and click the "All" button using general XPath
        if not all_button_clicked:
            try:
                all_buttons = driver.find_elements(By.XPATH, '//button[contains(@class, "ipc-see-more")]')
                for button in all_buttons:
                    if 'All' in button.text:
                        driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", button)
                        all_button_clicked = True
                        break
            except Exception:
                pass

        # Wait for reviews to load after clicking the "All" button
        if all_button_clicked:
            time.sleep(waiting_timeout)
        else:
            time.sleep(3)

        # Extract HTML and parse with BeautifulSoup
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        reviews = []

        # Main selector
        results = soup.find_all('div', {'class': 'ipc-html-content-inner-div'})
        reviews.extend([review.get_text(strip=True) for review in results])

        # Fallback selector if none found
        if not reviews:
            results = soup.find_all('div', {'class': 'text show-more__control'})
            reviews.extend([review.get_text(strip=True) for review in results])

        return reviews

    finally:
        driver.quit()
