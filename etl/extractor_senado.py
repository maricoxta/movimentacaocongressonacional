import requests
from datetime import datetime, timedelta
from typing import List, Dict


class SenadoAPI:
    BASE_URL = "https://legis.senado.leg.br/dadosabertos"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ETL-Agenda-Congresso/1.0"
        })

    def get_comissoes_agenda(self, data_inicio: str = None, data_fim: str = None) -> List[Dict]:
        """
        Retorna agenda das comissões entre datas (default = hoje até +7 dias).
        """
        if not data_inicio:
            data_inicio = datetime.now().strftime("%Y-%m-%d")
        if not data_fim:
            data_fim = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        url = f"{self.BASE_URL}/comissao/agenda/{data_inicio}/{data_fim}"
        resp = self.session.get(url, timeout=20)
        resp.raise_for_status()

        dados = resp.json()
        eventos_raw = dados.get("AgendaComissoes", {}).get("Eventos", {}).get("Evento", [])

        return [self._parse_evento(evt) for evt in eventos_raw]

    def _parse_evento(self, evt: Dict) -> Dict:
        """
        Normaliza evento de comissão em formato padrão.
        """
        return {
            "evento_id_externo": f"senado::{evt.get('Codigo')}",
            "nome": evt.get("Descricao", "Evento de Comissão"),
            "data_inicio": self._formatar_data(evt.get("Data")),
            "data_fim": self._formatar_data(evt.get("DataFim")),
            "situacao": evt.get("Situacao", "Agendado"),
            "tema": evt.get("Tema", "Assuntos Legislativos"),
            "tipo_evento": evt.get("Tipo", "Reunião"),
            "local_evento": evt.get("Local", "Senado Federal"),
            "link_evento": evt.get("Link", ""),
            "area_tecnica": None,
            "fonte": "senado"
        }

    def _formatar_data(self, data_str: str) -> str:
        """
        Converte datas do Senado para padrão dd/mm/yyyy HH:MM.
        """
        if not data_str:
            return ""
        try:
            dt = datetime.fromisoformat(data_str.replace("Z", ""))
            return dt.strftime("%d/%m/%Y às %H:%M")
        except Exception:
            return data_str
