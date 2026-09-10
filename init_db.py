import sqlite3

def khoi_tao_db():
    ket_noi = sqlite3.connect('database.db')
    con_tro = ket_noi.cursor()

    con_tro.execute("DROP TABLE IF EXISTS users")
    con_tro.execute("DROP TABLE IF EXISTS records")
    con_tro.execute("DROP TABLE IF EXISTS logs")

    con_tro.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT
        )
    ''')

    con_tro.execute('''
        CREATE TABLE records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            owner TEXT NOT NULL
        )
    ''')

    con_tro.execute('''
        CREATE TABLE logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            endpoint TEXT,
            request_payload TEXT,
            status TEXT
        )
    ''')

    # Dữ liệu bảng users
    con_tro.execute("INSERT INTO users (id, username, password, role, email) VALUES (1, 'admin', 'AdminP@ss2026!', 'Administrator', 'admin@lab.local')")
    con_tro.execute("INSERT INTO users (id, username, password, role, email) VALUES (2, 'john_doe', 'Password123', 'User', 'john@lab.local')")

    # Dữ liệu bảng records
    con_tro.execute("INSERT INTO records (id, name, description, owner) VALUES (1, 'Project Alpha Plan', 'Confidential business strategy for 2026', 'admin')")
    con_tro.execute("INSERT INTO records (id, name, description, owner) VALUES (2, 'Financial Audit Q2', 'Internal financial records', 'admin')")
    con_tro.execute("INSERT INTO records (id, name, description, owner) VALUES (3, 'Public Notice', 'General guidelines for employees', 'john_doe')")

    # Dữ liệu log mẫu có sẵn đầy đủ cho cả 3 Demo
    con_tro.execute("INSERT INTO logs (endpoint, request_payload, status) VALUES ('/login', 'User: admin''--', 'SUCCESS / BYPASSED')")
    con_tro.execute("INSERT INTO logs (endpoint, request_payload, status) VALUES ('/manage', 'ID: 1, Desc: Hacked'', owner=''attacker'' --', 'MODIFY_ATTEMPT')")
    con_tro.execute("INSERT INTO logs (endpoint, request_payload, status) VALUES ('/search', ''' UNION SELECT id, username, password, role FROM users --', 'SEARCH_PERFORMED')")

    ket_noi.commit()
    ket_noi.close()
    print("Database SQLite đã được khởi tạo thành công!")
    return True

if __name__ == '__main__':
    khoi_tao_db()