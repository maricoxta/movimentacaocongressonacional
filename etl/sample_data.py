"""
Dados de exemplo para testes e demonstração do Dashboard Agenda Congresso
"""

import sqlite3
from datetime import datetime, timedelta
from etl.database_manager import DatabaseManager

def get_sample_eventos():
    """Retorna eventos de exemplo baseados em dados reais"""
    return [
        {
            'evento_id_externo': 'senado_cupula_climatica_2025',
            'nome': 'Abertura da II Cúpula Parlamentar de Mudança Climática e Transição Justa da América Latina e do Caribe',
            'data_inicio': '06/08/2025 às 09:00',
            'data_fim': '06/08/2025 às 18:00',
            'situacao': 'Em Andamento',
            'tema': 'Meio Ambiente e Saneamento',
            'tipo_evento': 'Cúpula Parlamentar',
            'local_evento': 'Plenário do Senado Federal',
            'link_evento': 'https://www12.senado.leg.br/institucional/eventos/detalheeventoeventos?evento_id=abertura-da-ii-cupula-parlamentar-de-mudanca-climatica-e-transicao-justa-da-america-latina-e-do-caribe',
            'area_tecnica': 'Meio Ambiente e Saneamento',
            'fonte': 'senado'
        },
        {
            'evento_id_externo': 'camara_audiencia_educacao_2025',
            'nome': 'Audiência Pública sobre Políticas Públicas de Educação Básica nos Municípios',
            'data_inicio': '22/08/2025 às 14:00',
            'data_fim': '22/08/2025 às 18:00',
            'situacao': 'Em Andamento',
            'tema': 'Educação',
            'tipo_evento': 'Audiência Pública',
            'local_evento': 'Anexo II, Plenário 01 - Câmara dos Deputados',
            'link_evento': 'https://www.camara.leg.br/eventos/12345',
            'area_tecnica': 'Educação',
            'fonte': 'camara'
        },
        {
            'evento_id_externo': 'camara_sessao_plenario_2025',
            'nome': 'Sessão Plenária - Votação de Projetos de Lei sobre Financiamento Municipal',
            'data_inicio': '25/08/2025 às 10:00',
            'data_fim': '25/08/2025 às 18:00',
            'situacao': 'Em Andamento',
            'tema': 'Finanças',
            'tipo_evento': 'Sessão Plenária',
            'local_evento': 'Plenário Ulysses Guimarães - Câmara dos Deputados',
            'link_evento': 'https://www.camara.leg.br/eventos/67890',
            'area_tecnica': 'Finanças',
            'fonte': 'camara'
        },
        {
            'evento_id_externo': 'senado_reuniao_saude_2025',
            'nome': 'Reunião da Comissão de Assuntos Sociais - Discussão sobre SUS Municipal',
            'data_inicio': '28/08/2025 às 15:00',
            'data_fim': '28/08/2025 às 17:00',
            'situacao': 'Em Andamento',
            'tema': 'Saúde',
            'tipo_evento': 'Reunião de Comissão',
            'local_evento': 'Sala 9 da Ala Senador Alexandre Costa - Senado Federal',
            'link_evento': 'https://www12.senado.leg.br/institucional/eventos/detalheeventoeventos?evento_id=reuniao-comissao-assuntos-sociais-sus-municipal',
            'area_tecnica': 'Saúde',
            'fonte': 'senado'
        },
        {
            'evento_id_externo': 'camara_debate_infraestrutura_2025',
            'nome': 'Debate sobre Investimentos em Infraestrutura Municipal',
            'data_inicio': '30/08/2025 às 16:00',
            'data_fim': '30/08/2025 às 19:00',
            'situacao': 'Em Andamento',
            'tema': 'Infraestrutura',
            'tipo_evento': 'Debate',
            'local_evento': 'Anexo II, Plenário 02 - Câmara dos Deputados',
            'link_evento': 'https://www.camara.leg.br/eventos/11111',
            'area_tecnica': 'Obras, Transferências e Parcerias',
            'fonte': 'camara'
        },
        {
            'evento_id_externo': 'senado_seminario_cultura_2025',
            'nome': 'Seminário sobre Políticas Culturais Municipais',
            'data_inicio': '02/09/2025 às 09:00',
            'data_fim': '02/09/2025 às 17:00',
            'situacao': 'Em Andamento',
            'tema': 'Cultura',
            'tipo_evento': 'Seminário',
            'local_evento': 'Auditório Petrônio Portella - Senado Federal',
            'link_evento': 'https://www12.senado.leg.br/institucional/eventos/detalheeventoeventos?evento_id=seminario-politicas-culturais-municipais',
            'area_tecnica': 'Cultura',
            'fonte': 'senado'
        },
        {
            'evento_id_externo': 'camara_audiencia_seguranca_2025',
            'nome': 'Audiência Pública sobre Segurança Pública Municipal',
            'data_inicio': '05/09/2025 às 14:30',
            'data_fim': '05/09/2025 às 18:30',
            'situacao': 'Em Andamento',
            'tema': 'Segurança',
            'tipo_evento': 'Audiência Pública',
            'local_evento': 'Anexo II, Plenário 03 - Câmara dos Deputados',
            'link_evento': 'https://www.camara.leg.br/eventos/22222',
            'area_tecnica': 'Jurídico',
            'fonte': 'camara'
        },
        {
            'evento_id_externo': 'senado_conferencia_transporte_2025',
            'nome': 'Conferência sobre Mobilidade Urbana e Transporte Municipal',
            'data_inicio': '08/09/2025 às 10:00',
            'data_fim': '08/09/2025 às 16:00',
            'situacao': 'Em Andamento',
            'tema': 'Transporte',
            'tipo_evento': 'Conferência',
            'local_evento': 'Plenário do Senado Federal',
            'link_evento': 'https://www12.senado.leg.br/institucional/eventos/detalheeventoeventos?evento_id=conferencia-mobilidade-urbana-transporte-municipal',
            'area_tecnica': 'Transporte e Mobilidade',
            'fonte': 'senado'
        }
    ]

