"""
Dados de exemplo para testes e demonstração do Dashboard Agenda Congresso
"""

SAMPLE_EVENTS = [
    {
        'evento_id_externo': 'camara_sample_001',
        'nome': 'Audiência Pública sobre Financiamento da Educação Municipal',
        'data_inicio': '25/07/2025 às 14:00',
        'data_fim': '25/07/2025 às 17:00',
        'situacao': 'Em Andamento',
        'tema': 'Financiamento da educação básica municipal',
        'tipo_evento': 'Audiência Pública',
        'local_evento': 'Plenário 10 - Câmara dos Deputados',
        'link_evento': 'https://www.camara.leg.br/eventos/12345',
        'area_tecnica': 'Educação',
        'fonte': 'camara'
    },
    {
        'evento_id_externo': 'senado_sample_001',
        'nome': 'Reunião da Comissão de Assuntos Municipais',
        'data_inicio': '26/07/2025 às 09:00',
        'data_fim': '26/07/2025 às 12:00',
        'situacao': 'Em Andamento',
        'tema': 'Políticas públicas municipais',
        'tipo_evento': 'Reunião',
        'local_evento': 'Sala 2 - Senado Federal',
        'link_evento': 'https://www.senado.leg.br/eventos/67890',
        'area_tecnica': 'Jurídico',
        'fonte': 'senado'
    },
    {
        'evento_id_externo': 'camara_sample_002',
        'nome': 'Sessão Plenária - Votação de Projetos de Lei Municipais',
        'data_inicio': '27/07/2025 às 16:00',
        'data_fim': '27/07/2025 às 20:00',
        'situacao': 'Em Andamento',
        'tema': 'Votação de projetos de interesse municipal',
        'tipo_evento': 'Sessão',
        'local_evento': 'Plenário Ulysses Guimarães - Câmara dos Deputados',
        'link_evento': 'https://www.camara.leg.br/eventos/12346',
        'area_tecnica': 'Jurídico',
        'fonte': 'camara'
    },
    {
        'evento_id_externo': 'senado_sample_002',
        'nome': 'Audiência Pública sobre Saneamento Básico',
        'data_inicio': '28/07/2025 às 15:30',
        'data_fim': '28/07/2025 às 18:30',
        'situacao': 'Em Andamento',
        'tema': 'Políticas de saneamento básico municipal',
        'tipo_evento': 'Audiência Pública',
        'local_evento': 'Auditório Petrônio Portella - Senado Federal',
        'link_evento': 'https://www.senado.leg.br/eventos/67891',
        'area_tecnica': 'Meio Ambiente e Saneamento',
        'fonte': 'senado'
    },
    {
        'evento_id_externo': 'camara_sample_003',
        'nome': 'Palestra sobre Gestão Financeira Municipal',
        'data_inicio': '29/07/2025 às 10:00',
        'data_fim': '29/07/2025 às 12:00',
        'situacao': 'Em Andamento',
        'tema': 'Boas práticas em gestão financeira municipal',
        'tipo_evento': 'Palestra',
        'local_evento': 'Auditório Nereu Ramos - Câmara dos Deputados',
        'link_evento': 'https://www.camara.leg.br/eventos/12347',
        'area_tecnica': 'Finanças',
        'fonte': 'camara'
    },
    {
        'evento_id_externo': 'senado_sample_003',
        'nome': 'Reunião sobre Políticas de Saúde Municipal',
        'data_inicio': '30/07/2025 às 14:00',
        'data_fim': '30/07/2025 às 16:00',
        'situacao': 'Em Andamento',
        'tema': 'Atenção básica de saúde nos municípios',
        'tipo_evento': 'Reunião',
        'local_evento': 'Sala 3 - Senado Federal',
        'link_evento': 'https://www.senado.leg.br/eventos/67892',
        'area_tecnica': 'Saúde',
        'fonte': 'senado'
    },
    {
        'evento_id_externo': 'camara_sample_004',
        'nome': 'Audiência Pública sobre Transporte Público Municipal',
        'data_inicio': '31/07/2025 às 09:30',
        'data_fim': '31/07/2025 às 12:30',
        'situacao': 'Em Andamento',
        'tema': 'Mobilidade urbana e transporte público',
        'tipo_evento': 'Audiência Pública',
        'local_evento': 'Plenário 9 - Câmara dos Deputados',
        'link_evento': 'https://www.camara.leg.br/eventos/12348',
        'area_tecnica': 'Transporte e Mobilidade',
        'fonte': 'camara'
    },
    {
        'evento_id_externo': 'senado_sample_004',
        'nome': 'Sessão sobre Orçamento Municipal',
        'data_inicio': '01/08/2025 às 16:00',
        'data_fim': '01/08/2025 às 18:00',
        'situacao': 'Em Andamento',
        'tema': 'Planejamento orçamentário municipal',
        'tipo_evento': 'Sessão',
        'local_evento': 'Plenário do Senado Federal',
        'link_evento': 'https://www.senado.leg.br/eventos/67893',
        'area_tecnica': 'Orçamento Público',
        'fonte': 'senado'
    },
    {
        'evento_id_externo': 'camara_sample_005',
        'nome': 'Reunião sobre Assistência Social Municipal',
        'data_inicio': '02/08/2025 às 14:00',
        'data_fim': '02/08/2025 às 16:00',
        'situacao': 'Em Andamento',
        'tema': 'Políticas de assistência social nos municípios',
        'tipo_evento': 'Reunião',
        'local_evento': 'Sala 5 - Câmara dos Deputados',
        'link_evento': 'https://www.camara.leg.br/eventos/12349',
        'area_tecnica': 'Assistência Social e Segurança Alimentar e Nutricional',
        'fonte': 'camara'
    },
    {
        'evento_id_externo': 'senado_sample_005',
        'nome': 'Palestra sobre Cultura Municipal',
        'data_inicio': '03/08/2025 às 10:00',
        'data_fim': '03/08/2025 às 12:00',
        'situacao': 'Em Andamento',
        'tema': 'Desenvolvimento cultural nos municípios',
        'tipo_evento': 'Palestra',
        'local_evento': 'Auditório Interlegis - Senado Federal',
        'link_evento': 'https://www.senado.leg.br/eventos/67894',
        'area_tecnica': 'Cultura',
        'fonte': 'senado'
    }
]

