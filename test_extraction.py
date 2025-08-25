#!/usr/bin/env python3
"""
Script para testar a extração real de dados das APIs da Câmara e Senado
"""

import sys
import os
from datetime import datetime, timedelta

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from etl.extractor_senado import ExtractorSenado
from etl.extractor_camara import CamaraExtractor

print("=== TESTANDO EXTRAÇÃO DO SENADO ===")
senado = ExtractorSenado()
eventos_senado = senado.get_agenda_legislativa()
print(f"Eventos Senado: {len(eventos_senado)}")
for i, evento in enumerate(eventos_senado[:3]):
    print(f"{i+1}. {evento['nome']} ({evento['tipo_evento']})")

print("\n=== TESTANDO EXTRAÇÃO DA CÂMARA ===")
camara = CamaraExtractor()
eventos_camara = camara.get_eventos_comissoes()
print(f"Eventos Câmara (comissões): {len(eventos_camara)}")
for i, evento in enumerate(eventos_camara[:3]):
    print(f"{i+1}. {evento['nome']} ({evento['tipo_evento']})")

eventos_plenario = camara.get_sessoes_plenario()
print(f"Eventos Câmara (plenário): {len(eventos_plenario)}")
for i, evento in enumerate(eventos_plenario[:3]):
    print(f"{i+1}. {evento['nome']} ({evento['tipo_evento']})")
