import requests
import csv
import os
import pathlib
import shutil
import urllib.request
from bs4 import BeautifulSoup

url = 'https://books.toscrape.com/'

def scrap_one_page(page_url) :
    response = requests.get(url + page_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table_rows = soup.select('tr > td')

    product_page_url = url + page_url
    universal_product_code = table_rows[0].text
    title = soup.find('h1').text
    price_including_tax = table_rows[2].text.replace('Â', '')
    price_excluding_tax = table_rows[3].text.replace('Â', '')
    number_available = table_rows[5].text.split()[2].replace('(', '')
    product_description = soup.find_all('p')[3].text
    category = soup.select('li > a')[2].text.lower().replace(" ",'')
    review_rating = soup.find(class_='star-rating').get('class')[1]
    image_url = url.replace('catalogue/a-light-in-the-attic_1000/index.html', '') + soup.find('img')['src'].replace('../../', '')
    
    download_image(image_url, title, category)

    dict = {
        "product_page_url": product_page_url,
        "universal_product_code": universal_product_code,
        "title": title,
        "price_including_tax": price_including_tax,
        "price_excluding_tax": price_excluding_tax,
        "number_available": number_available,
        "product_description": product_description,
        "category": category,
        "review_rating": review_rating,
        "image_url": image_url
    }

    with open(f'./csv/{category}.csv', 'a', newline='', encoding='utf-8') as fichier_csv:
        fieldnames = [
            'product_page_url', 
            'universal_product_code',
            'title',
            'price_including_tax',
            'price_excluding_tax',
            'number_available',
            'product_description',
            'category',
            'review_rating',
            'image_url'
            ]
        writer = csv.DictWriter(fichier_csv, fieldnames=fieldnames)
        if fichier_csv.tell() == 0 :
            writer.writeheader()
        writer.writerow(dict)



def create_setup_folder(name) :
    path = pathlib.Path(f"./{name}")

    if path.exists():
        shutil.rmtree(path) 

    try:
        os.mkdir(path)
    except OSError as error:
        print(error)  

        
def create_category_folder(category) :
    directory = category
    print(directory)
    parent_dir = "./images"
    path = os.path.join(parent_dir, directory) 

    try:
        os.mkdir(path)
    except OSError as error:
        print(error)  


def download_image(image_url, title, category) :
    title = title.replace(' ', '-').lower().replace('/','-')
    file_name = f"./images/{category}/{title}.jpg"
    urllib.request.urlretrieve(image_url, file_name)


def scrap_category(category_url) :
    print(url + category_url)

    response = requests.get(url + category_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    links = soup.select('div.image_container > a')
    for link in links:
        scrap_one_page('catalogue/' + link['href'].replace('../../../', ''))

    next_button = soup.find(class_='next')
    if next_button != None :
        next_url = next_button.find('a').get('href')
        category_base_url_split = category_url.split('/')
        category_base_url_split.pop(4)
        category_base_url = "/".join(category_base_url_split)
        scrap_category(f'{category_base_url}/{next_url}')

    

def scrap_all() :
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    categorys = soup.select('ul.nav > li > ul > li > a')
    for category in categorys :
        create_category_folder(category.text.replace(' ', '').replace('\n', '').lower())
        scrap_category(category["href"])

create_setup_folder('images')
create_setup_folder('csv')
scrap_all()