def get_sample_statistics():
    """Retorna estatísticas de exemplo baseadas em dados reais"""
    return [
        {
            'area_tecnica': 'Meio Ambiente e Saneamento',
            'posicionamento_cnm': 'Favorável',
            'aprovacao_camara': 15,
            'aprovacao_senado': 12,
            'sancionado_presidencia': 10
        },
        {
            'area_tecnica': 'Meio Ambiente e Saneamento',
            'posicionamento_cnm': 'Desfavorável',
            'aprovacao_camara': 3,
            'aprovacao_senado': 2,
            'sancionado_presidencia': 1
        },
        {
            'area_tecnica': 'Meio Ambiente e Saneamento',
            'posicionamento_cnm': 'Neutro',
            'aprovacao_camara': 8,
            'aprovacao_senado': 6,
            'sancionado_presidencia': 5
        },
        {
            'area_tecnica': 'Educação',
            'posicionamento_cnm': 'Favorável',
            'aprovacao_camara': 22,
            'aprovacao_senado': 18,
            'sancionado_presidencia': 15
        },
        {
            'area_tecnica': 'Educação',
            'posicionamento_cnm': 'Desfavorável',
            'aprovacao_camara': 2,
            'aprovacao_senado': 1,
            'sancionado_presidencia': 0
        },
        {
            'area_tecnica': 'Finanças',
            'posicionamento_cnm': 'Favorável',
            'aprovacao_camara': 18,
            'aprovacao_senado': 14,
            'sancionado_presidencia': 12
        },
        {
            'area_tecnica': 'Saúde',
            'posicionamento_cnm': 'Favorável',
            'aprovacao_camara': 25,
            'aprovacao_senado': 20,
            'sancionado_presidencia': 18
        }
    ]

def populate_sample_data():
    """Popula o banco de dados com dados de exemplo"""
    db_manager = DatabaseManager()
    
    # Inserir eventos de exemplo
    eventos = get_sample_eventos()
    eventos_inseridos = 0
    
    for evento in eventos:
        if db_manager.insert_evento(evento):
            eventos_inseridos += 1
    
    print(f"✅ {eventos_inseridos} eventos de exemplo inseridos")
    
    # Inserir estatísticas de exemplo
    estatisticas = get_sample_statistics()
    stats_inseridas = 0
    
    import sqlite3
    with sqlite3.connect(db_manager.db_path) as conn:
        for stat in estatisticas:
            try:
                conn.execute("""
                    INSERT INTO estatisticas_projetos 
                    (area_tecnica, posicionamento_cnm, aprovacao_camara, aprovacao_senado, sancionado_presidencia)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    stat['area_tecnica'],
                    stat['posicionamento_cnm'],
                    stat['aprovacao_camara'],
                    stat['aprovacao_senado'],
                    stat['sancionado_presidencia']
                ))
                stats_inseridas += 1
            except Exception as e:
                print(f"Erro ao inserir estatística: {e}")
    
    print(f"✅ {stats_inseridas} estatísticas de exemplo inseridas")
    
    # Log da operação
    db_manager.log_atualizacao(
        tipo="POPULACAO_DADOS_EXEMPLO",
        status="SUCESSO",
        eventos_novos=eventos_inseridos,
        detalhes=f"Dados de exemplo inseridos: {eventos_inseridos} eventos, {stats_inseridas} estatísticas"
    )
    
    return eventos_inseridos, stats_inseridas
