import os
import re
import json
import base64
import requests
import feedparser
from bs4 import BeautifulSoup
from urllib.parse import urlparse

import config
import database

# Initialize database
database.init_db()

# Default fallback images if original article has none
FALLBACK_IMAGES = {
    "उत्तराखंड": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=1080&auto=format&fit=crop&q=80",
    "रोजगार व शिक्षा": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?w=1080&auto=format&fit=crop&q=80",
    "सरकारी योजनाएं": "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=1080&auto=format&fit=crop&q=80",
    "टेक न्यूज़": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1080&auto=format&fit=crop&q=80",
    "default": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1080&auto=format&fit=crop&q=80"
}

def get_auth_headers():
    """Generates Basic Auth header for WordPress REST API"""
    credentials = f"{config.WP_USERNAME}:{config.WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode("utf-8")
    return {
        "Authorization": f"Basic {token}"
    }

def extract_image_url(entry, article_link: str) -> str:
    """Extracts image URL from RSS media tags or scrapes og:image from the article"""
    # 1. Check media:content or media_thumbnail in RSS entry
    if "media_content" in entry and len(entry.media_content) > 0:
        return entry.media_content[0].get("url", "")
    if "media_thumbnail" in entry and len(entry.media_thumbnail) > 0:
        return entry.media_thumbnail[0].get("url", "")
    if "enclosures" in entry and len(entry.enclosures) > 0:
        return entry.enclosures[0].get("href", "")

    # 2. Check html content of the entry for <img> tag
    raw_html = entry.get("summary", "") or entry.get("description", "")
    if raw_html:
        soup = BeautifulSoup(raw_html, "html.parser")
        img = soup.find("img")
        if img and img.get("src"):
            return img.get("src")

    # 3. Scrape og:image from the destination page
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(article_link, headers=headers, timeout=6)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            og_img = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "twitter:image"})
            if og_img and og_img.get("content"):
                return og_img.get("content")
    except Exception:
        pass

    return ""

