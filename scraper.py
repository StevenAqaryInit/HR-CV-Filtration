import requests
from bs4 import BeautifulSoup
import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd


# Define the URL of the website to scrape
responses = []
for i in range(1, 7):
    url = f'https://2gis.ae/dubai/search/Eat%20out/page/{i}'
    print(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    scraper = cloudscraper.create_scraper(browser={
            'custom': 'ScraperBot/1.0',
        })
    responses.append(scraper.get(url).text)



names = []
locations = []
links = []
for response in responses:
    soup = BeautifulSoup(response)
    names.append(soup.find_all('span', class_='_1cd6avd'))
    locations.append(soup.find_all('span', class_='_14quei'))
    links.append(soup.find_all('a', class_='_1rehek'))


text_name = []
text_location = []
links_list = []
for name_lst, loc_lst, link_list in zip(names, locations, links):
    text_name.extend([name.text.strip() for name in name_lst])
    text_location.extend([loc.text.replace('\u200b', '').replace('\xa0', ' ') for loc in loc_lst])
    links_list.extend([link['href'][len('/dubai'):] for link in link_list if link['href'].startswith('/dubai/firm')])



df = pd.DataFrame(columns=['restaurent_name', 'location', 'links'])
df['restaurent_name'] = text_name
df['location'] = text_location
df['links'] = links_list



responses = []
for link in df['links'].values:
    url = f'https://2gis.ae/dubai/search/Eat%20out'+link
    print(url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    scraper = cloudscraper.create_scraper(browser={
            'custom': 'ScraperBot/1.0',
        })
    responses.append(scraper.get(url).text)
