import requests
import csv
import os
import pathlib
import matplotlib.pyplot as plt
import shutil
import urllib.request
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer



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
    category_data = {}
    for category in categorys :
        #create_category_folder(category.text.replace(' ', '').replace('\n', '').lower())
        #scrap_category(category["href"])
        data = counter(category.text.replace(' ', '').replace('\n', '').lower())
        category_data[category.text.replace(' ', '').replace('\n', '').lower()] = data

    return category_data

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

def other_category(category_data) :
    categorys = [key for key in category_data.keys()]
    book_count = [count[0] for count in category_data.values()]
    book_count_high = []
    other_category = []
    other = 0
    for i in range(len(book_count)) :
        if book_count[i] <= 12 :
            other += book_count[i]
        else :
            book_count_high.append(book_count[i])
            other_category.append(categorys[i])
    
    book_count_high.append(other)
    other_category.append("other")

    return [book_count_high, other_category]


def pie_chart(category_data) :
    other = (other_category(category_data))
    categorys = other[1]
    book_count = other[0]
  

    plt.figure(figsize=(10, 10))
    plt.pie(book_count, labels=categorys, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 8}, wedgeprops={'linewidth': 0.5, 'edgecolor': 'black'})
    plt.axis('equal')
    plt.title('Répartition des prix moyens des livres par catégorie')
    plot_filename = "chart-pie.png"  
    plt.savefig(plot_filename)
    plt.close()

def bar_chart(category_data) :
    categorys = [key for key in category_data.keys()]
    prices = [price[1] for price in category_data.values()]

    plt.figure(figsize=(10, 12))
    plt.barh(categorys, prices, color='skyblue')
    plt.xlabel('Prix moyen (en £)')
    plt.title('Prix moyen des livres par catégorie')
    plt.tight_layout()
    plot_filename = "chart-bar.png"  
    plt.savefig(plot_filename)
    plt.close()

def get_most_espensive(category_data) : 
    categorys = [key for key in category_data.keys()]
    prices = [price[1] for price in category_data.values()]
    index_of_max = prices.index(max(prices))
    return categorys[index_of_max]

def get_higher_category(category_data) :
    categorys = [key for key in category_data.keys()]
    book_count = [count[0] for count in category_data.values()]
    index_of_max = book_count.index(max(book_count))
    return categorys[index_of_max]

def get_average_price(category_data) :
    prices = [price[1] for price in category_data.values()]
    average_price = sum(prices) / len(prices)
    return round(average_price, 2)

def create_pdf(filename, category_data):

    pdf = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    description_style = styles['BodyText']

    title = Paragraph("Rapport des prix des livres d'occasion", title_style)


    plot_image1 = Image("chart-pie.png")
    plot_image1.drawWidth = 600

    plot_image1.drawHeight = 600
    description1 = Paragraph("Description : Répartition des prix moyens des livres par catégorie.", description_style)


    plot_image2 = Image("chart-bar.png")
    plot_image2.drawWidth = 500
    plot_image2.drawHeight = 600
    description2 = Paragraph("Description : Prix moyen des livres par catégorie.", description_style)

    stats = Paragraph(f"La catégorie la plus représentée est {get_higher_category(category_data)}, la catégorie qui a le prix moyen le plus élevé est {get_most_espensive(category_data)} et le prix moyen de tous les livres est {get_average_price(category_data)}£.")

    content = [title, Spacer(1, 20), plot_image1, Spacer(1, 10), description1, Spacer(1, 20), plot_image2, Spacer(1, 10), description2, Spacer(1, 10), stats]

    pdf.build(content)

#create_setup_folder('images')
#create_setup_folder('csv')
category_data = scrap_all()
pie_chart(category_data)
bar_chart(category_data)
create_pdf("rapport_prix_livres.pdf", category_data)



