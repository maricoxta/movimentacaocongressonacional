#!/usr/bin/env python3
"""
Script de inicialização do Dashboard Agenda Congresso - CNM
Facilita a execução do sistema completo
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

def print_banner():
    """Exibe banner do sistema"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                Dashboard Agenda Congresso - CNM              ║
║                                                              ║
║  Sistema ETL para extração e visualização de dados          ║
║  da Câmara dos Deputados e do Senado Federal                ║
╚══════════════════════════════════════════════════════════════╝
    """)

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    try:
        import requests
        import pandas
        import flask
        import schedule
        print("✅ Todas as dependências estão instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("💡 Execute: pip install -r requirements.txt")
        return False

def run_etl():
    """Executa o ETL uma vez"""
    print("🔄 Executando ETL...")
    try:
        result = subprocess.run([
            sys.executable, "etl/etl_main.py", "uma-vez"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ ETL executado com sucesso")
            return True
        else:
            print(f"❌ Erro no ETL: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro ao executar ETL: {e}")
        return False

def start_api():
    """Inicia a API Flask"""
    print("🚀 Iniciando API...")
    try:
        # Iniciar API em thread separada
        api_process = subprocess.Popen([
            sys.executable, "api/app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguardar um pouco para a API inicializar
        time.sleep(3)
        
        if api_process.poll() is None:
            print("✅ API iniciada com sucesso (porta 5000)")
            return api_process
        else:
            print("❌ Erro ao iniciar API")
            return None
    except Exception as e:
        print(f"❌ Erro ao iniciar API: {e}")
        return None

def start_etl_scheduler():
    """Inicia o agendador do ETL"""
    print("⏰ Iniciando agendador do ETL...")
    try:
        etl_process = subprocess.Popen([
            sys.executable, "etl/etl_main.py", "agendar"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Agendador do ETL iniciado")
        return etl_process
    except Exception as e:
        print(f"❌ Erro ao iniciar agendador: {e}")
        return None

def open_dashboard():
    """Abre o dashboard no navegador"""
    import webbrowser
    
    dashboard_path = Path("web/index.html").absolute()
    
    if dashboard_path.exists():
        print("🌐 Abrindo dashboard...")
        webbrowser.open(f"file://{dashboard_path}")
        print("✅ Dashboard aberto no navegador")
    else:
        print("❌ Arquivo do dashboard não encontrado")

def main():
    """Função principal"""
    print_banner()
    
    # Verificar dependências
    if not check_dependencies():
        return
    
    print("\n🎯 Escolha uma opção:")
    print("1. Executar ETL uma vez")
    print("2. Iniciar sistema completo (ETL + API + Dashboard)")
    print("3. Iniciar apenas API")
    print("4. Abrir apenas dashboard")
    print("5. Sair")
    
    choice = input("\nDigite sua escolha (1-5): ").strip()
    
    if choice == "1":
        # Executar ETL uma vez
        run_etl()
        
    elif choice == "2":
        # Sistema completo
        print("\n🚀 Iniciando sistema completo...")
        
        # Executar ETL inicial
        if not run_etl():
            print("❌ Falha no ETL inicial. Abortando...")
            return
        
        # Iniciar API
        api_process = start_api()
        if not api_process:
            print("❌ Falha ao iniciar API. Abortando...")
            return
        
        # Iniciar agendador do ETL
        etl_process = start_etl_scheduler()
        
        # Abrir dashboard
        time.sleep(2)
        open_dashboard()
        
        print("\n✅ Sistema iniciado com sucesso!")
        print("📊 Dashboard: http://localhost:5000")
        print("🔌 API: http://localhost:5000/api")
        print("\n⏹️  Pressione Ctrl+C para parar...")
        
        try:
            # Manter sistema rodando
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Parando sistema...")
            if api_process:
                api_process.terminate()
            if etl_process:
                etl_process.terminate()
            print("✅ Sistema parado")
        
    elif choice == "3":
        # Apenas API
        api_process = start_api()
        if api_process:
            print("\n✅ API iniciada!")
            print("🔌 Endpoint: http://localhost:5000/api")
            print("\n⏹️  Pressione Ctrl+C para parar...")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Parando API...")
                api_process.terminate()
                print("✅ API parada")
        
    elif choice == "4":
        # Apenas dashboard
        open_dashboard()
        
    elif choice == "5":
        print("👋 Até logo!")
        
    else:
        print("❌ Opção inválida!")

if __name__ == "__main__":
    main()
