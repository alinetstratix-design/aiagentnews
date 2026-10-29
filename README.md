# 📰 Naya Uttarakhand - Automated AI News Publisher Agent

यह एक स्वचालित (Automated) AI News Publishing Agent है जिसे विशेष रूप से **[news.codevoraai.com](https://news.codevoraai.com/)** के लिए डिज़ाइन किया गया है।

---

## 🌟 मुख्य विशेषताएं (Key Features)

1. **100% मुफ़्त AI (No Paid API Needed)**: Google के आधिकारिक **Gemini API (Free Tier)** का उपयोग करता है (Google AI Studio से बिल्कुल फ़्री)।
2. **Organic SEO & AdSense Compliant**:
   - मूल खबर को 100% मौलिक और आकर्षक हिंदी में दोबारा लिखता है (No plagiarism).
   - सही HTML स्ट्रक्चर (`<h2>`, `<h3>`, बुलेट पॉइंट्स, मुख्य बिंदु).
   - आकर्षक और क्लिक-योग्य SEO टाइटल्स।
   - सर्च इंजन के लिए ऑटोमैटिक Meta Description व Tags।
3. **Auto Image Handler**:
   - RSS फीड या सोर्स आर्टिकल से ओरिजिनल इमेज निकालता है।
   - WordPress Media Library में ऑटोमैटिक अपलोड करके **Featured Image** सेट करता है।
4. **Duplicate Prevention**: SQLite डेटाबेस (`processed_news.db`) में सभी पब्लिश की गई खबरों का रिकॉर्ड रखता है ताकि कोई भी खबर दोबारा पोस्ट न हो।
5. **24/7 Cloud Automation**: GitHub Actions के ज़रिए बिना कंप्यूटर चालू रखे 24 घंटे ऑटोमैटिक चला सकते हैं।

---

## 🛠️ त्वरित सेटअप (Quick Setup)

### 1. Free Gemini API Key प्राप्त करें (2 मिनट)
1. **[https://aistudio.google.com/](https://aistudio.google.com/)** पर जाएं।
2. अपने Google खाते से साइन इन करें।
3. **"Get API key"** पर क्लिक करें और **"Create API key"** चुनें।
4. अपनी फ़्री API Key कॉपी कर लें।

### 2. WordPress Application Password प्राप्त करें (1 मिनट)
1. अपने वर्डप्रेस एडमिन प्रोफाइल पर जाएं:
   👉 `https://news.codevoraai.com/wp-admin/profile.php`
2. नीचे स्क्रॉल करके **"Application Passwords"** सेक्शन पर जाएं।
3. नाम में `NewsAgent` लिखें और **"Add New Application Password"** पर क्लिक करें।
4. जनरेट हुआ 24-अक्षरों का पासवर्ड कॉपी कर लें।

### 3. कॉन्फ़िगरेशन (.env फ़ाइल)
`.env.example` की एक कॉपी बनाकर उसका नाम `.env` रखें और अपनी डिटेल्स भरें:
```env
WP_URL=https://news.codevoraai.com
WP_USERNAME=your_admin_email_or_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
GEMINI_API_KEY=AIzaSy...your_gemini_api_key...
POST_STATUS=publish
MAX_ARTICLES_PER_RUN=3
```

---

## 🚀 लोकल कंप्यूटर पर कैसे चलाएं (How to Run Locally)

```bash
# 1. प्रोजेक्ट डायरेक्टरी में जाएं
cd C:\Users\HP_EliteBook\.gemini\antigravity-ide\scratch\news-ai-agent

# 2. आवश्यक पैकेज इंस्टॉल करें
pip install -r requirements.txt

# 3. एजेंट को चलाएं
python agent.py
```

---

## ☁️ 24/7 मुफ़्त में ऑटोमेशन कैसे सेट करें (GitHub Actions)
अगर आप चाहते हैं कि आपका कंप्यूटर बंद रहने पर भी हर 2 घंटे में ताज़ा खबरें अपने आप पब्लिश होती रहें:
1. इस पूरे फोल्डर को अपने **GitHub** के किसी **Private Repository** में पुश करें।
2. GitHub Repository में **Settings** > **Secrets and variables** > **Actions** पर जाएं।
3. **Repository secrets** जोड़ें:
   - `WP_URL` : `https://news.codevoraai.com`
   - `WP_USERNAME` : आपका वर्डप्रेस यूज़रनेम
   - `WP_APP_PASSWORD` : आपका 24-अक्षरों का Application Password
   - `GEMINI_API_KEY` : आपकी फ़्री Gemini API Key
4. `.github/workflows/auto_news_bot.yml` फ़ाइल हर 2 घंटे में यह स्क्रिप्ट ऑटोमैटिक चलाएगी!

---

## 💰 AdSense & Organic Traffic Tips
1. **Quality over Quantity**: दिन में 10 से 15 बेहतरीन, अच्छी तरह फॉर्मेटेड आर्टिकल्स पब्लिश करें।
2. **Google Discover**: हाई-रेज़ोल्यूशन इमेजेस (कम से कम 1200px चौड़ी) Google Discover में तेज़ी से आती हैं।
3. **Google Search Console**: अपनी `wp-sitemap.xml` को Search Console में सबमिट रखें ताकि नया आर्टिकल पब्लिश होते ही 10 मिनट में इंडेक्स हो जाए।