SAMPLE_STATISTICS = {
    'Educação': {
        'aprovados_favoraveis': 12,
        'reprovados_desfavoraveis': 3,
        'aprovados_cnm_favoravel': 10,
        'aprovados_cnm_desfavoravel': 2,
        'reprovados_cnm_favoravel': 1,
        'reprovados_cnm_desfavoravel': 2
    },
    'Saúde': {
        'aprovados_favoraveis': 8,
        'reprovados_desfavoraveis': 2,
        'aprovados_cnm_favoravel': 7,
        'aprovados_cnm_desfavoravel': 1,
        'reprovados_cnm_favoravel': 0,
        'reprovados_cnm_desfavoravel': 1
    },
    'Finanças': {
        'aprovados_favoraveis': 15,
        'reprovados_desfavoraveis': 5,
        'aprovados_cnm_favoravel': 12,
        'aprovados_cnm_desfavoravel': 3,
        'reprovados_cnm_favoravel': 2,
        'reprovados_cnm_desfavoravel': 3
    },
    'Meio Ambiente e Saneamento': {
        'aprovados_favoraveis': 6,
        'reprovados_desfavoraveis': 4,
        'aprovados_cnm_favoravel': 5,
        'aprovados_cnm_desfavoravel': 1,
        'reprovados_cnm_favoravel': 1,
        'reprovados_cnm_desfavoravel': 3
    },
    'Transporte e Mobilidade': {
        'aprovados_favoraveis': 9,
        'reprovados_desfavoraveis': 3,
        'aprovados_cnm_favoravel': 8,
        'aprovados_cnm_desfavoravel': 1,
        'reprovados_cnm_favoravel': 1,
        'reprovados_cnm_desfavoravel': 2
    },
    'Jurídico': {
        'aprovados_favoraveis': 20,
        'reprovados_desfavoraveis': 8,
        'aprovados_cnm_favoravel': 18,
        'aprovados_cnm_desfavoravel': 2,
        'reprovados_cnm_favoravel': 3,
        'reprovados_cnm_desfavoravel': 5
    },
    'Orçamento Público': {
        'aprovados_favoraveis': 11,
        'reprovados_desfavoraveis': 4,
        'aprovados_cnm_favoravel': 9,
        'aprovados_cnm_desfavoravel': 2,
        'reprovados_cnm_favoravel': 1,
        'reprovados_cnm_desfavoravel': 3
    },
    'Assistência Social e Segurança Alimentar e Nutricional': {
        'aprovados_favoraveis': 7,
        'reprovados_desfavoraveis': 2,
        'aprovados_cnm_favoravel': 6,
        'aprovados_cnm_desfavoravel': 1,
        'reprovados_cnm_favoravel': 0,
        'reprovados_cnm_desfavoravel': 1
    },
    'Cultura': {
        'aprovados_favoraveis': 4,
        'reprovados_desfavoraveis': 1,
        'aprovados_cnm_favoravel': 3,
        'aprovados_cnm_desfavoravel': 1,
        'reprovados_cnm_favoravel': 0,
        'reprovados_cnm_desfavoravel': 1
    }
}

