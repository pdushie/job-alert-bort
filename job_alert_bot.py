
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# URL to monitor
URL = "https://jobs.novascotia.ca/search/?createNewAlert=false&q=csds&locationsearch="

# File to store previously seen jobs
STORAGE_FILE = "seen_jobs.json"

# Gmail credentials (use environment variables for security)
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# Function to fetch job postings
def fetch_jobs():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []
    for job_card in soup.select(".jobTitle a"):
        title = job_card.text.strip()
        link = "https://jobs.novascotia.ca" + job_card.get("href")
        jobs.append({"title": title, "link": link})
    return jobs

# Function to load previously seen jobs
def load_seen_jobs():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    return []

# Function to save current jobs
def save_jobs(jobs):
    with open(STORAGE_FILE, "w") as f:
        json.dump(jobs, f)

# Function to send email
def send_email(new_jobs):
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = "New CSDS Job Postings"

    body = "Here are the new job postings:

"
    for job in new_jobs:
        body += f"{job['title']}
{job['link']}

"

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)

# Main logic
current_jobs = fetch_jobs()
seen_jobs = load_seen_jobs()

# Detect new jobs
new_jobs = [job for job in current_jobs if job not in seen_jobs]

if new_jobs:
    send_email(new_jobs)
    save_jobs(current_jobs)
    print(f"Sent email with {len(new_jobs)} new jobs.")
else:
    print("No new jobs found.")
