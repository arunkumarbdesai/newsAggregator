import os
import smtplib
import urllib.request
import xml.etree.ElementTree as ET
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json

# 1. Fetch RSS Feeds
FEEDS = [
    "https://news.ycombinator.com/rss",
    "https://techcrunch.com/feed/"
]

def get_headlines():
    raw_data = ""
    for url in FEEDS:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                root = ET.fromstring(response.read())
                for item in root.findall('.//item'):
                    title = item.find('title').text
                    link = item.find('link').text
                    raw_data += f"Title: {title}\nLink: {link}\n\n"
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    return raw_data

# 2. Generate AI Summary (Using Google Gemini API as an example)
def summarize_with_ai(content):
    api_key = os.environ["GEMINI_API_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompt = f"Summarize the following tech news into a sharp, scannable briefing with 3 sections: Global/Macro, Tech Launches, and Core Software Engineering trends. Use HTML formatting (bolding, lists, headers). Do not include markdown fences like ```html.\n\n{content}"
    
    data = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode('utf-8'))
        return res['candidates'][0]['content']['parts'][0]['text']

# 3. Send Email via SMTP
def send_email(html_content):
    sender = os.environ["EMAIL_SENDER"]
    password = os.environ["EMAIL_PASSWORD"]
    receiver = os.environ["EMAIL_RECEIVER"]
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Your Daily Tech & Engineering Briefing"
    msg['From'] = sender
    msg['To'] = receiver
    
    msg.attach(MIMEText(html_content, 'html'))
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())

if __name__ == "__main__":
    print("Fetching feeds...")
    headlines = get_headlines()
    print("Generating summary...")
    summary = summarize_with_ai(headlines)
    print("Sending email...")
    send_email(summary)
    print("Done!")
