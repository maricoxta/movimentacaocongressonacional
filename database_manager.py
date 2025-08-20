import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "database/agenda_congresso.db"):
        self.db_path = db_path
        self._ensure_database_exists()
        self._initialize_schema()
        self._populate_areas_tecnicas()

    def _ensure_database_exists(self):
        """Garante que o diretório do banco existe"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _initialize_schema(self):
        """Inicializa o schema do banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            # Tabela de eventos
            conn.execute("""
                CREATE TABLE IF NOT EXISTS eventos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evento_id_externo TEXT UNIQUE NOT NULL,
                    nome TEXT NOT NULL,
                    data_inicio TEXT,
                    data_fim TEXT,
                    situacao TEXT,
                    tema TEXT,
                    tipo_evento TEXT,
                    local_evento TEXT,
                    link_evento TEXT,
                    area_tecnica TEXT,
                    fonte TEXT,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabela de áreas técnicas
            conn.execute("""
                CREATE TABLE IF NOT EXISTS areas_tecnicas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL,
                    descricao TEXT,
                    palavras_chave TEXT,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabela de estatísticas de projetos
            conn.execute("""
                CREATE TABLE IF NOT EXISTS estatisticas_projetos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    area_tecnica TEXT NOT NULL,
                    projetos_aprovados_favoraveis INTEGER DEFAULT 0,
                    projetos_reprovados_desfavoraveis INTEGER DEFAULT 0,
                    projetos_aprovados_cnm_favoravel INTEGER DEFAULT 0,
                    projetos_aprovados_cnm_desfavoravel INTEGER DEFAULT 0,
                    projetos_reprovados_cnm_favoravel INTEGER DEFAULT 0,
                    projetos_reprovados_cnm_desfavoravel INTEGER DEFAULT 0,
                    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabela de logs de atualização
            conn.execute("""
                CREATE TABLE IF NOT EXISTS logs_atualizacao (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo_atualizacao TEXT NOT NULL,
                    status TEXT NOT NULL,
                    eventos_novos INTEGER DEFAULT 0,
                    eventos_atualizados INTEGER DEFAULT 0,
                    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    detalhes TEXT
                )
            """)

            # Tabela de proposições
            conn.execute("""
                CREATE TABLE IF NOT EXISTS proposicoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_projeto TEXT NOT NULL,
                    ementa TEXT NOT NULL,
                    casa_iniciadora TEXT NOT NULL,
                    forma_apreciacao TEXT NOT NULL,
                    eixo_tematico TEXT,
                    situacao TEXT NOT NULL,
                    cabe_analise TEXT NOT NULL,
                    prazo_analise TEXT,
                    analise_realizada TEXT NOT NULL,
                    documento_analise TEXT,
                    posicionamento_cnm TEXT NOT NULL,
                    prioridade TEXT NOT NULL,
                    observacao TEXT,
                    area_tecnica TEXT NOT NULL,
                    aprovacao_camara TEXT DEFAULT 'PENDENTE',
                    aprovacao_senado TEXT DEFAULT 'PENDENTE',
                    sancionado_presidencia TEXT DEFAULT 'PENDENTE',
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def _populate_areas_tecnicas(self):
        """Popula as áreas técnicas com dados padrão"""
        areas_data = [
            ("Assistência Social e Segurança Alimentar e Nutricional", "Políticas de assistência social e segurança alimentar", "assistência social, segurança alimentar, bolsa família, creas, cras"),
            ("Consórcios Públicos", "Gestão de consórcios intermunicipais", "consórcio, intermunicipal, associação pública"),
            ("Contabilidade Pública", "Contabilidade e gestão financeira pública", "contabilidade, gestão financeira, prestação de contas"),
            ("Cultura", "Políticas culturais e patrimônio", "cultura, patrimônio, arte, teatro, museu"),
            ("Defesa Civil", "Proteção e defesa civil", "defesa civil, emergência, desastre, calamidade"),
            ("Desenvolvimento Rural", "Desenvolvimento rural e agricultura familiar", "desenvolvimento rural, agricultura familiar, assentamento"),
            ("Educação", "Políticas educacionais", "educação, escola, creche, ensino fundamental"),
            ("Finanças", "Gestão financeira e tributária", "finanças, tributo, imposto, receita"),
            ("Jurídico", "Assuntos jurídicos e legislativos", "jurídico, advocacia, processo, legislação"),
            ("Meio Ambiente e Saneamento", "Políticas ambientais e saneamento básico", "meio ambiente, saneamento, esgoto, água, resíduos"),
            ("Mulheres", "Políticas para mulheres e igualdade de gênero", "mulheres, gênero, igualdade, combate à violência"),
            ("Obras, Transferências e Parcerias", "Obras públicas e parcerias", "obras, transferências, parcerias, convênios"),
            ("Orçamento Público", "Orçamento e planejamento público", "orçamento, planejamento, lei orçamentária"),
            ("Planejamento Territorial e Habitação", "Planejamento urbano e habitação", "planejamento territorial, habitação, urbanismo"),
            ("Previdência", "Previdência social e benefícios", "previdência, aposentadoria, benefícios"),
            ("Saúde", "Políticas de saúde pública", "saúde, hospital, posto de saúde, atenção básica"),
            ("Transporte e Mobilidade", "Transporte público e mobilidade urbana", "transporte, mobilidade, ônibus, metrô"),
            ("Turismo", "Políticas de turismo e lazer", "turismo, hotel, pousada, atrativo turístico")
        ]

        with sqlite3.connect(self.db_path) as conn:
            for nome, descricao, palavras_chave in areas_data:
                conn.execute("""
                    INSERT OR IGNORE INTO areas_tecnicas (nome, descricao, palavras_chave)
                    VALUES (?, ?, ?)
                """, (nome, descricao, palavras_chave))
            conn.commit()

    def insert_evento(self, evento: Dict) -> bool:
        """Insere ou atualiza um evento"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO eventos (
                        evento_id_externo, nome, data_inicio, data_fim, situacao,
                        tema, tipo_evento, local_evento, link_evento, area_tecnica,
                        fonte, data_atualizacao
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    evento['evento_id_externo'],
                    evento['nome'],
                    evento.get('data_inicio'),
                    evento.get('data_fim'),
                    evento.get('situacao'),
                    evento.get('tema'),
                    evento.get('tipo_evento'),
                    evento.get('local_evento'),
                    evento.get('link_evento'),
                    evento.get('area_tecnica'),
                    evento.get('fonte'),
                    datetime.now().isoformat()
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao inserir evento: {e}")
            return False

    def get_eventos_por_area(self, area_tecnica: str = None, limit: int = 100) -> List[Dict]:
        """Retorna eventos, opcionalmente filtrados por área"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if area_tecnica:
                    cursor = conn.execute("""
                        SELECT * FROM eventos 
                        WHERE area_tecnica = ?
                        ORDER BY data_inicio DESC
                        LIMIT ?
                    """, (area_tecnica, limit))
                else:
                    cursor = conn.execute("""
                        SELECT * FROM eventos 
                        ORDER BY data_inicio DESC
                        LIMIT ?
                    """, (limit,))
                
                eventos = []
                for row in cursor.fetchall():
                    eventos.append(dict(zip([col[0] for col in cursor.description], row)))
                
                return eventos
        except Exception as e:
            print(f"Erro ao buscar eventos: {e}")
            return []

    def get_eventos_nao_categorizados(self, limit: int = 100) -> List[Dict]:
        """Retorna eventos não categorizados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM eventos 
                    WHERE area_tecnica IS NULL OR area_tecnica = ''
                    ORDER BY data_inicio DESC
                    LIMIT ?
                """, (limit,))
                
                eventos = []
                for row in cursor.fetchall():
                    eventos.append(dict(zip([col[0] for col in cursor.description], row)))
                
                return eventos
        except Exception as e:
            print(f"Erro ao buscar eventos não categorizados: {e}")
            return []

    def get_areas_tecnicas(self) -> List[Dict]:
        """Retorna todas as áreas técnicas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM areas_tecnicas ORDER BY nome")
                
                areas = []
                for row in cursor.fetchall():
                    areas.append(dict(zip([col[0] for col in cursor.description], row)))
                
                return areas
        except Exception as e:
            print(f"Erro ao buscar áreas técnicas: {e}")
            return []

    def update_evento_situacao(self, evento_id_externo: str, situacao: str) -> bool:
        """Atualiza a situação de um evento"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE eventos 
                    SET situacao = ?, data_atualizacao = ?
                    WHERE evento_id_externo = ?
                """, (situacao, datetime.now().isoformat(), evento_id_externo))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao atualizar situação do evento: {e}")
            return False

    def update_evento_area_tecnica(self, evento_id: str, area_tecnica: str) -> bool:
        """Atualiza a área técnica de um evento"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE eventos 
                    SET area_tecnica = ?, data_atualizacao = ?
                    WHERE evento_id_externo = ?
                """, (area_tecnica, datetime.now().isoformat(), evento_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao atualizar área técnica do evento: {e}")
            return False

    def update_evento(self, evento_id: str, data: Dict) -> bool:
        """Atualiza um evento com novos dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Construir query de atualização dinamicamente
                campos_permitidos = ['situacao', 'area_tecnica', 'tema', 'nome', 'data_inicio', 'data_fim', 'tipo_evento', 'local_evento', 'link_evento']
                campos_para_atualizar = {}
                
                for campo in campos_permitidos:
                    if campo in data:
                        campos_para_atualizar[campo] = data[campo]
                
                if not campos_para_atualizar:
                    return False
                
                set_clause = ', '.join([f"{campo} = ?" for campo in campos_para_atualizar.keys()])
                valores = list(campos_para_atualizar.values()) + [datetime.now().isoformat(), evento_id]
                
                conn.execute(f"""
                    UPDATE eventos 
                    SET {set_clause}, data_atualizacao = ?
                    WHERE evento_id_externo = ?
                """, valores)
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao atualizar evento: {e}")
            return False

    def buscar_eventos(self, termo: str) -> List[Dict]:
        """Busca eventos por termo"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM eventos 
                    WHERE nome LIKE ? OR tema LIKE ? OR tipo_evento LIKE ?
                    ORDER BY data_inicio DESC
                    LIMIT 50
                """, (f'%{termo}%', f'%{termo}%', f'%{termo}%'))
                
                eventos = []
                for row in cursor.fetchall():
                    eventos.append(dict(zip([col[0] for col in cursor.description], row)))
                
                return eventos
        except Exception as e:
            print(f"Erro ao buscar eventos: {e}")
            return []

    def log_atualizacao(self, tipo: str, status: str, eventos_novos: int = 0, eventos_atualizados: int = 0, detalhes: str = None):
        """Registra log de atualização"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO logs_atualizacao (
                        tipo_atualizacao, status, eventos_novos, eventos_atualizados, detalhes
                    ) VALUES (?, ?, ?, ?, ?)
                """, (tipo, status, eventos_novos, eventos_atualizados, detalhes))
                conn.commit()
        except Exception as e:
            print(f"Erro ao registrar log: {e}")

    def get_proposicoes_por_area(self, area_tecnica: str) -> List[Dict]:
        """Retorna proposições de uma área técnica específica"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM proposicoes 
                    WHERE area_tecnica = ?
                    ORDER BY data_criacao DESC
                """, (area_tecnica,))
                
                proposicoes = []
                for row in cursor.fetchall():
                    proposicoes.append(dict(zip([col[0] for col in cursor.description], row)))
                
                return proposicoes
        except Exception as e:
            print(f"Erro ao buscar proposições: {e}")
            return []

    def insert_proposicao(self, proposicao: Dict) -> int:
        """Insere uma nova proposição"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT INTO proposicoes (
                        numero_projeto, ementa, casa_iniciadora, forma_apreciacao,
                        eixo_tematico, situacao, cabe_analise, prazo_analise,
                        analise_realizada, documento_analise, posicionamento_cnm,
                        prioridade, observacao, area_tecnica
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    proposicao['numero_projeto'],
                    proposicao['ementa'],
                    proposicao['casa_iniciadora'],
                    proposicao['forma_apreciacao'],
                    proposicao.get('eixo_tematico', ''),
                    proposicao['situacao'],
                    proposicao['cabe_analise'],
                    proposicao.get('prazo_analise', ''),
                    proposicao['analise_realizada'],
                    proposicao.get('documento_analise', ''),
                    proposicao['posicionamento_cnm'],
                    proposicao['prioridade'],
                    proposicao.get('observacao', ''),
                    proposicao['area_tecnica']
                ))
                
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Erro ao inserir proposição: {e}")
            raise

    def update_proposicao(self, proposicao_id: int, data: Dict) -> bool:
        """Atualiza uma proposição existente"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE proposicoes SET
                        numero_projeto = ?, ementa = ?, casa_iniciadora = ?, forma_apreciacao = ?,
                        eixo_tematico = ?, situacao = ?, cabe_analise = ?, prazo_analise = ?,
                        analise_realizada = ?, documento_analise = ?, posicionamento_cnm = ?,
                        prioridade = ?, observacao = ?, data_atualizacao = ?
                    WHERE id = ?
                """, (
                    data.get('numero_projeto', ''),
                    data.get('ementa', ''),
                    data.get('casa_iniciadora', ''),
                    data.get('forma_apreciacao', ''),
                    data.get('eixo_tematico', ''),
                    data.get('situacao', ''),
                    data.get('cabe_analise', ''),
                    data.get('prazo_analise', ''),
                    data.get('analise_realizada', ''),
                    data.get('documento_analise', ''),
                    data.get('posicionamento_cnm', ''),
                    data.get('prioridade', ''),
                    data.get('observacao', ''),
                    datetime.now().isoformat(),
                    proposicao_id
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao atualizar proposição: {e}")
            return False

    def delete_proposicao(self, proposicao_id: int) -> bool:
        """Exclui uma proposição"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM proposicoes WHERE id = ?", (proposicao_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao excluir proposição: {e}")
            return False

    def get_estatisticas_proposicoes(self, area_tecnica: str) -> Dict:
        """Retorna estatísticas de proposições por área técnica"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT 
                        SUM(CASE WHEN posicionamento_cnm = 'FAVORÁVEL' THEN 1 ELSE 0 END) as cnm_favoravel,
                        SUM(CASE WHEN posicionamento_cnm = 'DESFAVORÁVEL' THEN 1 ELSE 0 END) as cnm_desfavoravel,
                        SUM(CASE WHEN posicionamento_cnm = 'NEUTRO' THEN 1 ELSE 0 END) as cnm_neutro,
                        SUM(CASE WHEN posicionamento_cnm = 'FAVORÁVEL' AND aprovacao_camara = 'APROVADO' THEN 1 ELSE 0 END) as camara_cnm_favoravel,
                        SUM(CASE WHEN posicionamento_cnm = 'DESFAVORÁVEL' AND aprovacao_camara = 'APROVADO' THEN 1 ELSE 0 END) as camara_cnm_desfavoravel,
                        SUM(CASE WHEN posicionamento_cnm = 'NEUTRO' AND aprovacao_camara = 'APROVADO' THEN 1 ELSE 0 END) as camara_cnm_neutro,
                        SUM(CASE WHEN posicionamento_cnm = 'FAVORÁVEL' AND aprovacao_senado = 'APROVADO' THEN 1 ELSE 0 END) as senado_cnm_favoravel,
                        SUM(CASE WHEN posicionamento_cnm = 'DESFAVORÁVEL' AND aprovacao_senado = 'APROVADO' THEN 1 ELSE 0 END) as senado_cnm_desfavoravel,
                        SUM(CASE WHEN posicionamento_cnm = 'NEUTRO' AND aprovacao_senado = 'APROVADO' THEN 1 ELSE 0 END) as senado_cnm_neutro,
                        SUM(CASE WHEN posicionamento_cnm = 'FAVORÁVEL' AND sancionado_presidencia = 'SIM' THEN 1 ELSE 0 END) as presidencia_cnm_favoravel,
                        SUM(CASE WHEN posicionamento_cnm = 'DESFAVORÁVEL' AND sancionado_presidencia = 'SIM' THEN 1 ELSE 0 END) as presidencia_cnm_desfavoravel,
                        SUM(CASE WHEN posicionamento_cnm = 'NEUTRO' AND sancionado_presidencia = 'SIM' THEN 1 ELSE 0 END) as presidencia_cnm_neutro
                    FROM proposicoes 
                    WHERE area_tecnica = ?
                """, (area_tecnica,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'cnm_favoravel': row[0] or 0,
                        'cnm_desfavoravel': row[1] or 0,
                        'cnm_neutro': row[2] or 0,
                        'camara_cnm_favoravel': row[3] or 0,
                        'camara_cnm_desfavoravel': row[4] or 0,
                        'camara_cnm_neutro': row[5] or 0,
                        'senado_cnm_favoravel': row[6] or 0,
                        'senado_cnm_desfavoravel': row[7] or 0,
                        'senado_cnm_neutro': row[8] or 0,
                        'presidencia_cnm_favoravel': row[9] or 0,
                        'presidencia_cnm_desfavoravel': row[10] or 0,
                        'presidencia_cnm_neutro': row[11] or 0
                    }
                else:
                    return {
                        'cnm_favoravel': 0,
                        'cnm_desfavoravel': 0,
                        'cnm_neutro': 0,
                        'camara_cnm_favoravel': 0,
                        'camara_cnm_desfavoravel': 0,
                        'camara_cnm_neutro': 0,
                        'senado_cnm_favoravel': 0,
                        'senado_cnm_desfavoravel': 0,
                        'senado_cnm_neutro': 0,
                        'presidencia_cnm_favoravel': 0,
                        'presidencia_cnm_desfavoravel': 0,
                        'presidencia_cnm_neutro': 0
                    }
        except Exception as e:
            print(f"Erro ao buscar estatísticas: {e}")
            return {
                'cnm_favoravel': 0,
                'cnm_desfavoravel': 0,
                'cnm_neutro': 0,
                'camara_cnm_favoravel': 0,
                'camara_cnm_desfavoravel': 0,
                'camara_cnm_neutro': 0,
                'senado_cnm_favoravel': 0,
                'senado_cnm_desfavoravel': 0,
                'senado_cnm_neutro': 0,
                'presidencia_cnm_favoravel': 0,
                'presidencia_cnm_desfavoravel': 0,
                'presidencia_cnm_neutro': 0
            }
