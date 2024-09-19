import os
import requests
from bs4 import BeautifulSoup
import time
from plyer import notification

URL = "https://careers.gavyam-negev.co.il/"
KEYWORDS = ["junior", "student", "intern"]
CHECK_INTERVAL = 86400 
response = requests.get(URL).content.decode('utf-8')
soup = BeautifulSoup(response, 'html.parser')
jobs = soup.find_all('h3', attrs={'class': 'text-secondary mt0 mb4'})

for job in jobs:
    print(job.text.strip() + "\n")