import sqlite3
import os

# Caminho absoluto para garantir que funcione de qualquer lugar
caminho = os.path.join(os.path.dirname(__file__), 'database', 'meusite.db')

def conectar():
    return sqlite3.connect(caminho)