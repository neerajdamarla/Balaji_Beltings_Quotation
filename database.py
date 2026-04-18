import sqlite3

DB = "quotation_app.db"

def init_db():
    with sqlite3.connect(DB, timeout=10) as conn:
        c = conn.cursor()

        # Customers
        c.execute('''CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT, address TEXT, email TEXT, phone TEXT)''')

        # Items
        c.execute('''CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, hsn TEXT, make TEXT, default_price REAL)''')

        # Users
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE, password TEXT)''')

        # Quotations
        c.execute('''CREATE TABLE IF NOT EXISTS quotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quotation_no TEXT,
            quotation_date TEXT,
            customer_id INTEGER,
            FOREIGN KEY(customer_id) REFERENCES customers(id))''')
        


        # Quotation Items
        c.execute('''CREATE TABLE IF NOT EXISTS quotation_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quotation_id INTEGER,
            item_id INTEGER,
            qty REAL,
            uom TEXT,
            price REAL,
            FOREIGN KEY(quotation_id) REFERENCES quotations(id),
            FOREIGN KEY(item_id) REFERENCES items(id))''')

        # Insert default admin
        c.execute("SELECT COUNT(*) FROM users")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))

        conn.commit()


def validate_user(username, password):
    with sqlite3.connect(DB, timeout=10) as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
        row = c.fetchone()
        return row is not None


def add_customer(name, address, email, phone):
    with sqlite3.connect(DB, timeout=10) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO customers (company_name,address,email,phone) VALUES (?,?,?,?)",
                  (name, address, email, phone))
        conn.commit()


def add_item(name, hsn, make, price):
    with sqlite3.connect(DB, timeout=10) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO items (name,hsn,make,default_price) VALUES (?,?,?,?)",
                  (name, hsn, make, price))
        conn.commit()


def get_customers():
    with sqlite3.connect(DB, timeout=10) as conn:
        c = conn.cursor()
        c.execute("SELECT id, company_name, address, email, phone FROM customers ORDER BY company_name")
        return c.fetchall()


def get_items(search=""):
    with sqlite3.connect(DB, timeout=10) as conn:
        c = conn.cursor()
        if search:
            like = f"%{search}%"
            c.execute("SELECT id,name,hsn,make,default_price FROM items WHERE name LIKE ? OR hsn LIKE ?", (like, like))
        else:
            c.execute("SELECT id,name,hsn,make,default_price FROM items")
        return c.fetchall()


def save_quotation(meta, customer_id, items):
    with sqlite3.connect(DB, timeout=10) as conn:
        c = conn.cursor()
        c.execute("""INSERT INTO quotations 
                     (quotation_no, quotation_date, customer_id)
                     VALUES (?,?,?)""",
                  (meta['quotation_no'], meta['quotation_date'], customer_id))
        qid = c.lastrowid
        for it in items:
            c.execute("""INSERT INTO quotation_items 
                         (quotation_id, item_id, qty, uom, price)
                         VALUES (?,?,?,?,?)""",
                      (qid, it['id'], it['qty'], it['uom'], it['price']))
        conn.commit()


def get_quotation_history(customer_id=None, item_id=None):
    with sqlite3.connect(DB, timeout=10) as conn:
        c = conn.cursor()
        query = """SELECT q.quotation_no, q.quotation_date, c.company_name,
                          i.name, i.hsn, i.make,
                          qi.qty, qi.uom, qi.price
                   FROM quotations q
                   JOIN customers c ON q.customer_id = c.id
                   JOIN quotation_items qi ON q.id = qi.quotation_id
                   JOIN items i ON qi.item_id = i.id"""
        params = []
        conds = []
        if customer_id:
            conds.append("q.customer_id=?")
            params.append(customer_id)
        if item_id:
            conds.append("qi.item_id=?")
            params.append(item_id)
        if conds:
            query += " WHERE " + " AND ".join(conds)
        query += " ORDER BY q.quotation_date DESC"
        c.execute(query, params)
        return c.fetchall()
    
def get_latest_quotation(customer_id, item_id):
    with sqlite3.connect(DB, timeout=10) as conn:
        c = conn.cursor()
        query = """SELECT q.quotation_no, q.quotation_date, c.company_name,
                          i.name, i.hsn, i.make,
                          qi.qty, qi.uom, qi.price
                   FROM quotations q
                   JOIN customers c ON q.customer_id = c.id
                   JOIN quotation_items qi ON q.id = qi.quotation_id
                   JOIN items i ON qi.item_id = i.id
                   WHERE q.customer_id=? AND qi.item_id=?
                   ORDER BY q.id DESC LIMIT 1"""
        c.execute(query, (customer_id, item_id))
        return c.fetchone()