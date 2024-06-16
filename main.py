from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import requests
import json
from bs4 import BeautifulSoup
from time import sleep

# commands
# cd NewsAIScraper
# scraper\Scripts\activate
# python main.py

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)

df = pd.read_csv("newswebsites.csv")
websites = df['Website'].to_list()
filtered_websites = df[df['AI Usage'].isnull()]['Website'].to_list()

print(len(filtered_websites))

current_links = []
current_images = []
uses_AI = False

try:
    # 1841 websites to scrape
    for website in filtered_websites[1010:1020]:
        driver.get(website)
        links = driver.find_elements(By.TAG_NAME, "a")
    
        for link in links:
            if link is not None:
                src = link.get_attribute("href")
                if src:
                    stripped_src = src.strip()
                    if stripped_src:
                        current_links.append(stripped_src)

        for curr_l in current_links:
            driver.get(curr_l)
            images = driver.find_elements(By.TAG_NAME, "img")

            for image in images:
                src = image.get_attribute("src")
                if src and src not in current_images:
                    current_images.append(src)
            
            for curr_i in current_images:
                params = {
                    'url': curr_i,
                    'models': 'genai',
                    'api_user': '<API_USER>',
                    'api_secret': '<API_SECRET>'
                }
                try:
                    r = requests.get('https://api.sightengine.com/1.0/check.json', params=params)
                    output = json.loads(r.text)
                except:
                    output = None
                print('o ',output)
                if output and output['status'] == "success":
                    if output['type']['ai_generated'] > 0.5:
                        print("Ai generated image detected")
                        uses_AI = True
                        break
                    else:
                        print("Real image")
            
            current_images = []

            if uses_AI:
                break
        
        idx = websites.index(website)
        df.loc[idx, 'AI Usage'] = uses_AI
        
        uses_AI = False
        current_links = []

    df.to_csv("newswebsites.csv")
except KeyboardInterrupt:
    print("ended")
    df.to_csv("newswebsites.csv")

