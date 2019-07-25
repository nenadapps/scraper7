from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
from time import sleep
from urllib.request import Request
from urllib.request import urlopen

def get_html(url):
    html_content = ''
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html_page = urlopen(req).read()
        html_content = BeautifulSoup(html_page, "html.parser")
    except: 
        pass

    return html_content

def get_countries(url):
    items = []
    try:
        html = get_html(url)
        country_items = html.select('.box-wrapper a')
        for country_item in country_items:
            item = 'https://www.sandafayre.com' + country_item.get('href')
            items.append(item)
    except: 
        pass

    return items

def get_page_items(url):

    items = []
    next_url = ''
    country_name = ''

    try:
        html = get_html(url)
    except:
        return items, next_url

    try:
        country_name_temp = html.select(".container h1")[0].get_text()
        country_name_parts = country_name_temp.split("|")
        country_name = country_name_parts[0].replace(" STAMPS", "").strip()
    except:
        pass

    try:
        for item in html.select('.auction-lot-title a'):
            item = 'https://www.sandafayre.com' + item.get('href')
            items.append(item)
    except: 
        pass


    try:
        next_url = html.find_all('link', attrs={'rel': 'next'})[0].get('href')
        next_url = 'https://www.sandafayre.com' + next_url.replace('&amp;', '&')
    except:
        pass

    shuffle(items)

    return items, next_url, country_name

def get_details(url, country_name):

    stamp = {}
    
    try:
        html = get_html(url)
    except:
        return stamp

    try:
        price = html.select('.estimate strong')[0].get_text()
        price = price.replace('Estimate', '').strip()
        price = price.replace('£', '').strip()
        stamp['price_est'] = price
    except:
        stamp['price_est'] = None

    try:
        name = html.find_all("h1", {"class":"lot-title"})[0].find_next('p').get_text().strip()
        stamp['name'] = name
    except:
        stamp['name'] = None

    stamp['country'] = country_name

    stamp['currency'] = 'GBP'

    # image_urls should be a list
    images = []
    try:
        image_items = html.find_all('img', {'id': 'lot-image'})
        for image_item in image_items:
            img = image_item.get('src').split('-medium.jpg')
            img = 'https://www.sandafayre.com' + img[0] + '.jpg'
            images.append(img)
    except:
        pass

    stamp['image_urls'] = images 

    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date

    print(stamp)
    print('+++++++++++++')
    sleep(randint(22, 99))

    return stamp

# start url
start_url = 'https://www.sandafayre.com/all-countries'

# loop through all countries
countries = get_countries(start_url)
for country in countries:
    while(country):
        page_items, country, country_name = get_page_items(country)
        # loop through all items on current page
        for page_item in page_items:
            stamp = get_details(page_item, country_name) 