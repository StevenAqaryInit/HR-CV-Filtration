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


phone_number = []
rate = []
no_rate = []
payment_method_list = []
categories_list = []
assortment_list = []
location_list = []
language_list = []
similar_companies_list = []


for res in responses:
    soup = BeautifulSoup(res)
    phone_number.append(soup.find_all('a', class_='_2lcm958')[-3]['href'])
    rate.append(soup.find_all('div', class_='_y10azs')[-1].text)
    no_rate.append(soup.find_all('div', class_='_jspzdm')[-1].text)
    payment_methods_section = soup.find('span', text='Payment methods')
    categories_section = soup.find('div', text='Categories')
    if payment_methods_section:
        payment_methods_div = payment_methods_section.find_next('div', class_='_49kxlr')
        payment_methods = payment_methods_div.find_all('span', class_='_er2xx9')
        payment_method = ''
        for method in payment_methods:
            payment_method += method.text.strip().replace('\u200b', ', ')
        payment_method = payment_method[2:]
    else:
        payment_method = "No payment methods found."
    payment_method_list.append(payment_method)
    
    if categories_section:
        category = categories_section.find_next('div', class_='_172gbf8')
        # print(category.text)
        # categories = category.find_all('span', class_='_oqoid')
        if category.text:
            categories_list.append(category.text.replace('\u200b', ' '))
        else:
            categories_list.append('')

    assortment = soup.find('div', class_='_49kxlr', text='Assortment')
    if assortment:
        assortment_list.append(assortment.find_next('span', class_='_14quei').text.replace('\u200b', ', ')[2:])
    else:
        assortment_list.append('')

    location_list.append(soup.find_all('div', class_='_1p8iqzw')[-1].text)

    service_language = soup.find('span', class_='_ikhcqkr', text='Service Language')
    if service_language:
        language = service_language.find_next('span', class_='_14quei')
        language_list.append(language.text.replace('\u200b', ', ')[2:])
    else:
        language_list.append('')

    similar_companies = soup.find_all('div', class_='_xcog5ug')
    company_str = ''
    for company in similar_companies:
        company_str += company.text + ', '

    similar_companies_list.append(company_str[:-2])


df['phone_number'] = phone_number
df['rate'] = rate
df['no_rate'] = no_rate
df['payment_method'] = payment_method_list
df['categories'] = categories_list
df['assortment'] = assortment_list
df['service_language'] = language_list
df['similar_companies'] = similar_companies_list
# df['location'] = location_list
df
