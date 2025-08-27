import requests
from datetime import datetime, timedelta
from typing import List, Dict


class CamaraEventos:

    def __init__(self):
        self.base_arquivos = "https://dadosabertos.camara.leg.br/api/v2/eventos"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ETL-Agenda-Camara/1.0"
        })

    def get_eventos_periodo(self, dias_a_frente: int = 30, area_tecnica: str = None) -> List[Dict]:
        """
        Retorna eventos do período (hoje até X dias à frente),
        com opção de filtrar por área técnica.
        """
        hoje = datetime.now().date()
        limite = hoje + timedelta(days=dias_a_frente)

        # Faz a requisição
        response = self.session.get(self.base_arquivos, params={"itens": 100})
        response.raise_for_status()
        eventos_raw = response.json().get("dados", [])

        eventos_filtrados = []

        for evt in eventos_raw:
            try:
                data_inicio_str = evt.get("dataInicio") or evt.get("data")
                if not data_inicio_str:
                    continue

                data_inicio = datetime.fromisoformat(data_inicio_str.replace("Z", "")).date()

                # filtra pela data
                if not (hoje <= data_inicio <= limite):
                    continue

                data_fim = evt.get("dataFim")

                eventos_filtrados.append({
                    "evento_id_externo": f"camara::{evt.get('id', '')}",
                    "nome": evt.get("titulo") or evt.get("descricao", "Evento da Câmara"),
                    "data_inicio": data_inicio,
                    "data_fim": data_fim,
                    "situacao": evt.get("situacao", ""),
                    "tema": evt.get("tema", ""),
                    "tipo_evento": evt.get("eventoTipo", ""),
                    "local_evento": evt.get("local", ""),
                    "link_evento": evt.get("uriDetalhamento", ""),
                    "area_tecnica": area_tecnica,
                    "fonte": "camara"
                })

            except Exception as e:
                print(f"Erro ao processar evento: {e}")

        return eventos_filtrados
