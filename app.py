import requests
from bs4 import BeautifulSoup
import re
import time
import random
import json
import datetime

URL = 'https://www.avito.ru/krasnodar/kvartiry/sdam-ASgBAgICAUSSA8gQ?s=104'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36', 'accept': '*/*'}
HOST = 'https://www.avito.ru'
FILENAME = "data_file.json"

def prepare_soup(html):
    soup = BeautifulSoup(html, 'html.parser')
  # вип-объявления удаляeм
    for div in soup.find_all(class_= re.compile("^items-vip-")):    
     div.decompose()
   # из других городов удаляeм  - если имеется - объявлений на одну страницу  
    for div in soup.find_all(class_= re.compile("^items-extra-")):    
     div.decompose()  
    return soup
     
def get_html(url, params=None):
    errors = ''
    try:
      r = requests.get(url, headers=HEADERS, params=params)
      r.raise_for_status()
    except requests.exceptions.Timeout:
      time.sleep(random.randint(3, 5))  
      r = get_html(url)
    # except requests.exceptions.TooManyRedirects:
    # except requests.exceptions.ConnectionError
    # except requests.exceptions.HTTPError 
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        errors = e
    #   raise SystemExit(e)
    return r, errors;

def get_count_pagination(soup):
    return soup.find(attrs={"data-marker":"pagination-button/next"}).previous_element

def parse(soup, aparts):
#     soup = BeautifulSoup(html, 'html.parser')
#   #  print(soup.prettify())
#   # вип-объявления удаляeм
#     for div in soup.find_all(class_= re.compile("^items-vip-")):    #("div", {'class':'sidebar'}): 
#      div.decompose()
#    # из других городов удаляeм  - если имеется - объявлений на одну страницу  
#     for div in soup.find_all(class_= re.compile("^items-extra-")):    
#      div.decompose()

#     last_pagination = soup.find(attrs={"data-marker":"pagination-button/next"}).previous_element

    items = soup.find_all(attrs={"data-marker":"item"})

    for item in items:
     id = item.get('data-item-id') #item.find(class_= re.compile("^iva-item-root-"))
     title = item.find(class_= re.compile("^iva-item-")).get_text(strip=True) 
     price = item.find(class_= re.compile("^price-price-")).find(attrs={"itemprop":"price"}).get('content')
     address = item.find(class_= re.compile("^geo-address-")).get_text(strip=True) 
     raion = item.find(class_= re.compile("^geo-georeferences-"))
     if raion != None:
      raion = item.find(class_= re.compile("^geo-georeferences-")).get_text(strip=True) 
     else:
       raion = '' 
     url = item.find('a', class_= re.compile("^link-link-")).get('href') 
    # description = item.find(class_= re.compile("^iva-item-description-")).get_text(strip=True)
     description = item.find(attrs={"itemprop":"description"}).get('content')
  #   if (description is None):
   #    description = item.find(class_= re.compile("^iva-item-description-"))
   #  user_info = item.find(class_=re.compile("iva-item-userInfoStep-"))
     user_info = item.find(class_=re.compile("iva-item-userInfoStep-")).get_text(strip=True) 
     dt_now = datetime.datetime.now()
 
     if any(x == id for x, *_ in aparts): 
       return

     aparts.append({
            'id': id,
            'url': url,
            'title': title,
            'price': price,
            'address': address,
            'raion': raion,
            'description': description,
            'user_info': user_info, #.find('title'),
            'time': dt_now,
            # 'price': item.find('span', class_='snippet-price').get_text(strip=True).replace('  ₽', '').replace(' ', '')[:-3],
            # 'rooms': rooms,
            # 'meters': meters,
            # 'floor': item.find('span', class_='snippet-link-name').get_text(strip=True)[M+4:SLASH],
            # 'street': street,
            # 'house': house.split(', ')[-1],
            # 'link': HOST + item.find('a', class_='snippet-link').get('href'),
     })

   # M = item.find('span', class_='snippet-link-name').get_text(strip=True).find('м')
   #  SLASH = item.find('span', class_='snippet-link-name').get_text(strip=True).find('/')
    # STREET = item.find('span', class_='item-address__string').get_text(strip=True)
    # house = item.find('span', class_='item-address__string').get_text(strip=True).replace('д. ', '').replace('стр. ', '')
    # rooms = item.find('span', class_='snippet-link-name').get_text(strip=True)[:1]
    # meters = item.find('span', class_='snippet-link-name').get_text(strip=True)

    # if rooms == 'К':
    #     rooms = '1'
    #     meters = meters[17:M-1]
    # else:
    #     meters = meters[14:M-1]

    # if STREET.find('у') == 0:
    #     street = item.find('span', class_='item-address__string').get_text(strip=True).split(', ')[0].replace('ул. ', '')
    # else:
    #     street = item.find('span', class_='item-address__string').get_text(strip=True).split(', ')[-2].replace(' ул.', '')

    # aparts.append({
    #     'price': item.find('span', class_='snippet-price').get_text(strip=True).replace('  ₽', '').replace(' ', '')[:-3],
    #     'rooms': rooms,
    #     'meters': meters,
    #     'floor': item.find('span', class_='snippet-link-name').get_text(strip=True)[M+4:SLASH],
    #     'street': street,
    #     'house': house.split(', ')[-1],
    #     'link': HOST + item.find('a', class_='snippet-link').get('href'),
    # })

    #print(aparts)
  
     time.sleep(random.randint(1, 3)) # пауза от 1 до 3 секунд

def load_html(url):
    html, errors = get_html(url)
    if errors != '':
       print('Error {errors}') 
       return None
    if html.status_code == 200:
        return html.text
      #  get_content(html.text)
    else:
        print('Error { html.status_code} url:{url}')
        return None
######################################################################
aparts = []
try:
  with open(FILENAME, "r") as read_file:
    aparts = json.load(read_file)
except FileNotFoundError:
  print(f"Запрашиваемый файл {FILENAME } не найден")

url = URL
html = load_html(url)
if html != None:
  soup = prepare_soup(html)
  count_page = get_count_pagination(soup)
  if count_page.isdigit():
      count_page = int(count_page)
  else:
    count_page = 1

  curent_page = 1

  parse(soup, aparts)

  while curent_page < count_page:
   curent_page += 1
   url = URL + '?p=' + str(curent_page)
   html = load_html(url)
   if html != None:
     soup = prepare_soup(html)   
     parse(soup, aparts)

  if  aparts != []  :
    #  сохраняем в файл
    with open("data_file.json", "w") as write_file:
       json.dump(aparts, write_file, indent=2)
