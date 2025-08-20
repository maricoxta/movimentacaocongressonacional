#!/usr/bin/env python3
"""
Script para executar o sistema completo automaticamente
"""

import subprocess
import sys
import time
import os

def main():
    print("🚀 Iniciando sistema completo...")
    
    # Executar ETL uma vez primeiro
    print("🔄 Executando ETL inicial...")
    try:
        result = subprocess.run([
            sys.executable, "etl/etl_main.py", "uma-vez"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ ETL executado com sucesso")
        else:
            print(f"⚠️  ETL com avisos: {result.stderr}")
    except Exception as e:
        print(f"❌ Erro no ETL: {e}")
    
    # Iniciar API
    print("🚀 Iniciando API...")
    try:
        api_process = subprocess.Popen([
            sys.executable, "api/app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguardar API inicializar
        time.sleep(3)
        
        if api_process.poll() is None:
            print("✅ API iniciada com sucesso (porta 5000)")
        else:
            print("❌ Erro ao iniciar API")
            return
    except Exception as e:
        print(f"❌ Erro ao iniciar API: {e}")
        return
    
    # Iniciar agendador do ETL
    print("⏰ Iniciando agendador do ETL...")
    try:
        etl_process = subprocess.Popen([
            sys.executable, "etl/etl_main.py", "agendar"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Agendador do ETL iniciado")
    except Exception as e:
        print(f"❌ Erro ao iniciar agendador: {e}")
    
    # Abrir dashboard
    print("🌐 Abrindo dashboard...")
    try:
        import webbrowser
        from pathlib import Path
        
        dashboard_path = Path("web/index.html").absolute()
        
        if dashboard_path.exists():
            webbrowser.open(f"file://{dashboard_path}")
            print("✅ Dashboard aberto no navegador")
        else:
            print("❌ Arquivo do dashboard não encontrado")
    except Exception as e:
        print(f"❌ Erro ao abrir dashboard: {e}")
    
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
        if 'api_process' in locals():
            api_process.terminate()
        if 'etl_process' in locals():
            etl_process.terminate()
        print("✅ Sistema parado")

if __name__ == "__main__":
    main()
