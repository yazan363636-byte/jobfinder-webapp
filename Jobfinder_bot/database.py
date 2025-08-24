import sqlite3

def init_db():
    conn = sqlite3.connect('favorites.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            user_id INTEGER,
            vacancy_id INTEGER,
            title TEXT,
            company TEXT,
            salary TEXT,
            url TEXT,
            PRIMARY KEY (user_id, vacancy_id)
        )
    ''')
    conn.commit()
    conn.close()

def add_favorite(user_id, vac):
    conn = sqlite3.connect('favorites.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO favorites (user_id, vacancy_id, title, company, salary, url)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, vac['id'], vac['title'], vac['company'], vac['salary'], vac['url']))
    conn.commit()
    conn.close()

def get_favorites(user_id):
    conn = sqlite3.connect('favorites.db')
    c = conn.cursor()
    c.execute('SELECT title, company, salary, url FROM favorites WHERE user_id = ?', (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows