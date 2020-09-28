import os
from fake_useragent import UserAgent


API_TOKEN = os.environ["API_TOKEN"]

url = "https://777score.ru/live"
headers = {"User-Agent": UserAgent().chrome}




