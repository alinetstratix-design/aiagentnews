import os
from dotenv import load_dotenv

load_dotenv()

# WordPress Credentials
WP_URL = os.getenv("WP_URL", "https://news.codevoraai.com").rstrip("/")
WP_USERNAME = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")

# 100% Free Gemini API Key from Google AI Studio (https://aistudio.google.com/)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Post Status: 'publish' to go live immediately, or 'draft' for review
POST_STATUS = os.getenv("POST_STATUS", "publish")

# Maximum articles to process per run (keeps API usage safe within free tier)
MAX_ARTICLES_PER_RUN = int(os.getenv("MAX_ARTICLES_PER_RUN", "3"))

# RSS Feeds curated specifically for "नया उत्तराखंड"
RSS_FEEDS = [
    {
        "category": "उत्तराखंड",
        "url": "https://news.google.com/rss/search?q=Uttarakhand+news+when:1d&hl=hi&gl=IN&ceid=IN:hi"
    },
    {
        "category": "रोजगार व शिक्षा",
        "url": "https://news.google.com/rss/search?q=UKSSSC+UKPSC+bharti+result+when:2d&hl=hi&gl=IN&ceid=IN:hi"
    },
    {
        "category": "सरकारी योजनाएं",
        "url": "https://news.google.com/rss/search?q=sarkari+yojana+uttarakhand+when:3d&hl=hi&gl=IN&ceid=IN:hi"
    },
    {
        "category": "टेक न्यूज़",
        "url": "https://news.google.com/rss/search?q=Technology+AI+news+when:1d&hl=hi&gl=IN&ceid=IN:hi"
    }
]
