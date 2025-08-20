#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de exemplo
"""

import sys
import os
import sqlite3

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from etl.database_manager import DatabaseManager
from etl.sample_data import populate_sample_data

def main():
    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║                População de Dados de Exemplo                 ║")
    print("║                                                              ║")
    print("║  Dashboard Agenda Congresso - CNM                           ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    print("🔧 Inicializando banco de dados...")
    
    db_manager = DatabaseManager()
    
    # Verificar se já existem dados
    try:
        eventos = db_manager.get_eventos_por_area()
        if eventos:
            print("⚠️  Já existem dados no banco!")
            resposta = input("Deseja limpar e recriar com dados de exemplo? (s/N): ")
            
            if resposta.lower() in ['s', 'sim', 'y', 'yes']:
                print("🗑️  Limpando dados existentes...")
                
                # Limpar dados existentes
                import sqlite3
                with sqlite3.connect(db_manager.db_path) as conn:
                    conn.execute("DELETE FROM eventos")
                    conn.execute("DELETE FROM estatisticas_projetos")
                    conn.execute("DELETE FROM logs_atualizacao")
                    conn.commit()
                
                print("✅ Dados limpos")
            else:
                print("❌ Operação cancelada pelo usuário")
                return
    except Exception as e:
        print(f"⚠️  Erro ao verificar dados existentes: {e}")
    
    try:
        # Popular com dados de exemplo
        eventos_inseridos, stats_inseridas = populate_sample_data()
        
        print(f"\n🎉 População concluída com sucesso!")
        print(f"📊 Eventos inseridos: {eventos_inseridos}")
        print(f"📈 Estatísticas inseridas: {stats_inseridas}")
        
        # Mostrar alguns exemplos
        print("\n📝 Exemplos de eventos inseridos:")
        eventos = db_manager.get_eventos_por_area()
        for i, evento in enumerate(eventos[:3]):
            print(f"  {i+1}. {evento['nome']}")
            print(f"     Data: {evento['data_inicio']}")
            print(f"     Área: {evento['area_tecnica']}")
            print(f"     Link: {evento['link_evento']}")
            print()
        
    except Exception as e:
        print(f"❌ Erro durante a população: {e}")

if __name__ == "__main__":
    main()
