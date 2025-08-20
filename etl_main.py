import schedule
import time
from datetime import datetime, timedelta
from typing import List, Dict
import sys
import os

# Adicionar diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.database_manager import DatabaseManager
from etl.extractor_camara import CamaraExtractor
from etl.extractor_senado import SenadoExtractor
from etl.categorizador import CategorizadorEventos

class ETLAgendaCongresso:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.camara_extractor = CamaraExtractor()
        self.senado_extractor = SenadoExtractor()
        self.categorizador = CategorizadorEventos(self.db_manager)
    
    def executar_etl_completo(self):
        """Executa o processo ETL completo"""
        print(f"Iniciando ETL - {datetime.now()}")
        
        try:
            # Extrair dados da Câmara
            eventos_camara = self._extrair_dados_camara()
            print(f"Extraídos {len(eventos_camara)} eventos da Câmara")
            
            # Extrair dados do Senado
            eventos_senado = self._extrair_dados_senado()
            print(f"Extraídos {len(eventos_senado)} eventos do Senado")
            
            # Combinar eventos
            todos_eventos = eventos_camara + eventos_senado
            
            # Categorizar eventos
            eventos_categorizados = self.categorizador.categorizar_lote(todos_eventos)
            
            # Salvar no banco
            eventos_novos, eventos_atualizados = self._salvar_eventos(eventos_categorizados)
            
            # Log da execução
            self.db_manager.log_atualizacao(
                tipo="ETL_COMPLETO",
                status="SUCESSO",
                eventos_novos=eventos_novos,
                eventos_atualizados=eventos_atualizados,
                detalhes=f"Processados {len(todos_eventos)} eventos total"
            )
            
            print(f"ETL concluído - {eventos_novos} novos, {eventos_atualizados} atualizados")
            
        except Exception as e:
            print(f"Erro no ETL: {e}")
            self.db_manager.log_atualizacao(
                tipo="ETL_COMPLETO",
                status="ERRO",
                detalhes=str(e)
            )
    
    def _extrair_dados_camara(self) -> List[Dict]:
        """Extrai dados da Câmara dos Deputados"""
        eventos = []
        
        try:
            # Eventos das comissões
            eventos_comissoes = self.camara_extractor.get_eventos_comissoes()
            eventos.extend(eventos_comissoes)
            
            # Sessões do plenário
            eventos_plenario = self.camara_extractor.get_sessoes_plenario()
            eventos.extend(eventos_plenario)
            
        except Exception as e:
            print(f"Erro ao extrair dados da Câmara: {e}")
        
        return eventos
    
    def _extrair_dados_senado(self) -> List[Dict]:
        """Extrai dados do Senado Federal"""
        eventos = []
        
        try:
            # Eventos das comissões
            eventos_comissoes = self.senado_extractor.get_eventos_comissoes()
            eventos.extend(eventos_comissoes)
            
            # Agenda geral
            eventos_geral = self.senado_extractor.get_agenda_geral()
            eventos.extend(eventos_geral)
            
        except Exception as e:
            print(f"Erro ao extrair dados do Senado: {e}")
        
        return eventos
    
    def _salvar_eventos(self, eventos: List[Dict]) -> tuple:
        """Salva eventos no banco de dados"""
        eventos_novos = 0
        eventos_atualizados = 0
        
        for evento in eventos:
            try:
                # Verificar se evento já existe
                eventos_existentes = self.db_manager.get_eventos_por_area()
                evento_existe = any(e['evento_id_externo'] == evento['evento_id_externo'] 
                                  for e in eventos_existentes)
                
                if evento_existe:
                    # Atualizar situação se necessário
                    self.db_manager.update_evento_situacao(
                        evento['evento_id_externo'], 
                        evento['situacao']
                    )
                    eventos_atualizados += 1
                else:
                    # Inserir novo evento
                    if self.db_manager.insert_evento(evento):
                        eventos_novos += 1
                        
            except Exception as e:
                print(f"Erro ao salvar evento {evento.get('evento_id_externo')}: {e}")
        
        return eventos_novos, eventos_atualizados
    
    def atualizar_situacoes(self):
        """Atualiza situações dos eventos existentes"""
        print(f"Atualizando situações - {datetime.now()}")
        
        try:
            # Buscar eventos em andamento
            eventos_andamento = self.db_manager.get_eventos_por_area()
            eventos_para_atualizar = [e for e in eventos_andamento if e['situacao'] == 'Em Andamento']
            
            eventos_atualizados = 0
            
            for evento in eventos_para_atualizar:
                nova_situacao = self._verificar_situacao_evento(evento)
                if nova_situacao != evento['situacao']:
                    self.db_manager.update_evento_situacao(evento['evento_id_externo'], nova_situacao)
                    eventos_atualizados += 1
            
            print(f"Atualizadas {eventos_atualizados} situações")
            
        except Exception as e:
            print(f"Erro ao atualizar situações: {e}")
    
    def _verificar_situacao_evento(self, evento: Dict) -> str:
        """Verifica situação atual de um evento"""
        # Implementação simplificada - pode ser expandida
        # para verificar APIs das casas legislativas
        
        data_inicio = evento.get('data_inicio', '')
        if data_inicio:
            try:
                # Tentar parsear data
                data_parts = data_inicio.split(' ')
                if len(data_parts) >= 1:
                    data_str = data_parts[0]
                    data_evento = datetime.strptime(data_str, "%d/%m/%Y")
                    
                    # Se passou da data, marcar como encerrada
                    if data_evento.date() < datetime.now().date():
                        return "Encerrada"
            except:
                pass
        
        return evento['situacao']
    
    def executar_uma_vez(self):
        """Executa o ETL uma única vez"""
        self.executar_etl_completo()
    
    def agendar_execucao(self):
        """Agenda execução automática do ETL"""
        # Executar a cada hora
        schedule.every().hour.do(self.executar_etl_completo)
        
        # Atualizar situações a cada 30 minutos
        schedule.every(30).minutes.do(self.atualizar_situacoes)
        
        print("ETL agendado para execução automática")
        print("Execução completa: a cada hora")
        print("Atualização de situações: a cada 30 minutos")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto

def main():
    etl = ETLAgendaCongresso()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "uma-vez":
            etl.executar_uma_vez()
        elif sys.argv[1] == "agendar":
            etl.agendar_execucao()
        else:
            print("Uso: python etl_main.py [uma-vez|agendar]")
    else:
        # Execução padrão: uma vez
        etl.executar_uma_vez()

if __name__ == "__main__":
    main()
