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
        """Extrai eventos das comissões da Câmara - apenas Sessões e Reuniões legislativas"""
        if not data_inicio:
            data_inicio = datetime.now().strftime("%Y-%m-%d")
        if not data_fim:
            data_fim = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        eventos = []
        
        # Buscar comissões legislativas principais
        comissoes_legislativas = [
            'CCJC',  # Constituição e Justiça
            'CE',    # Educação
            'CFT',   # Finanças e Tributação
            'CMO',   # Orçamento
            'CREDN', # Relações Exteriores
            'CTASP', # Trabalho
            'CME',   # Minas e Energia
            'CSSF',  # Seguridade Social e Família
            'CVT'    # Viação e Transportes
        ]
        
        for sigla in comissoes_legislativas:
            try:
                # Buscar comissão por sigla
                comissao = self._buscar_comissao_por_sigla(sigla)
                if comissao:
                    eventos_comissao = self._get_eventos_comissao(comissao['id'], data_inicio, data_fim)
                    eventos.extend(eventos_comissao)
                    
            except Exception as e:
                print(f"Erro ao buscar eventos da comissão {sigla}: {e}")
        
        return eventos
    
    def _buscar_comissao_por_sigla(self, sigla: str) -> Dict:
        """Busca comissão por sigla"""
        try:
            url = f"{self.base_url}/orgaos"
            params = {'sigla': sigla}
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            dados = response.json()['dados']
            
            if dados:
                return dados[0]
                
        except Exception as e:
            print(f"Erro ao buscar comissão {sigla}: {e}")
        
        return None
    
    def _get_eventos_comissao(self, comissao_id: int, data_inicio: str, data_fim: str) -> List[Dict]:
        """Busca eventos de uma comissão específica (apenas Reuniões)"""
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
                # Filtrar apenas Reuniões legislativas (excluir audiências/solenidades)
                if self._eh_reuniao_legislativa(evento):
                    evento_processado = self._processar_evento_camara(evento)
                    if evento_processado:
                        eventos.append(evento_processado)
                    
        except Exception as e:
            print(f"Erro ao buscar eventos da comissão {comissao_id}: {e}")
        
        return eventos
    
    def _eh_reuniao_legislativa(self, evento: Dict) -> bool:
        """Retorna True somente para Reuniões legislativas."""
        tipo_evento = (evento.get('tipo') or '').lower()
        titulo = (evento.get('titulo') or '').lower()
        
        # APENAS Reuniões
        if 'reuni' in tipo_evento or 'reuni' in titulo:
            # EXCLUIR TODOS os outros tipos de eventos
            if any(p in titulo for p in ['solenidade', 'homenagem', 'lançamento', 'sessão solene', 'audiência', 'audiencia', 'conferência', 'conferencia', 'seminário', 'seminario', 'cúpula', 'cupula', 'palestra', 'exposição', 'exposicao', 'visita', 'debate', 'workshop', 'curso', 'simpósio', 'simposio']):
                return False
            return True
        return False
    
    def get_sessoes_plenario(self, data_inicio: str = None, data_fim: str = None) -> List[Dict]:
        """Extrai sessões do plenário (apenas Sessões)"""
        if not data_inicio:
            data_inicio = datetime.now().strftime("%Y-%m-%d")
        if not data_fim:
            data_fim = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        eventos = []
        
        # Buscar eventos do plenário
        url = f"{self.base_url}/eventos"
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
                # Filtrar apenas sessões do plenário
                if self._eh_sessao_plenario(evento):
                    evento_processado = self._processar_evento_camara(evento)
                    if evento_processado:
                        eventos.append(evento_processado)
                        
        except Exception as e:
            print(f"Erro ao buscar sessões do plenário: {e}")
        
        return eventos
    
    def _eh_sessao_plenario(self, evento: Dict) -> bool:
        """Verifica se o evento é uma sessão do plenário"""
        tipo_evento = (evento.get('tipo') or '').lower()
        titulo = (evento.get('titulo') or '').lower()
        
        # APENAS Sessões
        if 'sess' in tipo_evento or 'sessão' in titulo or 'plenár' in titulo:
            # EXCLUIR TODOS os outros tipos de eventos
            if any(p in titulo for p in ['solene', 'solenidade', 'homenagem', 'audiência', 'audiencia', 'conferência', 'conferencia', 'seminário', 'seminario', 'cúpula', 'cupula', 'palestra', 'exposição', 'exposicao', 'visita', 'debate', 'workshop', 'curso', 'simpósio', 'simposio']):
                return False
            return True
        
        return False
    
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
            
            # Obter título real do evento
            titulo = self._obter_titulo_real(evento_raw)
            
            # Gerar link real do evento
            link_evento = self._gerar_link_evento(evento_raw)
            
            # Comissão e finalidade (se disponíveis)
            orgao = evento_raw.get('orgao') or {}
            comissao = orgao.get('nome')
            descricao = (evento_raw.get('descricao') or '').strip()
            finalidade = None
            if descricao:
                # usar primeira frase longa como finalidade
                partes = re.split(r'[\.!?]', descricao)
                for p in partes:
                    p = p.strip()
                    if len(p) > 20:
                        finalidade = p
                        break
                if not finalidade:
                    finalidade = descricao
            
            evento = {
                'evento_id_externo': f"camara_{evento_raw.get('id')}",
                'nome': titulo,
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'situacao': situacao,
                'tema': evento_raw.get('tema') or self._extrair_tema_evento(evento_raw),
                'tipo_evento': tipo_evento,
                'local_evento': local,
                'link_evento': link_evento,
                'area_tecnica': None,  # Será categorizado posteriormente
                'fonte': 'Camara',
                'comissao': comissao,
                'finalidade': finalidade
            }
            
            return evento
            
        except Exception as e:
            print(f"Erro ao processar evento da Câmara: {e}")
            return None
    
    def _obter_titulo_real(self, evento_raw: Dict) -> str:
        """Obtém o título real do evento"""
        titulo = evento_raw.get('titulo', '')
        if titulo:
            return titulo
        # fallback
        tipo = evento_raw.get('tipo', 'Evento')
        orgao = evento_raw.get('orgao', {}).get('nome', 'Câmara dos Deputados')
        return f"{tipo} - {orgao}"
    
    def _gerar_link_evento(self, evento_raw: Dict) -> str:
        """Gera link real para o evento"""
        evento_id = evento_raw.get('id')
        if evento_id:
            return f"https://www.camara.leg.br/eventos/{evento_id}"
        return "https://www.camara.leg.br/eventos"
    
    def _extrair_tema_evento(self, evento_raw: Dict) -> str:
        """Extrai tema do evento baseado em informações disponíveis"""
        tema = evento_raw.get('tema')
        if tema:
            return tema
        titulo = evento_raw.get('titulo', '')
        descricao = evento_raw.get('descricao', '')
        texto_completo = f"{titulo} {descricao}".lower()
        temas_keywords = {
            'Educação': ['educação', 'escola', 'universidade', 'ensino'],
            'Saúde': ['saúde', 'hospital', 'medicamento', 'vacina'],
            'Meio Ambiente e Saneamento': ['meio ambiente', 'sustentabilidade', 'poluição', 'clima'],
            'Economia': ['economia', 'finanças', 'orçamento', 'imposto'],
            'Segurança': ['segurança', 'polícia', 'crime', 'violência'],
            'Infraestrutura': ['infraestrutura', 'obra', 'construção', 'transporte'],
            'Jurídico': ['legislação', 'lei', 'direito', 'constituição']
        }
        for tema, keywords in temas_keywords.items():
            if any(keyword in texto_completo for keyword in keywords):
                return tema
        return "Jurídico"
    
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
            return "Agendada"
        s = situacao_raw.lower()
        if 'encerrad' in s:
            return "Encerrada"
        if 'cancelad' in s:
            return "Cancelada"
        if 'agendad' in s:
            return "Agendada"
        return "Em Andamento"
    
    def _determinar_tipo_evento(self, tipo_raw: str) -> str:
        """Determina tipo do evento"""
        if not tipo_raw:
            return "Evento"
        tipo_lower = tipo_raw.lower()
        if 'sess' in tipo_lower:
            return "Sessão"
        if 'reuni' in tipo_lower:
            return "Reunião"
        return tipo_raw
    
    def _formatar_local(self, local_raw) -> str:
        """Formata local do evento"""
        if not local_raw:
            return "Câmara dos Deputados"
        if isinstance(local_raw, dict):
            nome = local_raw.get('nome')
            predio = local_raw.get('predio')
            sala = local_raw.get('sala')
            andar = local_raw.get('andar')
            partes = []
            if nome: partes.append(nome)
            if predio: partes.append(f"Prédio {predio}")
            if andar: partes.append(f"{andar}º andar")
            if sala: partes.append(f"Sala {sala}")
            return f"{', '.join(partes)} - Câmara dos Deputados" if partes else "Câmara dos Deputados"
        if isinstance(local_raw, str):
            return f"{local_raw} - Câmara dos Deputados"
        return "Câmara dos Deputados"
