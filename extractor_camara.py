import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
import re

class CamaraExtractor:
    def __init__(self):
        self.base_url = "https://dadosabertos.camara.leg.br/api/v2"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ETL-Agenda-Congresso/1.0'
        })
    
    def get_eventos_comissoes(self, data_inicio: str = None, data_fim: str = None) -> List[Dict]:
        """Extrai eventos das comissões da Câmara"""
        if not data_inicio:
            data_inicio = datetime.now().strftime("%Y-%m-%d")
        if not data_fim:
            data_fim = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        eventos = []
        
        # Buscar comissões
        comissoes_url = f"{self.base_url}/orgaos"
        params = {
            'sigla': 'CCJC,CD,CE,CFT,CI,CMO,CREDN,CTASP,CUTI',
            'dataInicio': data_inicio,
            'dataFim': data_fim
        }
        
        try:
            response = self.session.get(comissoes_url, params=params)
            response.raise_for_status()
            comissoes = response.json()['dados']
            
            for comissao in comissoes:
                eventos_comissao = self._get_eventos_comissao(comissao['id'], data_inicio, data_fim)
                eventos.extend(eventos_comissao)
                
        except Exception as e:
            print(f"Erro ao buscar eventos das comissões: {e}")
        
        return eventos
    
    def _get_eventos_comissao(self, comissao_id: int, data_inicio: str, data_fim: str) -> List[Dict]:
        """Busca eventos de uma comissão específica"""
        eventos = []
        
        url = f"{self.base_url}/orgaos/{comissao_id}/eventos"
        params = {
            'dataInicio': data_inicio,
            'dataFim': data_fim,
            'itens': 100
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            dados = response.json()['dados']
            
            for evento in dados:
                evento_processado = self._processar_evento_camara(evento)
                if evento_processado:
                    eventos.append(evento_processado)
                    
        except Exception as e:
            print(f"Erro ao buscar eventos da comissão {comissao_id}: {e}")
        
        return eventos
    
    def get_sessoes_plenario(self, data_inicio: str = None, data_fim: str = None) -> List[Dict]:
        """Extrai sessões do plenário"""
        if not data_inicio:
            data_inicio = datetime.now().strftime("%Y-%m-%d")
        if not data_fim:
            data_fim = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        eventos = []
        url = f"{self.base_url}/eventos"
        params = {
            'dataInicio': data_inicio,
            'dataFim': data_fim,
            'tipo': 'Sessão Plenária',
            'itens': 100
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            dados = response.json()['dados']
            
            for evento in dados:
                evento_processado = self._processar_evento_camara(evento)
                if evento_processado:
                    eventos.append(evento_processado)
                    
        except Exception as e:
            print(f"Erro ao buscar sessões do plenário: {e}")
        
        return eventos
    
    def _processar_evento_camara(self, evento_raw: Dict) -> Dict:
        """Processa evento da Câmara para o formato padrão"""
        try:
            # Formatar data e hora
            data_inicio = self._formatar_data_hora(evento_raw.get('dataHoraInicio'))
            data_fim = self._formatar_data_hora(evento_raw.get('dataHoraFim'))
            
            # Determinar situação
            situacao = self._determinar_situacao(evento_raw.get('situacao'))
            
            # Determinar tipo do evento
            tipo_evento = self._determinar_tipo_evento(evento_raw.get('tipo'))
            
            # Formatar local
            local = self._formatar_local(evento_raw.get('localCamara'))
            
            evento = {
                'evento_id_externo': f"camara_{evento_raw.get('id')}",
                'nome': evento_raw.get('titulo', 'Evento sem título'),
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'situacao': situacao,
                'tema': evento_raw.get('tema'),
                'tipo_evento': tipo_evento,
                'local_evento': local,
                'link_evento': f"https://www.camara.leg.br/eventos/{evento_raw.get('id')}",
                'area_tecnica': None,  # Será categorizado posteriormente
                'fonte': 'camara'
            }
            
            return evento
            
        except Exception as e:
            print(f"Erro ao processar evento da Câmara: {e}")
            return None
    
    def _formatar_data_hora(self, data_hora_str: str) -> str:
        """Formata data e hora no formato especificado"""
        if not data_hora_str:
            return ""
        
        try:
            dt = datetime.fromisoformat(data_hora_str.replace('Z', '+00:00'))
            data = dt.strftime("%d/%m/%Y")
            hora = dt.strftime("às %H:%M")
            return f"{data} {hora}"
        except:
            return data_hora_str
    
    def _determinar_situacao(self, situacao_raw: str) -> str:
        """Determina situação do evento"""
        if not situacao_raw:
            return "Em Andamento"
        
        situacao_lower = situacao_raw.lower()
        if 'encerrada' in situacao_lower or 'finalizada' in situacao_lower:
            return "Encerrada"
        elif 'cancelada' in situacao_lower:
            return "Cancelada"
        else:
            return "Em Andamento"
    
    def _determinar_tipo_evento(self, tipo_raw: str) -> str:
        """Determina tipo do evento"""
        if not tipo_raw:
            return "Evento"
        
        tipo_lower = tipo_raw.lower()
        if 'audiência' in tipo_lower:
            return "Audiência Pública"
        elif 'sessão' in tipo_lower:
            return "Sessão"
        elif 'reunião' in tipo_lower:
            return "Reunião"
        elif 'palestra' in tipo_lower:
            return "Palestra"
        else:
            return tipo_raw
    
    def _formatar_local(self, local_raw: str) -> str:
        """Formata local do evento"""
        if not local_raw:
            return "Local não informado"
        
        return f"{local_raw} - Câmara dos Deputados"
