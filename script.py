import requests
import csv
import os
import pathlib
import shutil
import urllib.request
from bs4 import BeautifulSoup

url = 'https://books.toscrape.com/'
data_pages = []

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
    category = soup.select('li > a')[2].text.lower()
    review_rating = soup.find(class_='star-rating').get('class')[1]
    image_url = url.replace('catalogue/a-light-in-the-attic_1000/index.html', '') + soup.find('img')['src'].replace('../../', '')
    
    download_image(image_url, title, category)

    return  [
        product_page_url, 
        universal_product_code,
        title,
        price_including_tax,
        price_excluding_tax,
        number_available,
        product_description,
        category,
        review_rating,
        image_url
        ]

def create_image_folder () :
    path = pathlib.Path("./images")

    if path.exists():
        shutil.rmtree(path) 

    try:
        os.mkdir(path)
    except OSError as error:
        print(error)  

        
def create_category_folder(category) :
    directory = category
    parent_dir = "./images"
    path = os.path.join(parent_dir, directory) 

    try:
        os.mkdir(path)
    except OSError as error:
        print(error)  


def download_image(image_url, title, category) :
    title = title.replace(' ', '-').lower()
    file_name = f"./images/{category}/{title}.jpg"
    urllib.request.urlretrieve(image_url, file_name)


def scrap_category(category_url) :
    print(url + category_url)
    response = requests.get(url + category_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    links = soup.select('div.image_container > a')
    for link in links:
        data_page = scrap_one_page('catalogue/' + link['href'].replace('../../../', ''))
        data_pages.append(data_page)

    next_button = soup.find(class_='next')
    if next_button != None :
        next_url = next_button.find('a').get('href')
        scrap_category(f'catalogue/category/books/default_15/{next_url}')


with open('book.csv', 'w', newline='', encoding='utf-8') as fichier_csv:
    writter = csv.writer(fichier_csv)
    writter.writerow([
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
        ])
    
    create_image_folder()
    create_category_folder('default')
    scrap_category('catalogue/category/books/default_15/index.html')
    
    for data in data_pages :
        writter.writerow(
            data
        )