def rewrite_with_gemini(original_title: str, summary: str, category: str) -> dict:
    """Uses Google's Free Gemini API to rewrite news into high-quality SEO Hindi format"""
    if not config.GEMINI_API_KEY:
        print("[!] ERROR: GEMINI_API_KEY is not set in your .env file.")
        return None

    # Prompt designed specifically for AdSense compliance, high Google Discover CTR, and organic SEO
    prompt = f"""
आप 'नया उत्तराखंड' (Hindi News Portal) के सीनियर न्यूज़ एडिटर और SEO विशेषज्ञ हैं।
नीचे दी गई ताज़ा खबर का विवरण पढ़ें और इसे 100% मौलिक, प्रामाणिक और आकर्षक हिंदी न्यूज़ आर्टिकल में पुनः लिखें (Rewrite करें)।

मूल शीर्षक: {original_title}
कैटेगरी: {category}
मूल विवरण / सारांश: {summary}

निर्देश (Strict Guidelines):
1. भाषा: शुद्ध, सरल और पठनीय आधुनिक हिंदी।
2. SEO Title: 60-70 अक्षरों का क्लिक-योग्य (Non-clickbait), आकर्षक और सर्च-फ्रेंडली शीर्षक।
3. Content Format:
   - शुरुआत में 2-3 वाक्यों का मजबूत इंट्रोडक्टरी पैराग्राफ।
   - एक 'प्रमुख बिंदु (Key Highlights)' बॉक्स (HTML <ul> बुलेट पॉइंट्स में)।
   - 2 या 3 सब-हेडिंग्स (<h2> और <h3> टैग्स का इस्तेमाल करें) के साथ विस्तृत जानकारी।
   - महत्वपूर्ण तिथियां, पात्रता या आवश्यक निर्देश (यदि लागू हो)।
   - अंत में एक संक्षिप्त निष्कर्ष / सलाह।
4. AdSense & Google Policy Friendly: कोई भ्रामक दावा या कॉपी-पेस्ट नहीं।
5. Output को केवल और केवल वैध JSON फॉर्मेट में दें, कोई अतिरिक्त टेक्स्ट या बैक-टिक्स (```json) न लगाएं:
{{
  "title": "आकर्षक हिंदी शीर्षक",
  "content_html": "<p>पहला पैराग्राफ...</p><h3>मुख्य बिंदु:</h3><ul><li>...</li></ul><h2>विस्तृत खबर...</h2><p>...</p>",
  "meta_description": "140-160 शब्दों का संक्षिप्त SEO विवरण",
  "tags": ["टैग 1", "टैग 2", "टैग 3", "टैग 4"]
}}
"""

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={config.GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.5,
            "responseMimeType": "application/json"
        }
    }

    try:
        response = requests.post(api_url, json=payload, timeout=25)
        # If gemini-2.5-flash is not available, fallback to gemini-1.5-flash
        if response.status_code != 200:
            fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={config.GEMINI_API_KEY}"
            response = requests.post(fallback_url, json=payload, timeout=25)

        if response.status_code == 200:
            data = response.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            # Clean possible markdown wrap
            raw_text = re.sub(r"^```json\s*", "", raw_text)
            raw_text = re.sub(r"\s*```$", "", raw_text)
            return json.loads(raw_text)
        else:
            print(f"[-] Gemini API Error ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"[-] Error during Gemini rewrite: {e}")
    
    return None

def upload_image_to_wordpress(image_url: str, title: str, category: str) -> int:
    """Downloads the article image and uploads it to WordPress Media Library"""
    if not image_url or not image_url.startswith("http"):
        image_url = FALLBACK_IMAGES.get(category, FALLBACK_IMAGES["default"])

    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        img_resp = requests.get(image_url, headers=headers, timeout=10)
        if img_resp.status_code != 200:
            # Try fallback
            img_resp = requests.get(FALLBACK_IMAGES["default"], timeout=10)

        image_data = img_resp.content
        filename = f"news-{int(requests.utils.time.time())}.jpg"

        upload_url = f"{config.WP_URL}/wp-json/wp/v2/media"
        wp_headers = get_auth_headers()
        wp_headers.update({
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "image/jpeg"
        })

        res = requests.post(upload_url, data=image_data, headers=wp_headers, timeout=20)
        if res.status_code in [200, 201]:
            media_id = res.json().get("id")
            # Update Alt text and Title
            requests.post(
                f"{upload_url}/{media_id}",
                headers=get_auth_headers(),
                json={"alt_text": title, "title": title},
                timeout=10
            )
            return media_id
        else:
            print(f"[-] Failed to upload image to WP ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"[-] Error uploading image to WP: {e}")

    return 0

def get_or_create_category(category_name: str) -> int:
    """Gets the WordPress category ID, or creates it if it does not exist"""
    cat_url = f"{config.WP_URL}/wp-json/wp/v2/categories"
    try:
        # Search existing
        res = requests.get(f"{cat_url}?search={category_name}", headers=get_auth_headers(), timeout=10)
        if res.status_code == 200 and len(res.json()) > 0:
            for cat in res.json():
                if cat.get("name") == category_name:
                    return cat.get("id")

        # Create if not found
        create_res = requests.post(cat_url, headers=get_auth_headers(), json={"name": category_name}, timeout=10)
        if create_res.status_code in [200, 201]:
            return create_res.json().get("id")
    except Exception as e:
        print(f"[-] Error fetching/creating category: {e}")

    return 1 # Default Uncategorized

def get_or_create_tags(tag_names: list) -> list:
    """Gets or creates WordPress tag IDs for SEO tagging"""
    tag_ids = []
    tags_url = f"{config.WP_URL}/wp-json/wp/v2/tags"
    auth = get_auth_headers()

    for name in tag_names[:5]:
        name = name.strip()
        if not name:
            continue
        try:
            res = requests.get(f"{tags_url}?search={name}", headers=auth, timeout=8)
            if res.status_code == 200 and len(res.json()) > 0:
                tag_ids.append(res.json()[0]["id"])
            else:
                create_res = requests.post(tags_url, headers=auth, json={"name": name}, timeout=8)
                if create_res.status_code in [200, 201]:
                    tag_ids.append(create_res.json()["id"])
        except Exception:
            continue
    return tag_ids

def publish_to_wordpress(article_data: dict, media_id: int, category_id: int, tag_ids: list) -> int:
    """Publishes the rewritten article to WordPress via REST API"""
    posts_url = f"{config.WP_URL}/wp-json/wp/v2/posts"
    payload = {
        "title": article_data["title"],
        "content": article_data["content_html"],
        "excerpt": article_data.get("meta_description", ""),
        "status": config.POST_STATUS,
        "categories": [category_id] if category_id else [],
        "tags": tag_ids if tag_ids else []
    }
    if media_id:
        payload["featured_media"] = media_id

    try:
        res = requests.post(posts_url, headers=get_auth_headers(), json=payload, timeout=20)
        if res.status_code in [200, 201]:
            post = res.json()
            print(f"[+] SUCCESS: Published post ID {post.get('id')} -> {post.get('link')}")
            return post.get("id")
        else:
            print(f"[-] Failed to publish post ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"[-] Error publishing post: {e}")

    return 0

def run_agent():
    """Main execution loop for the news auto-publisher"""
    print("=" * 60)
    print("🚀 Starting 'Naya Uttarakhand' AI News Publisher Agent...")
    print(f"Site Target: {config.WP_URL}")
    print(f"Post Status: {config.POST_STATUS}")
    print("=" * 60)

    if not config.WP_USERNAME or not config.WP_APP_PASSWORD:
        print("[!] Please configure WP_USERNAME and WP_APP_PASSWORD in your .env file.")
        return

    if not config.GEMINI_API_KEY:
        print("[!] Please configure GEMINI_API_KEY in your .env file.")
        return

    articles_published_this_run = 0

    for feed_info in config.RSS_FEEDS:
        if articles_published_this_run >= config.MAX_ARTICLES_PER_RUN:
            print(f"[*] Reached limit of {config.MAX_ARTICLES_PER_RUN} articles for this run.")
            break

        category = feed_info["category"]
        feed_url = feed_info["url"]
        print(f"\n[>] Checking feed for category '{category}'...")

        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            print(f"[-] Could not parse feed {feed_url}: {e}")
            continue

        for entry in feed.entries:
            if articles_published_this_run >= config.MAX_ARTICLES_PER_RUN:
                break

            orig_link = entry.get("link", "")
            orig_title = entry.get("title", "")
            summary = entry.get("summary", "") or entry.get("description", "")

            # Check duplicate database
            if database.is_article_processed(orig_link):
                continue

            print(f"\n[*] Found new article: {orig_title[:60]}...")
            print("[1/4] Rewriting article with Gemini AI in Hindi...")
            rewritten = rewrite_with_gemini(orig_title, summary, category)
            if not rewritten:
                continue

            print(f"[2/4] New SEO Title: {rewritten['title']}")
            print("[3/4] Finding and uploading featured image...")
            image_url = extract_image_url(entry, orig_link)
            media_id = upload_image_to_wordpress(image_url, rewritten["title"], category)

            print("[4/4] Publishing to WordPress...")
            category_id = get_or_create_category(category)
            tag_ids = get_or_create_tags(rewritten.get("tags", []))
            post_id = publish_to_wordpress(rewritten, media_id, category_id, tag_ids)

            if post_id:
                database.record_processed_article(orig_link, orig_title, rewritten["title"], post_id)
                articles_published_this_run += 1
                print(f"[✓] Article completed! Total published in this run: {articles_published_this_run}")

    print("\n" + "=" * 60)
    print(f"✨ Run finished. Total new articles published: {articles_published_this_run}")
    print("=" * 60)

if __name__ == "__main__":
    run_agent()
