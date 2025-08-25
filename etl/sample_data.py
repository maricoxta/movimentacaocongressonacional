"""
Dados de exemplo para testes e demonstração do Dashboard Agenda Congresso
"""

import sqlite3
from datetime import datetime, timedelta
from etl.database_manager import DatabaseManager

def get_sample_eventos():
    """Retorna eventos de exemplo - APENAS Sessões e Reuniões legislativas"""
    return [
        {
            'evento_id_externo': 'camara_001',
            'nome': '22ª Reunião Ordinária - Comissão de Meio Ambiente e Desenvolvimento Sustentável',
            'data_inicio': '26/08/2025 às 14:00',
            'data_fim': '26/08/2025 às 18:00',
            'situacao': 'Agendada',
            'tema': 'Discussão e votação das emendas a serem apresentadas pela Comissão de Meio Ambiente à Comissão Mista de Planos, Orçamentos Públicos e Fiscalização (CMO) referentes ao PLDO 2026 (PLN 2/2025)',
            'tipo_evento': 'Reunião de Comissão',
            'local_evento': 'Sala 1 da Ala Nilo Coelho - Senado Federal',
            'link_evento': 'https://www25.senado.leg.br/web/atividade/agenda/2025/08/26',
            'area_tecnica': 'Meio Ambiente e Saneamento',
            'fonte': 'senado',
            'comissao': 'Comissão de Meio Ambiente e Desenvolvimento Sustentável',
            'finalidade': 'Discussão e votação das emendas a serem apresentadas pela Comissão de Meio Ambiente à Comissão Mista de Planos, Orçamentos Públicos e Fiscalização (CMO) referentes ao PLDO 2026 (PLN 2/2025), que "Dispõe sobre as diretrizes para a elaboração e a execução da Lei Orçamentária de 2026 e dá outras providências".'
        },
        {
            'evento_id_externo': 'camara_002',
            'nome': 'Sessão Ordinária - Plenário da Câmara dos Deputados',
            'data_inicio': '27/08/2025 às 14:00',
            'data_fim': '27/08/2025 às 22:00',
            'situacao': 'Agendada',
            'tema': 'Votação de Projetos de Lei sobre Financiamento Municipal e Transferências Constitucionais',
            'tipo_evento': 'Sessão Plenária',
            'local_evento': 'Plenário Ulysses Guimarães - Câmara dos Deputados',
            'link_evento': 'https://www.camara.leg.br/eventos/agenda/2025/08/27',
            'area_tecnica': 'Finanças',
            'fonte': 'camara',
            'comissao': 'Plenário da Câmara dos Deputados',
            'finalidade': 'Votação de projetos de lei relacionados ao financiamento municipal, incluindo PL 1234/2025 sobre transferências constitucionais e PL 5678/2025 sobre fundo de participação dos municípios.'
        },
        {
            'evento_id_externo': 'senado_003',
            'nome': '15ª Reunião Extraordinária - Comissão de Assuntos Sociais',
            'data_inicio': '28/08/2025 às 09:00',
            'data_fim': '28/08/2025 às 12:00',
            'situacao': 'Agendada',
            'tema': 'Análise de Projetos de Lei sobre Políticas Públicas de Educação Básica nos Municípios',
            'tipo_evento': 'Reunião de Comissão',
            'local_evento': 'Sala 3 da Ala Alexandre Costa - Senado Federal',
            'link_evento': 'https://www25.senado.leg.br/web/atividade/agenda/2025/08/28',
            'area_tecnica': 'Educação',
            'fonte': 'senado',
            'comissao': 'Comissão de Assuntos Sociais',
            'finalidade': 'Análise e votação de projetos de lei relacionados à educação básica municipal, incluindo PL 9876/2025 sobre financiamento da educação básica e PL 5432/2025 sobre merenda escolar.'
        },
        {
            'evento_id_externo': 'camara_004',
            'nome': 'Sessão Deliberativa - Plenário da Câmara dos Deputados',
            'data_inicio': '29/08/2025 às 15:00',
            'data_fim': '29/08/2025 às 20:00',
            'situacao': 'Agendada',
            'tema': 'Votação de Projetos de Lei sobre Saúde Pública Municipal',
            'tipo_evento': 'Sessão Plenária',
            'local_evento': 'Plenário Ulysses Guimarães - Câmara dos Deputados',
            'link_evento': 'https://www.camara.leg.br/eventos/agenda/2025/08/29',
            'area_tecnica': 'Saúde',
            'fonte': 'camara',
            'comissao': 'Plenário da Câmara dos Deputados',
            'finalidade': 'Votação de projetos de lei relacionados à saúde pública municipal, incluindo PL 1111/2025 sobre atenção básica de saúde e PL 2222/2025 sobre financiamento do SUS municipal.'
        },
        {
            'evento_id_externo': 'senado_005',
            'nome': '8ª Reunião Ordinária - Comissão de Constituição, Justiça e Cidadania',
            'data_inicio': '30/08/2025 às 10:00',
            'data_fim': '30/08/2025 às 13:00',
            'situacao': 'Agendada',
            'tema': 'Análise de Projetos de Lei sobre Autonomia Municipal e Competências Legislativas',
            'tipo_evento': 'Reunião de Comissão',
            'local_evento': 'Sala 2 da Ala Nilo Coelho - Senado Federal',
            'link_evento': 'https://www25.senado.leg.br/web/atividade/agenda/2025/08/30',
            'area_tecnica': 'Jurídico',
            'fonte': 'senado',
            'comissao': 'Comissão de Constituição, Justiça e Cidadania',
            'finalidade': 'Análise de projetos de lei relacionados à autonomia municipal e competências legislativas, incluindo PL 3333/2025 sobre competências municipais e PL 4444/2025 sobre autonomia financeira dos municípios.'
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
