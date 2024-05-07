from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import json

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        payment = request.form['payment']
        cart_items_json = request.form['cart_items']

        with get_db_connection() as conn:
            # Вставка заказа
            cur = conn.cursor()
            cur.execute('INSERT INTO orders (name, email, address, payment) VALUES (?, ?, ?, ?)',
                        (name, email, address, payment))
            order_id = cur.lastrowid  # Получение ID заказа

            # Вставка заказанных товаров
            cart_items = json.loads(cart_items_json)
            for item in cart_items:
                cur.execute('INSERT INTO order_items (order_id, product_name, quantity) VALUES (?, ?, ?)',
                            (order_id, item['name'], item['quantity']))

            conn.commit()

        return redirect(url_for('index'))

    return render_template('checkout.html')

@app.route('/product/<int:product_id>')
def product(product_id):
    # Подключение к базе данных
    with get_db_connection() as conn:
        # Извлечение данных о товаре из базы данных
        product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        if not product:
            return 'Товар не найден', 404

    return render_template('product.html',
                           product_name=product['name'],
                           product_description=product['description'],
                           product_price=product['price'],
                           product_image=product['image'])

if __name__ == '__main__':
    app.run(debug=True)
