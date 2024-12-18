from app import app
from flask import request, render_template
import subprocess
import sqlite3
from app.scraping.database import create_connection
from app.scraping.scraper import scrape_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    quantity = request.form['quantity']

    if query.strip() == "":
        message = "Por favor, digite o item que deseja buscar!"
        message_type = "error"
        return render_template('index.html', message=message, message_type=message_type)
    if not quantity.isdigit() or int(quantity) < 10 or int(quantity) > 100:
        message = "Por favor, digite uma quantidade de itens entre 10 e 100!"
        message_type = "error"
        return render_template('index.html', message=message, message_type=message_type)


    # Removido devido caminho fixo.
    # python_path = r'C:\Users\badi_\Documents\comparativo-valores\env\Scripts\python.exe'
    # subprocess.run([python_path, 'app/scraping/scraper.py', query, quantity])

    # Inclusa chamada da função no mesmo processo
    scrape_data(query, quantity)

    database = "database/database.db"
    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute("SELECT title, description, price, link, reviews, rating, discount, seller, installments FROM products")
    results = cur.fetchall()

    # Calculando a média dos preços
    prices = []
    for result in results:
        try:
            price_str = result[2].replace('R$', '').strip().replace('.', '').replace(',', '.')
            prices.append(float(price_str))
        except ValueError:
            pass

    average_price = sum(prices) / len(prices) if prices else 0

    if results:
        message = "Busca realizada com sucesso!"
        message_type = "success"
    else:
        message = "Nenhum resultado encontrado!"
        message_type = "error"
    return render_template('index.html', results=results, message=message, message_type=message_type, average_price=average_price)
