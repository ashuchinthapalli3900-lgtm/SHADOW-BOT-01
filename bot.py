import os
import instaloader
import requests
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv('WEBHOOK_URL')
USERNAME = 'dragon___up'

L = instaloader.Instaloader()
LAST_POST_FILE = 'last_post.txt'

def get_last_shortcode():
    try:
        with open(LAST_POST_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_last_shortcode(shortcode):
    with open(LAST_POST_FILE, 'w') as f:
        f.write(shortcode)

def check_instagram():
    try:
        profile = instaloader.Profile.from_username(L.context, USERNAME)
        posts = list(profile.get_posts())
        if posts:
            latest = posts[0]
            return latest.shortcode
    except Exception as e:
        print(f"Error checking Instagram: {e}")
    return None

def main():
    latest_shortcode = check_instagram()
    if latest_shortcode:
        last_shortcode = get_last_shortcode()
        if latest_shortcode != last_shortcode:
            link = f"https://www.instagram.com/p/{latest_shortcode}/"
            if WEBHOOK_URL:
                response = requests.post(WEBHOOK_URL, json={"content": link})
                if response.status_code == 204:
                    print("Message sent to Discord")
                    save_last_shortcode(latest_shortcode)
                else:
                    print(f"Failed to send message: {response.status_code}")
            else:
                print("WEBHOOK_URL not set")
        else:
            print("No new post")
    else:
        print("No posts found")

if __name__ == "__main__":
    main()