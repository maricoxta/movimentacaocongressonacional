import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
from bs4 import BeautifulSoup
import re

class SenadoExtractor:
    def __init__(self):
        self.base_url = "https://www12.senado.leg.br"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ETL-Agenda-Congresso/1.0'
        })
    
    def get_eventos_comissoes(self, data_inicio: str = None, data_fim: str = None) -> List[Dict]:
        """Extrai eventos das comissões do Senado - apenas atividades legislativas"""
        if not data_inicio:
            data_inicio = datetime.now().strftime("%Y-%m-%d")
        if not data_fim:
            data_fim = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        eventos = []
        
        # URLs específicas para atividades legislativas do Senado
        urls_legislativas = [
            f"{self.base_url}/institucional/eventos",
            f"{self.base_url}/institucional/eventos/agenda",
            f"{self.base_url}/institucional/eventos/comissoes"
        ]
        
        for url in urls_legislativas:
            try:
                eventos.extend(self._scraping_eventos_legislativos(url, data_inicio, data_fim))
            except Exception as e:
                print(f"Erro ao buscar eventos legislativos em {url}: {e}")
        
        return eventos
    
    def get_agenda_geral(self, data_inicio: str = None, data_fim: str = None) -> List[Dict]:
        """Extrai agenda geral do Senado - apenas atividades legislativas"""
        if not data_inicio:
            data_inicio = datetime.now().strftime("%Y-%m-%d")
        if not data_fim:
            data_fim = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        eventos = []
        
        try:
            # URL da agenda de eventos do Senado
            url = f"{self.base_url}/institucional/eventos"
            eventos.extend(self._scraping_eventos_legislativos(url, data_inicio, data_fim))
            
        except Exception as e:
            print(f"Erro ao buscar agenda geral do Senado: {e}")
        
        return eventos
    
    def _scraping_eventos_legislativos(self, url: str, data_inicio: str, data_fim: str) -> List[Dict]:
        """Faz web scraping de eventos legislativos do Senado"""
        eventos = []
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar por elementos que contenham eventos legislativos
                elementos_evento = soup.find_all(['div', 'article', 'section'], class_=re.compile(r'evento|agenda|reuniao|sessao|audiencia'))
                
                for elemento in elementos_evento:
                    evento = self._extrair_evento_legislativo_senado(elemento)
                    if evento and self._eh_atividade_legislativa_senado(evento):
                        # Filtrar por data se possível
                        if self._evento_no_periodo(evento, data_inicio, data_fim):
                            eventos.append(evento)
                
                print(f"✅ Web scraping do Senado: {len(eventos)} eventos legislativos encontrados")
                
        except Exception as e:
            print(f"❌ Erro no web scraping do Senado: {e}")
        
        return eventos
    
    def _eh_atividade_legislativa_senado(self, evento: Dict) -> bool:
        """Verifica se o evento do Senado é uma atividade legislativa"""
        titulo = evento.get('nome', '').lower()
        tipo_evento = evento.get('tipo_evento', '').lower()
        
        # Palavras-chave que indicam atividades legislativas
        palavras_legislativas = [
            'audiência', 'reunião', 'sessão', 'debate', 'votação', 'apreciação',
            'discussão', 'deliberação', 'projeto', 'lei', 'proposta', 'matéria',
            'comissão', 'plenário', 'cúpula', 'conferência', 'seminário'
        ]
        
        # Verificar se o título contém palavras legislativas
        for palavra in palavras_legislativas:
            if palavra in titulo:
                return True
        
        # Verificar se o tipo do evento é legislativo
        tipos_legislativos = [
            'audiência pública', 'reunião', 'sessão', 'debate', 'votação'
        ]
        
        for tipo in tipos_legislativos:
            if tipo in tipo_evento:
                return True
        
        return False
    
    def _extrair_evento_legislativo_senado(self, elemento) -> Dict:
        """Extrai informações de evento legislativo do Senado"""
        try:
            # Tentar extrair título
            titulo_element = elemento.find(['h1', 'h2', 'h3', 'h4', 'h5', 'strong', 'b'])
            titulo = titulo_element.get_text().strip() if titulo_element else ""
            
            # Se não encontrou título, tentar extrair do texto do elemento
            if not titulo:
                texto_completo = elemento.get_text().strip()
                # Tentar extrair primeira linha como título
                linhas = [linha.strip() for linha in texto_completo.split('\n') if linha.strip()]
                if linhas:
                    titulo = linhas[0][:200]  # Limitar a 200 caracteres
            
            if not titulo:
                return None
            
            # Tentar extrair data
            data_texto = self._extrair_data_html(elemento)
            
            # Tentar extrair hora
            hora_texto = self._extrair_hora_html(elemento)
            
            # Tentar extrair local
            local_texto = self._extrair_local_html(elemento)
            
            # Determinar tipo do evento
            tipo_evento = self._determinar_tipo_evento_legislativo(elemento, titulo)
            
            # Gerar link real do evento
            link_evento = self._gerar_link_evento_senado(elemento, titulo)
            
            evento = {
                'evento_id_externo': f"senado_{hash(titulo + data_texto)}",
                'nome': titulo,
                'data_inicio': f"{data_texto} {hora_texto}".strip() if data_texto else "",
                'data_fim': "",
                'situacao': "Em Andamento",
                'tema': self._extrair_tema_legislativo(elemento, titulo),
                'tipo_evento': tipo_evento,
                'local_evento': local_texto or "Senado Federal",
                'link_evento': link_evento,
                'area_tecnica': None,
                'fonte': 'senado'
            }
            
            return evento
            
        except Exception as e:
            print(f"Erro ao extrair evento legislativo do Senado: {e}")
            return None
    
    def _gerar_link_evento_senado(self, elemento, titulo: str) -> str:
        """Gera link real para evento do Senado"""
        # Tentar extrair link do elemento
        link_element = elemento.find('a')
        if link_element and link_element.get('href'):
            href = link_element.get('href')
            if href.startswith('/'):
                return f"{self.base_url}{href}"
            elif href.startswith('http'):
                return href
        
        # Se não encontrou link, tentar gerar baseado no título
        # Exemplo: "Abertura da II Cúpula Parlamentar de Mudança Climática e Transição Justa da América Latina e do Caribe"
        # Link: https://www12.senado.leg.br/institucional/eventos/detalheeventoeventos?evento_id=abertura-da-ii-cupula-parlamentar-de-mudanca-climatica-e-transicao-justa-da-america-latina-e-do-caribe
        
        # Gerar ID do evento baseado no título
        evento_id = self._gerar_id_evento(titulo)
        if evento_id:
            return f"{self.base_url}/institucional/eventos/detalheeventoeventos?evento_id={evento_id}"
        
        # Link genérico da agenda do Senado
        return f"{self.base_url}/institucional/eventos"
    
    def _gerar_id_evento(self, titulo: str) -> str:
        """Gera ID do evento baseado no título"""
        if not titulo:
            return ""
        
        # Converter título para formato de ID (lowercase, sem acentos, com hífens)
        import unicodedata
        
        # Remover acentos
        titulo_sem_acento = ''.join(
            c for c in unicodedata.normalize('NFD', titulo.lower())
            if not unicodedata.combining(c)
        )
        
        # Substituir espaços e caracteres especiais por hífens
        id_evento = re.sub(r'[^a-z0-9\s-]', '', titulo_sem_acento)
        id_evento = re.sub(r'\s+', '-', id_evento.strip())
        
        return id_evento
    
    def _determinar_tipo_evento_legislativo(self, elemento, titulo: str) -> str:
        """Determina tipo do evento legislativo baseado no HTML e título"""
        texto = elemento.get_text().lower()
        titulo_lower = titulo.lower()
        
        if 'audiência' in titulo_lower or 'audiência' in texto:
            return "Audiência Pública"
        elif 'sessão' in titulo_lower or 'sessão' in texto:
            return "Sessão"
        elif 'reunião' in titulo_lower or 'reunião' in texto:
            return "Reunião"
        elif 'comissão' in titulo_lower or 'comissão' in texto:
            return "Reunião de Comissão"
        elif 'plenário' in titulo_lower or 'plenário' in texto:
            return "Sessão Plenária"
        elif 'cúpula' in titulo_lower or 'cúpula' in texto:
            return "Cúpula Parlamentar"
        elif 'conferência' in titulo_lower or 'conferência' in texto:
            return "Conferência"
        elif 'seminário' in titulo_lower or 'seminário' in texto:
            return "Seminário"
        else:
            return "Evento Legislativo"
    
    def _extrair_tema_legislativo(self, elemento, titulo: str) -> str:
        """Extrai tema do evento legislativo baseado no HTML e título"""
        texto = elemento.get_text().lower()
        titulo_lower = titulo.lower()
        
        # Palavras-chave para identificar temas legislativos
        temas_keywords = {
            'Meio Ambiente e Saneamento': ['meio ambiente', 'sustentabilidade', 'poluição', 'clima', 'mudança climática', 'transição justa'],
            'Educação': ['educação', 'escola', 'universidade', 'ensino'],
            'Saúde': ['saúde', 'hospital', 'medicamento', 'vacina'],
            'Economia': ['economia', 'finanças', 'orçamento', 'imposto'],
            'Segurança': ['segurança', 'polícia', 'crime', 'violência'],
            'Infraestrutura': ['infraestrutura', 'obra', 'construção', 'transporte'],
            'Jurídico': ['legislação', 'lei', 'direito', 'constituição'],
            'Relações Exteriores': ['relações exteriores', 'diplomacia', 'internacional']
        }
        
        texto_completo = f"{titulo_lower} {texto}"
        
        for tema, keywords in temas_keywords.items():
            if any(keyword in texto_completo for keyword in keywords):
                return tema
        
        return "Assuntos Legislativos"
    
    def _extrair_data_html(self, elemento) -> str:
        """Extrai data de um elemento HTML"""
        # Buscar por padrões de data
        texto = elemento.get_text()
        
        # Padrões de data brasileira
        padroes_data = [
            r'(\d{2}/\d{2}/\d{4})',
            r'(\d{2}-\d{2}-\d{4})',
            r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})'
        ]
        
        for padrao in padroes_data:
            match = re.search(padrao, texto)
            if match:
                return match.group(1)
        
        return ""
    
    def _extrair_hora_html(self, elemento) -> str:
        """Extrai hora de um elemento HTML"""
        texto = elemento.get_text()
        
        # Padrão de hora
        padrao_hora = r'(\d{2}:\d{2})'
        match = re.search(padrao_hora, texto)
        
        if match:
            return f"às {match.group(1)}"
        
        return ""
    
    def _extrair_local_html(self, elemento) -> str:
        """Extrai local de um elemento HTML"""
        texto = elemento.get_text()
        
        # Palavras-chave que indicam local
        palavras_local = ['auditório', 'sala', 'plenário', 'comissão', 'senado']
        
        linhas = texto.split('\n')
        for linha in linhas:
            linha_lower = linha.lower()
            if any(palavra in linha_lower for palavra in palavras_local):
                return linha.strip()
        
        return ""
    
    def _evento_no_periodo(self, evento: Dict, data_inicio: str, data_fim: str) -> bool:
        """Verifica se evento está no período especificado"""
        data_evento = evento.get('data_inicio', '')
        if not data_evento:
            return True  # Se não tem data, incluir
        
        try:
            # Tentar extrair data do formato "dd/mm/yyyy às hh:mm"
            data_str = data_evento.split(' às ')[0]
            data_evento_dt = datetime.strptime(data_str, "%d/%m/%Y")
            
            inicio_dt = datetime.strptime(data_inicio, "%Y-%m-%d")
            fim_dt = datetime.strptime(data_fim, "%Y-%m-%d")
            
            return inicio_dt.date() <= data_evento_dt.date() <= fim_dt.date()
            
        except:
            return True  # Se não conseguir parsear, incluir
    
    def _tentar_api_dados_abertos(self, data_inicio: str, data_fim: str) -> List[Dict]:
        """Tenta usar a API de dados abertos do Senado"""
        eventos = []
        
        # URLs possíveis da API
        urls_teste = [
            f"{self.base_url}/dados-abertos/api/agenda",
            f"{self.base_url}/dados-abertos/api/eventos",
            f"{self.base_url}/dados-abertos/api/comissoes/eventos"
        ]
        
        for url in urls_teste:
            try:
                params = {
                    'dataInicio': data_inicio,
                    'dataFim': data_fim
                }
                
                response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    if response.headers.get('content-type', '').startswith('application/json'):
                        dados = response.json()
                        eventos.extend(self._processar_eventos_senado(dados))
                        print(f"✅ API do Senado funcionou: {url}")
                        break
                        
            except Exception as e:
                print(f"❌ API do Senado falhou: {url} - {e}")
                continue
        
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
