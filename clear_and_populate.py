import sqlite3
import os
from etl.database_manager import DatabaseManager
from etl.sample_data import get_sample_eventos
from etl.categorizador import CategorizadorEventos

# Caminho do banco
db_path = "database/agenda_congresso.db"

print("Limpando banco de dados...")
# Remover banco se existir
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print("Banco de dados removido.")
    except PermissionError:
        print("Erro: Banco está sendo usado. Tentando limpar tabela...")
        db = DatabaseManager()
        with sqlite3.connect(db.db_path) as conn:
            conn.execute("DELETE FROM eventos")
            conn.commit()
        print("Tabela de eventos limpa.")

# Recriar banco
print("Recriando banco de dados...")
db = DatabaseManager()

# Carregar dados de exemplo
print("Carregando dados de exemplo...")
eventos = get_sample_eventos()

# Categorizar eventos
print("Categorizando eventos...")
categorizador = CategorizadorEventos(db)
eventos_categorizados = categorizador.categorizar_lote(eventos)

# Salvar no banco
print("Salvando no banco...")
for evento in eventos_categorizados:
    db.insert_evento(evento)

print(f"✅ Banco populado com {len(eventos)} eventos (apenas Sessões e Reuniões)")
