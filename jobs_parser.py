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
                "text": message,
                "parse_mode": "HTML"
        }
        requests.post(url, json=payload)

def check_for_jobs():
        gev_yam_URL = "https://careers.gavyam-negev.co.il/"
        gev_yam_response = requests.get(gev_yam_URL).content.decode('utf-8')
        soup = BeautifulSoup(gev_yam_response, 'html.parser')
        jobs_container = soup.find('div', class_='container oe_website_jobs')
        job_links = jobs_container.find_all('a', class_='text-decoration-none')
        jobs_found = []

        for link in job_links:
                job_url = gev_yam_URL + link['href']
                job_title = link.find('h3', class_='text-secondary').text.strip()
                lower_job_title = job_title.lower()

                for keyword in KEYWORDS:
                        if keyword in lower_job_title:
                                jobs_found.append({
                                "title": job_title,
                                "url": job_url
                        })
                        break

        return jobs_found



def main():
        previous_jobs = set()

        current_jobs = set(tuple(job.items()) for job in check_for_jobs())
        new_jobs = current_jobs - previous_jobs

        if new_jobs:
                message = "New Jobs Found:\n\n"
                for job in new_jobs:
                        job_dict = dict(job)
                        message += f"<b>{job_dict['title']}</b>\n"
                        message += f"<a href='{job_dict['url']}'>Apply Here</a>\n\n"
                send_telegram_message(message)
                previous_jobs = current_jobs

                
if __name__ == "__main__":
    main()