import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
from bs4 import BeautifulSoup
import re

class SenadoExtractor:
    def __init__(self):
        self.base_url = "https://www12.senado.leg.br/dados-abertos"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ETL-Agenda-Congresso/1.0'
        })
    
    def get_eventos_comissoes(self, data_inicio: str = None, data_fim: str = None) -> List[Dict]:
        """Extrai eventos das comissões do Senado"""
        if not data_inicio:
            data_inicio = datetime.now().strftime("%Y-%m-%d")
        if not data_fim:
            data_fim = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        eventos = []
        
        # URLs das comissões principais do Senado
        comissoes_urls = [
            "https://www12.senado.leg.br/dados-abertos/api/agenda/comissoes",
            "https://www12.senado.leg.br/dados-abertos/api/agenda/plenario"
        ]
        
        for url in comissoes_urls:
            try:
                params = {
                    'dataInicio': data_inicio,
                    'dataFim': data_fim
                }
                
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                if response.headers.get('content-type', '').startswith('application/json'):
                    dados = response.json()
                    eventos.extend(self._processar_eventos_senado(dados))
                else:
                    # Se não for JSON, tentar parsear HTML
                    eventos.extend(self._parsear_html_senado(response.text))
                    
            except Exception as e:
                print(f"Erro ao buscar eventos do Senado em {url}: {e}")
        
        return eventos
    
    def get_agenda_geral(self, data_inicio: str = None, data_fim: str = None) -> List[Dict]:
        """Extrai agenda geral do Senado"""
        if not data_inicio:
            data_inicio = datetime.now().strftime("%Y-%m-%d")
        if not data_fim:
            data_fim = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        eventos = []
        
        # URL da agenda geral do Senado
        url = "https://www12.senado.leg.br/dados-abertos/api/agenda"
        
        try:
            params = {
                'dataInicio': data_inicio,
                'dataFim': data_fim
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            if response.headers.get('content-type', '').startswith('application/json'):
                dados = response.json()
                eventos.extend(self._processar_eventos_senado(dados))
            else:
                eventos.extend(self._parsear_html_senado(response.text))
                
        except Exception as e:
            print(f"Erro ao buscar agenda geral do Senado: {e}")
        
        return eventos
    
    def _processar_eventos_senado(self, dados: Dict) -> List[Dict]:
        """Processa eventos do Senado em formato JSON"""
        eventos = []
        
        try:
            # Estrutura pode variar dependendo da API
            if 'dados' in dados:
                eventos_raw = dados['dados']
            elif 'eventos' in dados:
                eventos_raw = dados['eventos']
            else:
                eventos_raw = dados
            
            if isinstance(eventos_raw, list):
                for evento_raw in eventos_raw:
                    evento_processado = self._processar_evento_senado(evento_raw)
                    if evento_processado:
                        eventos.append(evento_processado)
                        
        except Exception as e:
            print(f"Erro ao processar eventos JSON do Senado: {e}")
        
        return eventos
    
    def _parsear_html_senado(self, html_content: str) -> List[Dict]:
        """Parseia HTML da agenda do Senado quando API não está disponível"""
        eventos = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Buscar por elementos que possam conter eventos
            # Esta é uma implementação genérica que pode precisar de ajustes
            elementos_evento = soup.find_all(['div', 'tr'], class_=re.compile(r'evento|agenda|reuniao'))
            
            for elemento in elementos_evento:
                evento = self._extrair_evento_html(elemento)
                if evento:
                    eventos.append(evento)
                    
        except Exception as e:
            print(f"Erro ao parsear HTML do Senado: {e}")
        
        return eventos
    
    def _extrair_evento_html(self, elemento) -> Dict:
        """Extrai informações de evento de um elemento HTML"""
        try:
            # Tentar extrair informações básicas
            titulo = elemento.find(['h3', 'h4', 'strong'])
            titulo_texto = titulo.get_text().strip() if titulo else "Evento do Senado"
            
            # Tentar extrair data
            data_element = elemento.find(text=re.compile(r'\d{2}/\d{2}/\d{4}'))
            data_texto = data_element.strip() if data_element else ""
            
            # Tentar extrair hora
            hora_element = elemento.find(text=re.compile(r'\d{2}:\d{2}'))
            hora_texto = hora_element.strip() if hora_element else ""
            
            evento = {
                'evento_id_externo': f"senado_{hash(titulo_texto)}",
                'nome': titulo_texto,
                'data_inicio': f"{data_texto} {hora_texto}" if data_texto and hora_texto else "",
                'data_fim': "",
                'situacao': "Em Andamento",
                'tema': None,
                'tipo_evento': "Evento do Senado",
                'local_evento': "Senado Federal",
                'link_evento': "",
                'area_tecnica': None,
                'fonte': 'senado'
            }
            
            return evento
            
        except Exception as e:
            print(f"Erro ao extrair evento HTML: {e}")
            return None
    
    def _processar_evento_senado(self, evento_raw: Dict) -> Dict:
        """Processa evento do Senado para o formato padrão"""
        try:
            # Formatar data e hora
            data_inicio = self._formatar_data_hora_senado(evento_raw.get('dataInicio') or evento_raw.get('data'))
            data_fim = self._formatar_data_hora_senado(evento_raw.get('dataFim'))
            
            # Determinar situação
            situacao = self._determinar_situacao_senado(evento_raw.get('situacao'))
            
            # Determinar tipo do evento
            tipo_evento = self._determinar_tipo_evento_senado(evento_raw.get('tipo'))
            
            evento = {
                'evento_id_externo': f"senado_{evento_raw.get('id', hash(evento_raw.get('titulo', '')))}",
                'nome': evento_raw.get('titulo', evento_raw.get('nome', 'Evento do Senado')),
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'situacao': situacao,
                'tema': evento_raw.get('tema'),
                'tipo_evento': tipo_evento,
                'local_evento': evento_raw.get('local', 'Senado Federal'),
                'link_evento': evento_raw.get('link', ''),
                'area_tecnica': None,  # Será categorizado posteriormente
                'fonte': 'senado'
            }
            
            return evento
            
        except Exception as e:
            print(f"Erro ao processar evento do Senado: {e}")
            return None
    
    def _formatar_data_hora_senado(self, data_hora_str: str) -> str:
        """Formata data e hora do Senado no formato especificado"""
        if not data_hora_str:
            return ""
        
        try:
            # Tentar diferentes formatos de data
            formatos = [
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%d/%m/%Y %H:%M",
                "%d/%m/%Y"
            ]
            
            for formato in formatos:
                try:
                    dt = datetime.strptime(data_hora_str, formato)
                    data = dt.strftime("%d/%m/%Y")
                    hora = dt.strftime("às %H:%M")
                    return f"{data} {hora}"
                except:
                    continue
            
            return data_hora_str
            
        except:
            return data_hora_str
    
    def _determinar_situacao_senado(self, situacao_raw: str) -> str:
        """Determina situação do evento do Senado"""
        if not situacao_raw:
            return "Em Andamento"
        
        situacao_lower = situacao_raw.lower()
        if 'encerrada' in situacao_lower or 'finalizada' in situacao_lower:
            return "Encerrada"
        elif 'cancelada' in situacao_lower:
            return "Cancelada"
        else:
            return "Em Andamento"
    
    def _determinar_tipo_evento_senado(self, tipo_raw: str) -> str:
        """Determina tipo do evento do Senado"""
        if not tipo_raw:
            return "Evento do Senado"
        
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
