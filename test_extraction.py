#!/usr/bin/env python3
"""
Script para testar a extração real de dados das APIs da Câmara e Senado
"""

import sys
import os
from datetime import datetime, timedelta

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from etl.extractor_camara import CamaraExtractor
from etl.extractor_senado import SenadoExtractor
from etl.database_manager import DatabaseManager
from etl.categorizador import CategorizadorEventos

def test_camara_extraction():
    """Testa extração da Câmara"""
    print("🔍 Testando extração da Câmara dos Deputados...")
    
    camara = CamaraExtractor()
    
    # Definir período de teste (próximos 30 dias para encontrar mais eventos)
    data_inicio = datetime.now().strftime("%Y-%m-%d")
    data_fim = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"📅 Período: {data_inicio} a {data_fim}")
    
    try:
        # Testar eventos das comissões
        print("📋 Buscando eventos das comissões...")
        eventos_comissoes = camara.get_eventos_comissoes(data_inicio, data_fim)
        print(f"✅ Encontrados {len(eventos_comissoes)} eventos das comissões")
        
        # Testar sessões do plenário
        print("🏛️ Buscando sessões do plenário...")
        eventos_plenario = camara.get_sessoes_plenario(data_inicio, data_fim)
        print(f"✅ Encontrados {len(eventos_plenario)} eventos do plenário")
        
        # Mostrar alguns exemplos
        todos_eventos = eventos_comissoes + eventos_plenario
        if todos_eventos:
            print("\n📝 Exemplos de eventos encontrados:")
            for i, evento in enumerate(todos_eventos[:3]):
                print(f"  {i+1}. {evento['nome']}")
                print(f"     Data: {evento['data_inicio']}")
                print(f"     Tipo: {evento['tipo_evento']}")
                print(f"     Local: {evento['local_evento']}")
                print(f"     Link: {evento['link_evento']}")
                print()
        
        return todos_eventos
        
    except Exception as e:
        print(f"❌ Erro na extração da Câmara: {e}")
        return []

def test_senado_extraction():
    """Testa extração do Senado"""
    print("\n🔍 Testando extração do Senado Federal...")
    
    senado = SenadoExtractor()
    
    # Definir período de teste (próximos 30 dias)
    data_inicio = datetime.now().strftime("%Y-%m-%d")
    data_fim = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"📅 Período: {data_inicio} a {data_fim}")
    
    try:
        # Testar eventos das comissões
        print("📋 Buscando eventos das comissões...")
        eventos_comissoes = senado.get_eventos_comissoes(data_inicio, data_fim)
        print(f"✅ Encontrados {len(eventos_comissoes)} eventos das comissões")
        
        # Testar agenda geral
        print("📅 Buscando agenda geral...")
        eventos_geral = senado.get_agenda_geral(data_inicio, data_fim)
        print(f"✅ Encontrados {len(eventos_geral)} eventos da agenda geral")
        
        # Mostrar alguns exemplos
        todos_eventos = eventos_comissoes + eventos_geral
        if todos_eventos:
            print("\n📝 Exemplos de eventos encontrados:")
            for i, evento in enumerate(todos_eventos[:3]):
                print(f"  {i+1}. {evento['nome']}")
                print(f"     Data: {evento['data_inicio']}")
                print(f"     Tipo: {evento['tipo_evento']}")
                print(f"     Local: {evento['local_evento']}")
                print(f"     Link: {evento['link_evento']}")
                print()
        
        return todos_eventos
        
    except Exception as e:
        print(f"❌ Erro na extração do Senado: {e}")
        return []

