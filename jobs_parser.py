import os
import requests
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv, dotenv_values
KEYWORDS = ["junior", "student", "intern"]
CHECK_INTERVAL = 86400 
load_dotenv()

def send_telegram_message(message):
        url = f"https://api.telegram.org/bot{os.getenv("BOT_TOKEN")}/sendMessage"
        payload= {
                "chat_id": os.getenv("CHAT_ID"),
                "text": message
        }
        requests.post(url, json=payload)

def check_for_jobs():
        gev_yam_URL = "https://careers.gavyam-negev.co.il/"
        gev_yam_response = requests.get(gev_yam_URL).content.decode('utf-8')
        soup = BeautifulSoup(gev_yam_response, 'html.parser')
        jobs = soup.find_all('h3', attrs={'class': 'text-secondary mt0 mb4'})
        jobs_found = []

        for job in jobs:
                lower_job_text = job.text.strip().lower()
                for keyword in KEYWORDS:
                        if keyword in lower_job_text:
                                jobs_found.append(job.text.strip())
                                break;
        return jobs_found



def main():
        previous_jobs = set()
      
        current_jobs = set(check_for_jobs())
        new_jobs = current_jobs - previous_jobs

        if new_jobs:
                message = "New Jobs Found:\n\n" + "\n".join(new_jobs)
                send_telegram_message(message)
                previous_jobs = current_jobs
                

if __name__ == "__main__":
        main()