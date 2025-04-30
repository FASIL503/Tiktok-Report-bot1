from playwright.sync_api import sync_playwright
import sys

def report_tiktok_video(video_url: str, reason_text: str, storage_path: str = "state.json"):
    """
    Automates reporting a TikTok video via browser UI:
      1. Loads saved authentication from storage_state (state.json).
      2. Navigates to the TikTok video URL.
      3. Opens the '...' menu, clicks 'Report', selects the reason, and submits.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set to False to see the browser UI
        context = browser.new_context(storage_state=storage_path)
        page = context.new_page()

        try:
            # 1) Navigate to video page
            page.goto(video_url, wait_until="networkidle")

            # 2) Open the “more options” menu (the 3-dot button)
            page.click("css=[data-e2e='more-btn']")

            # 3) Click the “Report” menu item
            page.click("text=Report")

            # 4) Choose the specified reason (by visible text)
            page.click(f"text={reason_text}")

            # 5) Submit the report
            page.click("text=Submit")

            # Wait for confirmation (could be a toast or dialog)
            page.wait_for_selector("text=Thank you for your report", timeout=5000)
            print("✅ Report submitted successfully!")

        except Exception as e:
            print(f"❌ Error during reporting: {e}", file=sys.stderr)
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python report_tiktok.py <video_url> <reason_text>")
        print("Example reasons: Spam, Harassment, Child endangerment, ...")
        sys.exit(1)

    video_url = sys.argv[1]
    reason_text = sys.argv[2]
    report_tiktok_video(video_url, reason_text)
