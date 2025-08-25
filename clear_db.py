import sqlite3
import os

# Caminho do banco
db_path = "database/agenda_congresso.db"

# Remover banco se existir
if os.path.exists(db_path):
    os.remove(db_path)
    print("Banco de dados removido.")

# Recriar banco
from etl.database_manager import DatabaseManager
db = DatabaseManager()
print("Banco de dados recriado com sucesso.")
