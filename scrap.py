import os
import csv
import pathlib
import requests
import shutil
from bs4 import BeautifulSoup
import asyncio
import aiohttp
import time  # Pour mesurer le temps d'exécution

BASE_URL = 'https://books.toscrape.com/'

async def download_image(session, image_url, title, category):
    """
    Télécharge une image depuis une URL donnée et l'enregistre dans un dossier spécifique.

    Args:
        session (aiohttp.ClientSession): La session aiohttp utilisée pour faire des requêtes.
        image_url (str): L'URL de l'image à télécharger.
        title (str): Le titre du produit, utilisé pour nommer le fichier.
        category (str): La catégorie dans laquelle l'image sera enregistrée.

    Returns:
        None
    """
    title = title.replace(' ', '-').lower().replace('/', '-')
    file_name = f"./images/{category}/{title}.jpg"

    # Assurez-vous que le dossier de destination existe
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    
    async with session.get(image_url) as response:
        if response.status == 200:
            with open(file_name, 'wb') as f:
                f.write(await response.read())
        else:
            print(f"Error downloading image from {image_url}: Status code {response.status}")

def create_setup_folder(name):
    """
    Crée un dossier pour la configuration, en supprimant un dossier existant s'il y en a un.

    Args:
        name (str): Le nom du dossier à créer.

    Returns:
        None
    """
    path = pathlib.Path(f"./{name}")
    if path.exists():
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)

def create_category_folder(category):
    """
    Crée un dossier pour une catégorie donnée.

    Args:
        category (str): Le nom de la catégorie pour laquelle créer un dossier.

    Returns:
        None
    """
    path = os.path.join("./images", category)
    os.makedirs(path, exist_ok=True)

async def scrap_one_page(session, page_url):
    """
    Scrape les informations d'un produit sur une page donnée et télécharge son image.

    Args:
        session (aiohttp.ClientSession): La session aiohttp utilisée pour faire des requêtes.
        page_url (str): L'URL de la page à scraper.

    Returns:
        None
    """
    async with session.get(BASE_URL + page_url) as response:
        if response.status != 200:
            print(f"Failed to fetch {page_url}: {response.status}")
            return
        
        soup = BeautifulSoup(await response.text(), 'html.parser')
        table_rows = soup.select('tr > td')
        
        # Extract product details
        product_page_url = BASE_URL + page_url
        universal_product_code = table_rows[0].text
        title = soup.find('h1').text
        price_including_tax = table_rows[2].text.replace('Â', '')
        price_excluding_tax = table_rows[3].text.replace('Â', '')
        number_available = table_rows[5].text.split()[2].replace('(', '')
        product_description = soup.find_all('p')[3].text
        category = soup.select('li > a')[2].text.lower().replace(" ", "")
        review_rating = soup.find(class_='star-rating').get('class')[1]
        image_url = BASE_URL + soup.find('img')['src'].replace('../../', '')

        # Schedule image download asynchronously
        await download_image(session, image_url, title, category)

        # Prepare data dictionary
        data = {
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

        # Save data to CSV
        save_to_csv(data, category)

def save_to_csv(data, category):
    """
    Enregistre les informations d'un produit dans un fichier CSV.

    Args:
        data (dict): Dictionnaire contenant les informations du produit.
        category (str): La catégorie du produit, utilisée pour nommer le fichier.

    Returns:
        None
    """
    csv_path = f'./csv/{category}.csv'
    fieldnames = [
        'product_page_url', 'universal_product_code', 'title', 'price_including_tax',
        'price_excluding_tax', 'number_available', 'product_description',
        'category', 'review_rating', 'image_url'
    ]
    with open(csv_path, 'a', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if csv_file.tell() == 0:
            writer.writeheader()
        writer.writerow(data)

async def scrap_category(session, category_url, category_name):
    """
    Scrape toutes les pages de produits d'une catégorie donnée.

    Args:
        session (aiohttp.ClientSession): La session aiohttp utilisée pour faire des requêtes.
        category_url (str): L'URL de la catégorie à scraper.
        category_name (str): Le nom de la catégorie en cours de traitement.

    Returns:
        None
    """
    print(f"Scraping category: {category_name}...")
    async with session.get(BASE_URL + category_url) as response:
        if response.status != 200:
            print(f"Failed to fetch {category_url}: {response.status}")
            return
        
        soup = BeautifulSoup(await response.text(), 'html.parser')

        # Extract links to individual book pages
        links = soup.select('div.image_container > a')
        for link in links:
            page_url = 'catalogue/' + link['href'].replace('../../../', '')
            await scrap_one_page(session, page_url)

        # Check for the next page and recursively scrape it
        next_button = soup.find(class_='next')
        if next_button:
            next_url = next_button.find('a').get('href')
            category_base_url = "/".join(category_url.split('/')[:-1])
            await scrap_category(session, f'{category_base_url}/{next_url}', category_name)

def counter(category_name) :
    moyenne, counter = 0 , 0
    with open(f'./csv/{category_name}.csv','r', newline='',) as fichier_csv:         
        reader = csv.reader(fichier_csv)        
        for ligne in reader:     
            if ligne[3] == 'price_including_tax':
                continue
            counter += 1
            price = ligne[3].replace('£', '')
            moyenne += float(price) / counter
    return [counter, round(moyenne, 2)]

async def scrap_all():
    """
    Lance le processus de scraping pour toutes les catégories disponibles.

    Returns:
        None
    """
    start_time = time.time()  # Start the timer
    create_setup_folder('images')
    create_setup_folder('csv')

    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    category_data = {}

    categories = soup.select('ul.nav > li > ul > li > a')
    async with aiohttp.ClientSession() as session:
        for category in categories:
            category_name = category.text.strip().replace(" ", "").lower()
            create_category_folder(category_name)
            category_url = category['href']
            await scrap_category(session, category_url, category_name)

            data = counter(category.text.replace(' ', '').replace('\n', '').lower())
            category_data[category.text.replace(' ', '').replace('\n', '').lower()] = data

    
    # End the timer and print the total time taken
    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nScraping completed in {total_time:.2f} seconds.")
    
    return category_data

