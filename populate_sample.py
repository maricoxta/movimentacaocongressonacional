#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de exemplo
Útil para demonstração e testes
"""

import sys
import os

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from etl.database_manager import DatabaseManager
from etl.sample_data import populate_sample_data

def main():
    """Função principal"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                População de Dados de Exemplo                 ║
║                                                              ║
║  Dashboard Agenda Congresso - CNM                           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Inicializar gerenciador de banco
        print("🔧 Inicializando banco de dados...")
        db_manager = DatabaseManager()
        
        # Verificar se já existem dados
        eventos_existentes = db_manager.get_eventos_por_area(limit=1)
        
        if eventos_existentes:
            print("⚠️  Já existem dados no banco!")
            resposta = input("Deseja limpar e recriar com dados de exemplo? (s/N): ").strip().lower()
            
            if resposta != 's':
                print("❌ Operação cancelada")
                return
            
            # Limpar dados existentes
            print("🗑️  Limpando dados existentes...")
            import sqlite3
            with sqlite3.connect(db_manager.db_path) as conn:
                conn.execute("DELETE FROM eventos")
                conn.execute("DELETE FROM estatisticas_projetos")
                conn.execute("DELETE FROM logs_atualizacao")
                conn.commit()
            print("✅ Dados limpos")
        
        # Popular com dados de exemplo
        populate_sample_data(db_manager)
        
        print("\n🎉 População concluída com sucesso!")
        print("\n📊 Dados inseridos:")
        print("   • 10 eventos de exemplo")
        print("   • Estatísticas para 9 áreas técnicas")
        print("   • Log de população")
        
        print("\n🚀 Para testar o sistema:")
        print("   1. Execute: python api/app.py")
        print("   2. Abra: web/index.html no navegador")
        print("   3. Ou execute: python start.py")
        
    except Exception as e:
        print(f"❌ Erro durante a população: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
