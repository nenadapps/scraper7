# sandafayre
from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
from time import sleep
from urllib.request import Request
from urllib.request import urlopen
'''
import requests
from fake_useragent import UserAgent
import sqlite3
import os
import shutil
from stem import Signal
from stem.control import Controller
import socket
import socks

controller = Controller.from_port(port=9051)
controller.authenticate()

UA = UserAgent(fallback='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
hdr = {'User-Agent': "'"+UA.random+"'",
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8'}

def connectTor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5 , "127.0.0.1", 9150)
    socket.socket = socks.socksocket

def renew_tor():
    controller.signal(Signal.NEWNYM)

def showmyip():
    url = "http://www.showmyip.gr/"
    r = requests.Session()
    page = r.get(url)
    soup = bs4.BeautifulSoup(page.content, "lxml")
    try:
        ip_address = soup.find("span",{"class":"ip_address"}).text.strip()
        print(ip_address)
    except:
        print('Issue with printing IP')
'''        
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
    shuffle(list(set(items)))
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

    shuffle(list(set(items)))

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
        stamp['raw_text'] = name.replace('"',"'")
    except:
        stamp['raw_text'] = None
    
    try:
    	temp = stamp['raw_text'].split(' ')
    	stamp['year']=temp[2]
    except:
    	stamp['year']=None

    stamp['country'] = country_name

    stamp['currency'] = 'GBP'

    # image_urls should be a list
    images = []
    try:
        if html.select('#lotGallery'):
            image_items = html.select('#lotGallery li img')
        else:    
            image_items = html.select('#lot-image')
            
        for image_item in image_items:
            img_src = image_item.get('src')
            if '-medium.jpg' in img_src:
                img_parts = img_src.split('-medium.jpg')
            else:
                img_parts = img_src.split('-small.jpg')
            img = 'https://www.sandafayre.com' + img_parts[0] + '.jpg'
            images.append(img)
    except:
        pass

    stamp['image_urls'] = images 

    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date
    stamp['url']=url

    print(stamp)
    print('+++++++++++++')
    sleep(randint(45, 125))

    return stamp
'''
def file_names(stamp):
    file_name = []
    rand_string = "RAND_"+str(randint(0,100000))
    file_name = [rand_string+"-" + str(i) + ".png" for i in range(len(stamp['image_urls']))]
    return(file_name)

def query_for_previous(stamp):
    # CHECKING IF Stamp IN DB
    os.chdir("/Volumes/Stamps/")
    conn1 = sqlite3.connect('Reference_data.db')
    c = conn1.cursor()
    col_nm = 'url'
    col_nm2 = 'raw_text'
    unique = stamp['url']
    unique2 = stamp['raw_text']
    c.execute('SELECT * FROM sandafayre WHERE "{cn}" LIKE "{un}%" AND "{cn2}" LIKE "{un2}%"'.format(cn=col_nm, cn2=col_nm2, un=unique, un2=unique2))
    all_rows = c.fetchall()
    conn1.close()
    
    if len(all_rows) > 0:
        print ("This is in the database already")
        sleep(randint(10,25))
        next_step='continue'
        pass
    else:
        next_step='pass'
    return (next_step)
    
def db_update_image_download(stamp):  
    req = requests.Session()
    directory = "/Volumes/Stamps/stamps/sandafayre/" + str(datetime.datetime.today().strftime('%Y-%m-%d')) +"/"
    image_paths = []
    f_names = file_names(stamp)
    image_paths = [directory + f_names[i] for i in range(len(f_names))]
    print("image paths", image_paths)
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    for item in range(0,len(f_names)):
        print (stamp['image_urls'][item])
        try:
            imgRequest1=req.get(stamp['image_urls'][item],headers=hdr, timeout=60, stream=True)
        except:
            print ("waiting...")
            sleep(randint(3000,6000))
            print ("...")
            imgRequest1=req.get(stamp['image_urls'][item], headers=hdr, timeout=60, stream=True)
        if imgRequest1.status_code==200:
            with open(f_names[item],'wb') as localFile:
                imgRequest1.raw.decode_content = True
                shutil.copyfileobj(imgRequest1.raw, localFile)
                sleep(randint(18,30))
    stamp['image_paths']=", ".join(image_paths)
    #url_count += len(image_paths)
    database_update =[]

    # PUTTING NEW STAMPS IN DB
    database_update.append((
        stamp['url'],
        stamp['raw_text'],
        stamp['country'],
        stamp['price_est'],
        stamp['currency'],
        stamp['scrape_date'],
        stamp['image_paths']))
    os.chdir("/Volumes/Stamps/")
    conn = sqlite3.connect('Reference_data.db')
    conn.text_factory = str
    cur = conn.cursor()
    cur.executemany("""INSERT INTO sandafayre ('url','raw_text', 'country', 'price_est',
    'currency', 'scrape_date','image_paths') VALUES (?, ?, ?, ?, ?, ?, ?)""", database_update)
    conn.commit()
    conn.close()
    print ("all updated")
    print ("++++++++++++")
    print (" ")
    sleep(randint(45,115))


connectTor()
req = requests.Session()
'''
count = 0
# start url
start_url = 'https://www.sandafayre.com/all-countries'

# loop through all countries
countries = get_countries(start_url)
shuffle(list(set(countries)))
for country in countries:
    while(country):
        page_items, country, country_name = get_page_items(country)
        # loop through all items on current page
        shuffle(list(set(page_items)))
        for page_item in page_items:
        	count += 1
        	if count > randint(75,156):
        		sleep(randint(500,2000))
        		#connectTor()
        		#showmyip()
        		count = 0
        	else:
        		pass
        	stamp = get_details(page_item, country_name)
        	'''
        	next_step = query_for_previous(stamp)
        	if next_step == 'continue':
        		print('Only updating price')
        		continue
        	elif next_step == 'pass':
        		print('Inserting the item')
        		pass
        	else:
        		break
        	db_update_image_download(stamp)
        	'''