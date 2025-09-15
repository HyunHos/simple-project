from scraper import fetch_chrome_blog_titles

if __name__ == "__main__":
    print("Fetching latest Chrome blog titles using Selenium...")
    titles = fetch_chrome_blog_titles()
    
    if titles:
        print("\n--- Latest Posts ---")
        for i, title in enumerate(titles, 1):
            print(f"{i}. {title}")
        print("--------------------\n")
    else:
        print("Could not fetch titles.")

