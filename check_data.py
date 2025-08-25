from etl.database_manager import DatabaseManager

db = DatabaseManager()
eventos = db.get_eventos_por_area()

print(f"Total de eventos: {len(eventos)}")
print("\nPrimeiros 10 eventos:")
for i, evento in enumerate(eventos[:10]):
    print(f"{i+1}. {evento['nome']} ({evento['tipo_evento']}) - {evento['fonte']}")

print("\nEventos por fonte:")
camara = [e for e in eventos if e['fonte'] == 'camara']
senado = [e for e in eventos if e['fonte'] == 'senado']
print(f"Câmara: {len(camara)} eventos")
print(f"Senado: {len(senado)} eventos")
