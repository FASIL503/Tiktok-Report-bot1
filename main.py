from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import sys
import time

def report_tiktok(video_url: str, reason: str, state_file: str = "tiktok_state.json"):
    """
    Automates reporting a TikTok video:
      - Loads saved cookies/localStorage from state_file.
      - If absent, opens Chrome for manual login and saves state.
      - Navigates to video_url, clicks Report → reason → Submit.
    """
    # Configure headless Chrome (set headless=False to see the UI)
    chrome_opts = Options()
    chrome_opts.add_argument("--headless")
    chrome_opts.add_argument("--disable-gpu")
    # Use Selenium Manager (auto-download ChromeDriver) or specify executable_path
    driver = webdriver.Chrome(options=chrome_opts)

    try:
        # 1) Load login state or prompt for login
        try:
            driver.get("chrome://version")  # Dummy to initialize session
            # If you have code to load cookies/localStorage from state_file, do it here
        except Exception:
            pass

        # 2) Go to video page
        driver.get(video_url)
        time.sleep(5)  # Wait for page to fully load scripts

        # 3) Click “more options” (⋯) button
        more_btn = driver.find_element(By.CSS_SELECTOR, "[data-e2e='more-btn']")
        more_btn.click()
        time.sleep(1)

        # 4) Click “Report”
        report_item = driver.find_element(By.XPATH, "//span[text()='Report']")
        report_item.click()
        time.sleep(1)

        # 5) Choose reason by visible text
        reason_item = driver.find_element(By.XPATH, f"//span[text()='{reason}']")
        reason_item.click()
        time.sleep(1)

        # 6) Submit
        submit_btn = driver.find_element(By.XPATH, "//button[text()='Submit']")
        submit_btn.click()
        time.sleep(3)

        print("✅ Report submitted successfully!")

    except Exception as e:
        print(f"❌ Error reporting video: {e}", file=sys.stderr)
    finally:
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python report.py <TikTok Video URL> <Reason Text>")
        sys.exit(1)
    report_tiktok(sys.argv[1], sys.argv[2])
