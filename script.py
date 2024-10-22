import requests
import csv
from bs4 import BeautifulSoup

url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
table_rows = []

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
    table_rows = soup.select('tr > td')

    product_page_url = url
    universal_product_code = table_rows[0].text
    title = soup.find('h1').text
    price_including_tax = table_rows[2].text.replace('Â', '')
    price_excluding_tax = table_rows[3].text.replace('Â', '')
    number_available = table_rows[5].text.split()[2].replace('(', '')
    product_description = soup.find_all('p')[3].text
    category = soup.select('li > a')[2].text
    review_rating = 'n/a'
    image_url = url.replace('catalogue/a-light-in-the-attic_1000/index.html', '') + soup.find('img')['src'].replace('../../', '')

    writter.writerow(
        [
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
    )
