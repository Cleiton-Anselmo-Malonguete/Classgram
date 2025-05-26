# criar_banco.py
import sqlite3

def criar_banco():
    with open('database.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()

    conn = sqlite3.connect('meusite.db')
    cursor = conn.cursor()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
    print("Banco de dados criado com sucesso!")

if __name__ == '__main__':
    criar_banco()