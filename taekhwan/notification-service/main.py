import time
import os
from scraper import fetch_chrome_blog_posts

SEEN_POSTS_FILE = "seen_posts.txt"
# Check for new posts every hour. For testing, you can set this to a smaller value like 60 (1 minute).
CHECK_INTERVAL_SECONDS = 3600 

def load_seen_posts():
    """Loads seen post URLs from the file into a set."""
    if not os.path.exists(SEEN_POSTS_FILE):
        return set()
    with open(SEEN_POSTS_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def save_seen_post(url):
    """Appends a new seen post URL to the file."""
    with open(SEEN_POSTS_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")

if __name__ == "__main__":
    print("Starting notification service...")
    
    # On the first run, fetch all current posts and mark them as seen without notifying.
    print("Performing initial scan to set a baseline...")
    initial_posts = fetch_chrome_blog_posts()
    seen_posts = load_seen_posts()
    
    initial_new_posts = 0
    if initial_posts:
        # Iterate in reverse to add the oldest posts first
        for post in reversed(initial_posts):
            if post['url'] not in seen_posts:
                save_seen_post(post['url'])
                seen_posts.add(post['url'])
                initial_new_posts += 1
    
    if initial_new_posts > 0:
        print(f"Baseline established. Marked {initial_new_posts} posts as seen.")
    else:
        print("Baseline is up-to-date.")

    print(f"Will check for new posts every {CHECK_INTERVAL_SECONDS // 60} minutes.")
    print("--------------------")

    while True:
        print("Checking for new posts...")
        posts = fetch_chrome_blog_posts()
        seen_posts = load_seen_posts()
        new_post_found = False

        if posts:
            # The scraper gets the latest posts, so we check from oldest to newest (reversed list)
            # to ensure we notify in chronological order if multiple new posts appear.
            for post in reversed(posts):
                if post['url'] not in seen_posts:
                    new_post_found = True
                    print(f"\n✨ New Post Found! ✨")
                    print(f"  Title: {post['title']}")
                    print(f"  URL: {post['url']}\n")
                    save_seen_post(post['url'])
        
        if not new_post_found:
            print("No new posts found.")

        print(f"Waiting for {CHECK_INTERVAL_SECONDS // 60} minutes until the next check...")
        time.sleep(CHECK_INTERVAL_SECONDS)

