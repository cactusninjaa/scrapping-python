import csv

from scrap import scrap_all

import asyncio
import matplotlib.pyplot as plt
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image


def counter(category_name):
    """
    Compte le nombre de livres dans une catégorie et calcule le prix moyen.

    Args:
        category_name (str): Le nom de la catégorie pour laquelle compter les livres.

    Returns:
        list: Un tableau contenant le nombre de livres et le prix moyen arrondi à deux décimales.
    """
    total_price, count = 0, 0
    with open(f'./csv/{category_name}.csv', 'r', newline='', encoding='utf-8') as fichier_csv:
        reader = csv.reader(fichier_csv)
        # Ignore l'en-tête
        next(reader)
        for ligne in reader:
            price = ligne[3].replace('£', '').replace(' ', '')
            if price:  # Vérifie que le prix n'est pas vide
                total_price += float(price)
                count += 1
    average_price = round(total_price / count, 2) if count > 0 else 0
    return [count, average_price]

def other_category(category_data):
    """
    Regroupe les catégories en fonction du nombre de livres, en consolidant celles qui en ont peu.

    Args:
        category_data (dict): Dictionnaire contenant les données des catégories.

    Returns:
        list: Un tableau contenant les comptes de livres consolidés et les noms des catégories.
    """
    category_names = list(category_data.keys())
    book_counts = [data[0] for data in category_data.values()]
    consolidated_counts = []
    consolidated_names = []
    other_count = 0

    for i, count in enumerate(book_counts):
        if count <= 12:
            other_count += count
        else:
            consolidated_counts.append(count)
            consolidated_names.append(category_names[i])

    consolidated_counts.append(other_count)
    consolidated_names.append("other")

    return [consolidated_counts, consolidated_names]

def pie_chart(category_data):
    """
    Crée un graphique circulaire représentant la répartition des prix moyens des livres par catégorie.

    Args:
        category_data (dict): Dictionnaire contenant les données des catégories.

    Returns:
        None
    """
    other = other_category(category_data)
    categories = other[1]
    book_counts = other[0]

    plt.figure(figsize=(10, 10))
    plt.pie(book_counts, labels=categories, autopct='%1.1f%%', startangle=140, 
            textprops={'fontsize': 8}, wedgeprops={'linewidth': 0.5, 'edgecolor': 'black'})
    plt.axis('equal')
    plt.title('Répartition des prix moyens des livres par catégorie')
    plt.savefig("chart-pie.png")
    plt.close()

def bar_chart(category_data):
    """
    Crée un graphique à barres représentant le prix moyen des livres par catégorie.

    Args:
        category_data (dict): Dictionnaire contenant les données des catégories.

    Returns:
        None
    """
    categories = list(category_data.keys())
    prices = [data[1] for data in category_data.values()]

    plt.figure(figsize=(10, 12))
    plt.barh(categories, prices, color='skyblue')
    plt.xlabel('Prix moyen (en £)')
    plt.title('Prix moyen des livres par catégorie')
    plt.tight_layout()
    plt.savefig("chart-bar.png")
    plt.close()

def get_most_expensive(category_data):
    """
    Trouve la catégorie ayant le prix moyen le plus élevé.

    Args:
        category_data (dict): Dictionnaire contenant les données des catégories.

    Returns:
        str: Le nom de la catégorie avec le prix moyen le plus élevé.
    """
    prices = [data[1] for data in category_data.values()]
    max_price_index = prices.index(max(prices))
    return list(category_data.keys())[max_price_index]

def get_higher_category(category_data):
    """
    Trouve la catégorie ayant le plus grand nombre de livres.

    Args:
        category_data (dict): Dictionnaire contenant les données des catégories.

    Returns:
        str: Le nom de la catégorie avec le plus grand nombre de livres.
    """
    book_counts = [data[0] for data in category_data.values()]
    max_count_index = book_counts.index(max(book_counts))
    return list(category_data.keys())[max_count_index]

def get_average_price(category_data):
    """
    Calcule le prix moyen de tous les livres.

    Args:
        category_data (dict): Dictionnaire contenant les données des catégories.

    Returns:
        float: Le prix moyen arrondi à deux décimales.
    """
    prices = [data[1] for data in category_data.values()]
    average_price = sum(prices) / len(prices) if prices else 0
    return round(average_price, 2)

def create_pdf(filename, category_data):
    """
    Crée un rapport PDF des prix des livres avec des graphiques.

    Args:
        filename (str): Le nom du fichier PDF à créer.
        category_data (dict): Dictionnaire contenant les données des catégories.

    Returns:
        None
    """
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

    stats = Paragraph(
        f"La catégorie la plus représentée est {get_higher_category(category_data)}, "
        f"la catégorie qui a le prix moyen le plus élevé est {get_most_expensive(category_data)} "
        f"et le prix moyen de tous les livres est {get_average_price(category_data)}£.",
        description_style
    )

    content = [title, Spacer(1, 20), plot_image1, Spacer(1, 10), description1,
               Spacer(1, 20), plot_image2, Spacer(1, 10), description2, Spacer(1, 10), stats]

    pdf.build(content)


category_data = asyncio.run(scrap_all())
pie_chart(category_data)
bar_chart(category_data)
create_pdf("rapport_prix_livres.pdf", category_data)