import sqlite3

def initiate_db():
    conn = sqlite3.connect('not_telegram.db')
    cursor = conn.cursor()

    # Создание таблицы Products, если она ещё не создана
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL
    )
    ''')

    # Создание таблицы Users, если она ещё не создана
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        age INTEGER NOT NULL,
        balance INTEGER NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

def get_all_products():
    conn = sqlite3.connect('not_telegram.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Products')
    products = cursor.fetchall()

    conn.close()

    return products

def populate_products():
    conn = sqlite3.connect('not_telegram.db')
    cursor = conn.cursor()

    products = [
        ('Product1', 'Описание 1', 100),
        ('Product2', 'Описание 2', 200),
        ('Product3', 'Описание 3', 300),
        ('Product4', 'Описание 4', 400)
    ]

    cursor.executemany('''
    INSERT INTO Products (title, description, price) VALUES (?, ?, ?)
    ''', products)

    conn.commit()
    conn.close()

def add_user(username, email, age):
    conn = sqlite3.connect('not_telegram.db')
    cursor = conn.cursor()

    balance = 1000  # Баланс у новых пользователей всегда равен 1000
    cursor.execute('''
    INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)
    ''', (username, email, age, balance))

    conn.commit()
    conn.close()

def is_included(username):
    conn = sqlite3.connect('not_telegram.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Users WHERE username = ?', (username,))
    user = cursor.fetchone()

    conn.close()

    return user is not None