def get_sample_events():
    """Retorna eventos de exemplo"""
    return SAMPLE_EVENTS

def get_sample_statistics(area_tecnica=None):
    """Retorna estatísticas de exemplo"""
    if area_tecnica:
        return SAMPLE_STATISTICS.get(area_tecnica, {
            'aprovados_favoraveis': 0,
            'reprovados_desfavoraveis': 0,
            'aprovados_cnm_favoravel': 0,
            'aprovados_cnm_desfavoravel': 0,
            'reprovados_cnm_favoravel': 0,
            'reprovados_cnm_desfavoravel': 0
        })
    return SAMPLE_STATISTICS

def populate_sample_data(db_manager):
    """Popula o banco com dados de exemplo"""
    print("📊 Populando banco com dados de exemplo...")
    
    # Inserir eventos de exemplo
    for evento in SAMPLE_EVENTS:
        db_manager.insert_evento(evento)
    
    print(f"✅ {len(SAMPLE_EVENTS)} eventos de exemplo inseridos")
    
    # Inserir estatísticas de exemplo
    for area, stats in SAMPLE_STATISTICS.items():
        try:
            import sqlite3
            with sqlite3.connect(db_manager.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO estatisticas_projetos 
                    (area_tecnica, projetos_aprovados_favoraveis, projetos_reprovados_desfavoraveis,
                     projetos_aprovados_cnm_favoravel, projetos_aprovados_cnm_desfavoravel,
                     projetos_reprovados_cnm_favoravel, projetos_reprovados_cnm_desfavoravel)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    area,
                    stats['aprovados_favoraveis'],
                    stats['reprovados_desfavoraveis'],
                    stats['aprovados_cnm_favoravel'],
                    stats['aprovados_cnm_desfavoravel'],
                    stats['reprovados_cnm_favoravel'],
                    stats['reprovados_cnm_desfavoravel']
                ))
                conn.commit()
        except Exception as e:
            print(f"Erro ao inserir estatísticas para {area}: {e}")
    
    print(f"✅ Estatísticas de exemplo inseridas para {len(SAMPLE_STATISTICS)} áreas")
    
    # Log da população
    db_manager.log_atualizacao(
        tipo="POPULACAO_EXEMPLO",
        status="SUCESSO",
        eventos_novos=len(SAMPLE_EVENTS),
        detalhes="Dados de exemplo inseridos para demonstração"
    )