def test_full_etl():
    """Testa o ETL completo"""
    print("\n🚀 Testando ETL completo...")
    
    try:
        # Extrair dados
        eventos_camara = test_camara_extraction()
        eventos_senado = test_senado_extraction()
        
        todos_eventos = eventos_camara + eventos_senado
        
        if not todos_eventos:
            print("⚠️ Nenhum evento encontrado. Testando com período maior...")
            
            # Tentar com período maior (últimos 7 dias até próximos 60 dias)
            data_inicio = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            data_fim = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
            
            print(f"🔄 Tentando período maior: {data_inicio} a {data_fim}")
            
            camara = CamaraExtractor()
            senado = SenadoExtractor()
            
            eventos_camara = camara.get_eventos_comissoes(data_inicio, data_fim)
            eventos_camara.extend(camara.get_sessoes_plenario(data_inicio, data_fim))
            
            eventos_senado = senado.get_eventos_comissoes(data_inicio, data_fim)
            eventos_senado.extend(senado.get_agenda_geral(data_inicio, data_fim))
            
            todos_eventos = eventos_camara + eventos_senado
            
            if todos_eventos:
                print(f"✅ Encontrados {len(todos_eventos)} eventos no período maior")
            else:
                print("❌ Nenhum evento encontrado mesmo com período maior")
                return
        
        print(f"\n📊 Total de eventos encontrados: {len(todos_eventos)}")
        print(f"   - Câmara: {len(eventos_camara)}")
        print(f"   - Senado: {len(eventos_senado)}")
        
        # Testar categorização
        print("\n🏷️ Testando categorização...")
        db_manager = DatabaseManager()
        categorizador = CategorizadorEventos(db_manager)
        
        eventos_categorizados = categorizador.categorizar_lote(todos_eventos)
        
        # Contar por área técnica
        areas_count = {}
        for evento in eventos_categorizados:
            area = evento.get('area_tecnica', 'Não categorizado')
            areas_count[area] = areas_count.get(area, 0) + 1
        
        print("\n📈 Distribuição por área técnica:")
        for area, count in areas_count.items():
            print(f"   - {area}: {count} eventos")
        
        # Testar salvamento no banco
        print("\n💾 Testando salvamento no banco...")
        eventos_novos = 0
        for evento in eventos_categorizados:
            if db_manager.insert_evento(evento):
                eventos_novos += 1
        
        print(f"✅ {eventos_novos} eventos salvos no banco")
        
        # Log da execução
        db_manager.log_atualizacao(
            tipo="TESTE_EXTRACAO",
            status="SUCESSO",
            eventos_novos=eventos_novos,
            detalhes=f"Teste de extração: {len(todos_eventos)} eventos processados"
        )
        
        print("\n🎉 Teste de ETL concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no teste de ETL: {e}")

def test_api_endpoints():
    """Testa endpoints específicos das APIs"""
    print("\n🔗 Testando endpoints das APIs...")
    
    import requests
    
    # Testar API da Câmara
    print("🏛️ Testando API da Câmara...")
    try:
        response = requests.get("https://dadosabertos.camara.leg.br/api/v2/orgaos", timeout=10)
        if response.status_code == 200:
            print("✅ API da Câmara está funcionando")
            dados = response.json()
            print(f"   - Encontrados {len(dados.get('dados', []))} órgãos")
        else:
            print(f"❌ API da Câmara retornou status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar API da Câmara: {e}")
    
    # Testar API do Senado
    print("\n🏛️ Testando API do Senado...")
    try:
        response = requests.get("https://www12.senado.leg.br/dados-abertos", timeout=10)
        if response.status_code == 200:
            print("✅ API do Senado está funcionando")
            print(f"   - Content-Type: {response.headers.get('content-type', 'N/A')}")
        else:
            print(f"❌ API do Senado retornou status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar API do Senado: {e}")

def main():
    print("🧪 TESTE DE EXTRAÇÃO DE DADOS DAS APIS")
    print("=" * 50)
    
    # Testar conectividade das APIs
    test_api_endpoints()
    
    # Testar extração completa
    test_full_etl()
    
    print("\n" + "=" * 50)
    print("✅ Teste concluído!")

if __name__ == "__main__":
    main()
