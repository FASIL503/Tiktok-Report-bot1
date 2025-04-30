import requests

def report_tiktok_video(video_id: str, referer: str):
    session = requests.Session()
    # You must visit TikTok in-session to get fresh cookies and csrf
    session.get("https://www.tiktok.com", headers={
        "User-Agent": "Mozilla/5.0"
    })
    # Extract csrf token from cookies
    csrf = session.cookies.get("tt_csrf_token")
    if not csrf:
        raise RuntimeError("Failed to get CSRF token")

    url = "https://www.tiktok.com/node/report/reasons_put"
    payload = {
        "reason": 1004,
        "object_id": video_id,
        "owner_id": "6636714219386781701",
        "report_type": "video"
    }
    headers = {
        "Content-Type": "application/json",
        "tt-csrf-token": csrf,
        "Referer": referer,
        "User-Agent": "Mozilla/5.0"
    }

    resp = session.post(url, json=payload, headers=headers)
    try:
        data = resp.json()
    except ValueError:
        print("Non-JSON response:", resp.text)
        return

    if data.get("status_code") == 0:
        print("Report submitted successfully!")
    else:
        print("Error reporting video:", data)

if __name__ == "__main__":
    vid = input("Enter TikTok Video ID: ").strip()
    ref = input("Enter full TikTok video URL (for Referer header): ").strip()
    report_tiktok_video(vid, ref)
