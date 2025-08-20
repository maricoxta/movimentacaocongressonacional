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
        
        # Só categoriza se o score for significativo
        if melhor_score >= 0.3:
            return melhor_area
        
        return None
    
    def _preparar_texto_analise(self, evento: Dict) -> str:
        """Prepara texto para análise combinando diferentes campos"""
        campos = [
            evento.get('nome', ''),
            evento.get('tema', ''),
            evento.get('tipo_evento', ''),
            evento.get('local_evento', '')
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
