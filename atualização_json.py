import json
import os
from etl.database_manager import DatabaseManager

# Inicializar gerenciador de banco
db_manager = DatabaseManager()

# Pasta onde os JSONs serão salvos
DATA_DIR = os.path.join(os.path.dirname(__file__), '../web/data')
os.makedirs(DATA_DIR, exist_ok=True)

# ----------------------------
# Áreas
# ----------------------------
areas = db_manager.get_areas_tecnicas()
with open(os.path.join(DATA_DIR, 'areas.json'), 'w', encoding='utf-8') as f:
    json.dump(areas, f, ensure_ascii=False, indent=2)

# ----------------------------
# Eventos
# ----------------------------
eventos = db_manager.get_eventos_por_area(limit=1000)  # pega todos
with open(os.path.join(DATA_DIR, 'eventos.json'), 'w', encoding='utf-8') as f:
    json.dump(eventos, f, ensure_ascii=False, indent=2)

# ----------------------------
# Proposições
# ----------------------------
proposicoes = []
for area in areas:
    proposicoes += db_manager.get_proposicoes_por_area(area['nome'])

with open(os.path.join(DATA_DIR, 'proposicoes.json'), 'w', encoding='utf-8') as f:
    json.dump(proposicoes, f, ensure_ascii=False, indent=2)

print("Arquivos JSON atualizados com sucesso!")
