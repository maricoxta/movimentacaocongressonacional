import re
from typing import Dict, List, Optional
from etl.database_manager import DatabaseManager

class CategorizadorEventos:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.areas_tecnicas = self._carregar_areas_tecnicas()
    
    def _carregar_areas_tecnicas(self) -> List[Dict]:
        """Carrega áreas técnicas do banco de dados"""
        return self.db_manager.get_areas_tecnicas()
    
    def categorizar_evento(self, evento: Dict) -> Optional[str]:
        """Categoriza um evento em uma área técnica baseado no conteúdo"""
        if not evento.get('nome'):
            return None
        
        texto_analise = self._preparar_texto_analise(evento)
        melhor_area = None
        melhor_score = 0
        
        for area in self.areas_tecnicas:
            score = self._calcular_score_area(texto_analise, area)
            if score > melhor_score:
                melhor_score = score
                melhor_area = area['nome']
        
        # Reduzir threshold para categorizar mais eventos
        if melhor_score >= 0.1:  # Reduzido de 0.3 para 0.1
            return melhor_area
        
        # Se não encontrou área específica, tentar categorização por contexto
        area_contexto = self._categorizar_por_contexto(evento)
        if area_contexto:
            return area_contexto
        
        return None
    
    def _preparar_texto_analise(self, evento: Dict) -> str:
        """Prepara texto para análise combinando diferentes campos"""
        campos = [
            evento.get('nome', ''),
            evento.get('tema', ''),
            evento.get('tipo_evento', ''),
            evento.get('local_evento', ''),
            evento.get('fonte', '')  # Adicionar fonte como contexto
        ]
        
        texto = ' '.join([campo for campo in campos if campo])
        return texto.lower()
    
    def _calcular_score_area(self, texto: str, area: Dict) -> float:
        """Calcula score de relevância para uma área técnica"""
        palavras_chave = area.get('palavras_chave', '').split(',')
        score = 0
        total_palavras = len(palavras_chave)
        
        if total_palavras == 0:
            return 0
        
        for palavra in palavras_chave:
            palavra = palavra.strip().lower()
            if palavra:
                # Busca por palavra exata
                if palavra in texto:
                    score += 1
                # Busca por variações
                elif self._buscar_variacoes(palavra, texto):
                    score += 0.8
                # Busca por palavras relacionadas
                elif self._buscar_palavras_relacionadas(palavra, texto):
                    score += 0.5
        
        return score / total_palavras
    
    def _buscar_variacoes(self, palavra: str, texto: str) -> bool:
        """Busca por variações da palavra no texto"""
        # Remover acentos para comparação
        palavra_sem_acento = self._remover_acentos(palavra)
        texto_sem_acento = self._remover_acentos(texto)
        
        # Buscar palavra exata
        if palavra_sem_acento in texto_sem_acento:
            return True
        
        # Buscar por radicais
        radical = palavra_sem_acento[:4]  # Primeiras 4 letras
        if len(radical) >= 3 and radical in texto_sem_acento:
            return True
        
        return False
    
    def _buscar_palavras_relacionadas(self, palavra: str, texto: str) -> bool:
        """Busca por palavras relacionadas"""
        palavras_relacionadas = {
            'educação': ['escola', 'universidade', 'ensino', 'aluno', 'professor'],
            'saúde': ['hospital', 'medicamento', 'vacina', 'doença', 'tratamento'],
            'meio ambiente': ['sustentabilidade', 'poluição', 'natureza', 'ecologia'],
            'economia': ['finanças', 'orçamento', 'imposto', 'dinheiro', 'mercado'],
            'segurança': ['polícia', 'crime', 'violência', 'proteção'],
            'infraestrutura': ['obra', 'construção', 'transporte', 'estrada'],
            'cultura': ['arte', 'teatro', 'museu', 'patrimônio'],
            'esporte': ['atividade física', 'competição', 'treino'],
            'tecnologia': ['digital', 'inovação', 'software', 'internet']
        }
        
        if palavra in palavras_relacionadas:
            for palavra_rel in palavras_relacionadas[palavra]:
                if palavra_rel in texto:
                    return True
        
        return False
    
    def _categorizar_por_contexto(self, evento: Dict) -> Optional[str]:
        """Categoriza evento por contexto quando informações são limitadas"""
        texto = self._preparar_texto_analise(evento)
        fonte = evento.get('fonte', '').lower()
        tipo_evento = evento.get('tipo_evento', '').lower()
        local = evento.get('local_evento', '').lower()
        
        # Categorização por tipo de evento
        if 'audiência' in tipo_evento:
            return self._categorizar_audiencia_publica(texto)
        elif 'sessão' in tipo_evento:
            return self._categorizar_sessao_plenario(texto)
        elif 'reunião' in tipo_evento:
            return self._categorizar_reuniao_comissao(texto)
        
        # Categorização por local
        if 'plenário' in local:
            return self._categorizar_por_plenario(texto)
        elif 'comissão' in local:
            return self._categorizar_por_comissao(texto)
        
        # Categorização por fonte
        if fonte == 'camara':
            return self._categorizar_evento_camara(evento)
        elif fonte == 'senado':
            return self._categorizar_evento_senado(evento)
        
        return None
    
    def _categorizar_audiencia_publica(self, texto: str) -> str:
        """Categoriza audiência pública por tema"""
        temas_audiencia = {
            'Educação': ['educação', 'escola', 'universidade', 'ensino'],
            'Saúde': ['saúde', 'hospital', 'medicamento', 'vacina'],
            'Meio Ambiente e Saneamento': ['meio ambiente', 'saneamento', 'água', 'esgoto'],
            'Transporte e Mobilidade': ['transporte', 'mobilidade', 'trânsito'],
            'Finanças': ['finanças', 'orçamento', 'imposto', 'tributo'],
            'Jurídico': ['jurídico', 'legislação', 'lei', 'direito']
        }
        
        for area, keywords in temas_audiencia.items():
            if any(keyword in texto for keyword in keywords):
                return area
        
        return 'Jurídico'  # Default para audiências públicas
    
    def _categorizar_sessao_plenario(self, texto: str) -> str:
        """Categoriza sessão do plenário"""
        return 'Jurídico'  # Sessões do plenário geralmente são jurídicas
    
    def _categorizar_reuniao_comissao(self, texto: str) -> str:
        """Categoriza reunião de comissão"""
        # Tentar identificar área da comissão
        comissoes_areas = {
            'Educação': ['educação', 'cultura', 'esporte'],
            'Saúde': ['saúde', 'previdência'],
            'Meio Ambiente e Saneamento': ['meio ambiente', 'agricultura'],
            'Finanças': ['finanças', 'orçamento', 'tributação'],
            'Jurídico': ['constituição', 'justiça', 'cidadania'],
            'Transporte e Mobilidade': ['transporte', 'infraestrutura']
        }
        
        for area, keywords in comissoes_areas.items():
            if any(keyword in texto for keyword in keywords):
                return area
        
        return 'Jurídico'  # Default para comissões
    
    def _categorizar_por_plenario(self, texto: str) -> str:
        """Categoriza eventos do plenário"""
        return 'Jurídico'
    
    def _categorizar_por_comissao(self, texto: str) -> str:
        """Categoriza eventos de comissão"""
        return self._categorizar_reuniao_comissao(texto)
    
    def _categorizar_evento_camara(self, evento: Dict) -> str:
        """Categoriza evento da Câmara por padrões conhecidos"""
        # Se é um evento genérico da Câmara, categorizar como Jurídico
        # pois geralmente são relacionados a processos legislativos
        return 'Jurídico'
    
    def _categorizar_evento_senado(self, evento: Dict) -> str:
        """Categoriza evento do Senado por padrões conhecidos"""
        # Se é um evento genérico do Senado, categorizar como Jurídico
        return 'Jurídico'
    
    def _remover_acentos(self, texto: str) -> str:
        """Remove acentos do texto"""
        import unicodedata
        return ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if not unicodedata.combining(c)
        )
    
    def categorizar_lote(self, eventos: List[Dict]) -> List[Dict]:
        """Categoriza uma lista de eventos"""
        eventos_categorizados = []
        
        for evento in eventos:
            area_tecnica = self.categorizar_evento(evento)
            if area_tecnica:
                evento['area_tecnica'] = area_tecnica
            eventos_categorizados.append(evento)
        
        return eventos_categorizados
    
    def atualizar_categorizacao_evento(self, evento_id: str, area_tecnica: str) -> bool:
        """Atualiza a categorização de um evento específico"""
        try:
            with self.db_manager.db_path as conn:
                conn.execute("""
                    UPDATE eventos 
                    SET area_tecnica = ?, data_atualizacao = CURRENT_TIMESTAMP
                    WHERE evento_id_externo = ?
                """, (area_tecnica, evento_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Erro ao atualizar categorização: {e}")
            return False
    
    def get_eventos_por_area(self, area_tecnica: str) -> List[Dict]:
        """Retorna eventos de uma área técnica específica"""
        return self.db_manager.get_eventos_por_area(area_tecnica)
    
    def get_estatisticas_areas(self) -> Dict:
        """Retorna estatísticas de eventos por área técnica"""
        estatisticas = {}
        
        for area in self.areas_tecnicas:
            eventos = self.get_eventos_por_area(area['nome'])
            estatisticas[area['nome']] = {
                'total_eventos': len(eventos),
                'eventos_andamento': len([e for e in eventos if e['situacao'] == 'Em Andamento']),
                'eventos_encerrados': len([e for e in eventos if e['situacao'] == 'Encerrada']),
                'eventos_cancelados': len([e for e in eventos if e['situacao'] == 'Cancelada'])
            }
        
        return estatisticas


