import os
import requests
from bs4 import BeautifulSoup
import time
import json
from dotenv import load_dotenv, dotenv_values
load_dotenv()

with open('config.json', 'r') as config_file:
        config = json.load(config_file)

KEYWORDS = config['keywords']
CHECK_INTERVAL = config['check_interval']
JOBS_FILE = 'previous_jobs.json'


def send_telegram_message(message):
        url = f"https://api.telegram.org/bot{os.getenv("BOT_TOKEN")}/sendMessage"
        payload= {
                "chat_id": os.getenv("CHAT_ID"),
                "text": message,
                "parse_mode": "HTML"
        }
        try:
                response = requests.post(url, json=payload)
                response.raise_for_status()
        except requests.RequestException as e:
                print(f"Error sending Telegram message: {e}")

        

def check_for_jobs(site):
    jobs_found = []
    try:
        response = requests.get(site['url'])
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        jobs_container = soup.find(site['container']['tag'], class_=site['container']['class'])
        job_links = jobs_container.find_all(site['job_link']['tag'], class_=site['job_link']['class'])

        for link in job_links:
            job_url = site['url'] + link['href']
            job_title = link.find(site['job_title']['tag'], class_=site['job_title']['class']).text.strip()
            lower_job_title = job_title.lower()

            if any(keyword in lower_job_title for keyword in KEYWORDS):
                jobs_found.append({
                    "title": job_title,
                    "url": job_url,
                    "site": site['name']
                })

    except requests.RequestException as e:
        print(f"Error fetching jobs from {site['name']}: {e}")
    except Exception as e:
        print(f"Error parsing jobs from {site['name']}: {e}")

    return jobs_found

def load_previous_jobs():
      try:
            with open(JOBS_FILE, 'r') as f:
                  return set(tuple(job.items()) for job in json.load(f))
      except FileNotFoundError:
            return set()
            
def save_current_jobs(jobs):
      with open(JOBS_FILE, 'w') as f:
            json.dump(list(dict(job) for job in jobs), f)


def main():

        all_new_jobs = []
        previous_jobs = load_previous_jobs()
        current_jobs = set()

        for site in config['sites']:
                site_jobs = check_for_jobs(site)
                site_jobs_set = set(tuple(job.items()) for job in site_jobs)
                new_jobs = site_jobs_set - previous_jobs
                all_new_jobs.extend(dict(job) for job in new_jobs)
                current_jobs.update(site_jobs_set)

        if all_new_jobs:
                message = "New Jobs Found:\n\n"
                for job in all_new_jobs:
                        message += f"<b>{job['title']}</b>\n"
                        message += f"<a href='{job['url']}'>Apply Here</a>\n\n"
        else:
                message = "No New Jobs With Your Keywords!"
        send_telegram_message(message)
        
        save_current_jobs(current_jobs)


if __name__ == "__main__":
    main()