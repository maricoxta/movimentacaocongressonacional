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
        """Extrai eventos das comissões da Câmara - apenas atividades legislativas"""
        if not data_inicio:
            data_inicio = datetime.now().strftime("%Y-%m-%d")
        if not data_fim:
            data_fim = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        eventos = []
        
        # Buscar comissões legislativas principais
        comissoes_legislativas = [
            'CCJC',  # Constituição e Justiça
            'CD',    # Defesa Nacional
            'CE',    # Educação
            'CFT',   # Finanças e Tributação
            'CI',    # Indústria
            'CMO',   # Orçamento
            'CREDN', # Relações Exteriores
            'CTASP', # Trabalho
            'CUTI'   # Urbanismo
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
                # Filtrar apenas atividades legislativas
                if self._eh_atividade_legislativa(evento):
                    evento_processado = self._processar_evento_camara(evento)
                    if evento_processado:
                        eventos.append(evento_processado)
                    
        except Exception as e:
            print(f"Erro ao buscar eventos da comissão {comissao_id}: {e}")
        
        return eventos
    
    def _eh_atividade_legislativa(self, evento: Dict) -> bool:
        """Verifica se o evento é uma atividade legislativa"""
        tipo_evento = evento.get('tipo', '').lower()
        titulo = evento.get('titulo', '').lower()
        
        # Tipos de atividades legislativas
        atividades_legislativas = [
            'audiência pública',
            'reunião',
            'sessão',
            'debate',
            'votação',
            'apreciação',
            'discussão',
            'deliberação'
        ]
        
        # Verificar se o tipo do evento é legislativo
        for atividade in atividades_legislativas:
            if atividade in tipo_evento:
                return True
        
        # Verificar se o título indica atividade legislativa
        palavras_legislativas = [
            'projeto', 'lei', 'proposta', 'matéria', 'votação', 'apreciação',
            'debate', 'discussão', 'deliberação', 'audiência', 'reunião'
        ]
        
        for palavra in palavras_legislativas:
            if palavra in titulo:
                return True
        
        return False
    
    def get_sessoes_plenario(self, data_inicio: str = None, data_fim: str = None) -> List[Dict]:
        """Extrai sessões do plenário - apenas atividades legislativas"""
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
        tipo_evento = evento.get('tipo', '').lower()
        titulo = evento.get('titulo', '').lower()
        
        # Verificar se é sessão do plenário
        if 'sessão' in tipo_evento and 'plenária' in tipo_evento:
            return True
        
        if 'plenário' in titulo or 'sessão plenária' in titulo:
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
                'fonte': 'camara'
            }
            
            return evento
            
        except Exception as e:
            print(f"Erro ao processar evento da Câmara: {e}")
            return None
    
    def _obter_titulo_real(self, evento_raw: Dict) -> str:
        """Obtém o título real do evento"""
        titulo = evento_raw.get('titulo', '')
        
        # Se o título está vazio ou é genérico, tentar extrair de outros campos
        if not titulo or titulo.strip() == '' or 'evento' in titulo.lower():
            # Tentar extrair de descrição
            descricao = evento_raw.get('descricao', '')
            if descricao and len(descricao) > 10:
                # Pegar primeira linha da descrição como título
                linhas = descricao.split('\n')
                for linha in linhas:
                    linha = linha.strip()
                    if linha and len(linha) > 10:
                        return linha[:200]  # Limitar a 200 caracteres
            
            # Tentar extrair de tema
            tema = evento_raw.get('tema', '')
            if tema:
                return f"{tema} - {evento_raw.get('orgao', {}).get('nome', 'Câmara dos Deputados')}"
            
            # Gerar título baseado no tipo e órgão
            tipo = evento_raw.get('tipo', 'Evento')
            orgao = evento_raw.get('orgao', {}).get('nome', 'Câmara dos Deputados')
            return f"{tipo} - {orgao}"
        
        return titulo
    
    def _gerar_link_evento(self, evento_raw: Dict) -> str:
        """Gera link real para o evento"""
        evento_id = evento_raw.get('id')
        
        if evento_id:
            # Link para evento específico da Câmara
            return f"https://www.camara.leg.br/eventos/{evento_id}"
        
        # Link genérico da agenda da Câmara
        return "https://www.camara.leg.br/eventos"
    
    def _extrair_tema_evento(self, evento_raw: Dict) -> str:
        """Extrai tema do evento baseado em informações disponíveis"""
        tema = evento_raw.get('tema')
        if tema:
            return tema
        
        # Tentar extrair tema do título ou descrição
        titulo = evento_raw.get('titulo', '')
        descricao = evento_raw.get('descricao', '')
        
        texto_completo = f"{titulo} {descricao}".lower()
        
        # Palavras-chave para identificar temas
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
        
        return "Assuntos Gerais"
    
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
    
    def _formatar_local(self, local_raw) -> str:
        """Formata local do evento"""
        if not local_raw:
            return "Local não informado - Câmara dos Deputados"
        
        # Se local_raw é um dicionário
        if isinstance(local_raw, dict):
            nome = local_raw.get('nome')
            predio = local_raw.get('predio')
            sala = local_raw.get('sala')
            andar = local_raw.get('andar')
            
            partes = []
            if nome:
                partes.append(nome)
            if predio:
                partes.append(f"Prédio {predio}")
            if andar:
                partes.append(f"{andar}º andar")
            if sala:
                partes.append(f"Sala {sala}")
            
            if partes:
                return f"{', '.join(partes)} - Câmara dos Deputados"
            else:
                return "Câmara dos Deputados"
        
        # Se local_raw é uma string
        elif isinstance(local_raw, str):
            return f"{local_raw} - Câmara dos Deputados"
        
        return "Câmara dos Deputados"
