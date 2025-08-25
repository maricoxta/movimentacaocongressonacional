from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime, timedelta
import sys

# Adicionar diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.database_manager import DatabaseManager
from etl.sample_data import get_sample_statistics

app = Flask(__name__, static_folder='../web', static_url_path='')
CORS(app)

# Inicializar gerenciador de banco
db_manager = DatabaseManager()

@app.route('/')
def index():
    """Serve a página principal do dashboard"""
    return send_from_directory('../web', 'index.html')

@app.route('/api/health')
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected'
    })

@app.route('/api/areas')
def get_areas():
    """Retorna todas as áreas técnicas"""
    try:
        areas = db_manager.get_areas_tecnicas()
        return jsonify(areas)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/eventos')
def get_eventos():
    """Retorna eventos, opcionalmente filtrados por área e período"""
    try:
        area = request.args.get('area')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 100, type=int)
        
        if area:
            eventos = db_manager.get_eventos_por_area(area, limit)
        else:
            eventos = db_manager.get_eventos_por_area(limit=limit)
        
        # Filtrar por período se fornecido
        if start_date or end_date:
            eventos = filter_events_by_date(eventos, start_date, end_date)
        
        return jsonify(eventos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/eventos/nao-categorizados')
def get_eventos_nao_categorizados():
    """Retorna eventos não categorizados"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 100, type=int)
        
        eventos = db_manager.get_eventos_nao_categorizados(limit)
        
        # Filtrar por período se fornecido
        if start_date or end_date:
            eventos = filter_events_by_date(eventos, start_date, end_date)
        
        return jsonify(eventos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/eventos/novos')
def get_eventos_novos():
    """Retorna eventos criados nas últimas 24 horas"""
    try:
        # Buscar eventos das últimas 24 horas
        yesterday = datetime.now() - timedelta(days=1)
        
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM eventos 
                WHERE data_criacao >= ?
                ORDER BY data_criacao DESC
            """, (yesterday.isoformat(),))
            
            eventos = []
            for row in cursor.fetchall():
                eventos.append(dict(zip([col[0] for col in cursor.description], row)))
        
        return jsonify(eventos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/estatisticas')
def get_estatisticas():
    """Retorna estatísticas de proposições por área técnica"""
    try:
        area = request.args.get('area')
        
        if area:
            # Buscar estatísticas específicas da área
            stats = get_estatisticas_por_area(area)
        else:
            # Retornar estatísticas gerais
            stats = get_estatisticas_gerais()
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/proposicoes')
def get_proposicoes():
    """Retorna proposições por área técnica"""
    try:
        area = request.args.get('area')
        
        if not area:
            return jsonify({'error': 'Área técnica é obrigatória'}), 400
        
        proposicoes = get_proposicoes_por_area(area)
        return jsonify(proposicoes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/proposicoes', methods=['POST'])
def add_proposicao():
    """Adiciona uma nova proposição"""
    try:
        data = request.json
        
        # Validar dados obrigatórios
        required_fields = ['numero_projeto', 'ementa', 'casa_iniciadora', 'forma_apreciacao', 
                          'situacao', 'cabe_analise', 'analise_realizada', 'posicionamento_cnm', 
                          'prioridade', 'area_tecnica']
        
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Inserir proposição
        proposicao_id = insert_proposicao(data)
        
        return jsonify({
            'id': proposicao_id,
            'message': 'Proposição adicionada com sucesso'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/proposicoes/<int:proposicao_id>', methods=['PUT'])
def update_proposicao(proposicao_id):
    """Atualiza uma proposição existente"""
    try:
        data = request.json
        
        # Atualizar proposição
        success = update_proposicao_by_id(proposicao_id, data)
        
        if success:
            return jsonify({'message': 'Proposição atualizada com sucesso'})
        else:
            return jsonify({'error': 'Proposição não encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/proposicoes/<int:proposicao_id>', methods=['DELETE'])
def delete_proposicao(proposicao_id):
    """Exclui uma proposição"""
    try:
        success = delete_proposicao_by_id(proposicao_id)
        
        if success:
            return jsonify({'message': 'Proposição excluída com sucesso'})
        else:
            return jsonify({'error': 'Proposição não encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/areas/contadores')
def get_contadores_areas():
    """Retorna contadores de eventos por área técnica"""
    try:
        areas = db_manager.get_areas_tecnicas()
        contadores = {}
        
        for area in areas:
            eventos = db_manager.get_eventos_por_area(area['nome'])
            contadores[area['nome']] = len(eventos)
        
        # Adicionar contador de não categorizados
        eventos_nao_categorizados = db_manager.get_eventos_nao_categorizados()
        contadores['Não Categorizados'] = len(eventos_nao_categorizados)
        
        return jsonify(contadores)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/eventos/<evento_id>/categorizar', methods=['POST'])
def categorizar_evento(evento_id):
    """Categoriza um evento em uma área técnica"""
    try:
        data = request.json
        area_tecnica = data.get('area_tecnica')
        
        if not area_tecnica:
            return jsonify({'error': 'Área técnica é obrigatória'}), 400
        
        success = db_manager.update_evento_area_tecnica(evento_id, area_tecnica)
        
        if success:
            return jsonify({'message': 'Evento categorizado com sucesso'})
        else:
            return jsonify({'error': 'Evento não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/eventos/<evento_id>', methods=['PUT'])
def update_evento(evento_id):
    """Atualiza um evento específico"""
    try:
        data = request.json
        
        success = db_manager.update_evento(evento_id, data)
        
        if success:
            return jsonify({'message': 'Evento atualizado com sucesso'})
        else:
            return jsonify({'error': 'Evento não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/eventos/buscar')
def buscar_eventos():
    """Busca eventos por termo"""
    try:
        termo = request.args.get('termo', '')
        
        if not termo:
            return jsonify([])
        
        eventos = db_manager.buscar_eventos(termo)
        return jsonify(eventos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs')
def get_logs():
    """Retorna logs de atualização"""
    try:
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM logs_atualizacao 
                ORDER BY data_atualizacao DESC 
                LIMIT 50
            """)
            
            logs = []
            for row in cursor.fetchall():
                logs.append(dict(zip([col[0] for col in cursor.description], row)))
        
        return jsonify(logs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Funções auxiliares

def filter_events_by_date(eventos, start_date, end_date):
    """Filtra eventos por período de data"""
    filtered = []
    
    for evento in eventos:
        # Converter data do evento para comparação
        try:
            if evento.get('data_inicio'):
                # Extrair data do formato "23/07/2025 às 15:45"
                event_date_str = evento['data_inicio'].split(' às ')[0]
                event_date = datetime.strptime(event_date_str, '%d/%m/%Y').date()
                
                # Aplicar filtros
                include_event = True
                
                if start_date:
                    start = datetime.strptime(start_date, '%Y-%m-%d').date()
                    if event_date < start:
                        include_event = False
                
                if end_date and include_event:
                    end = datetime.strptime(end_date, '%Y-%m-%d').date()
                    if event_date > end:
                        include_event = False
                
                if include_event:
                    filtered.append(evento)
        except:
            # Se não conseguir parsear a data, incluir o evento
            filtered.append(evento)
    
    return filtered

def get_estatisticas_por_area(area_tecnica):
    """Retorna estatísticas específicas de uma área técnica"""
    try:
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    SUM(CASE WHEN posicionamento_cnm = 'FAVORÁVEL' THEN 1 ELSE 0 END) as cnm_favoravel,
                    SUM(CASE WHEN posicionamento_cnm = 'DESFAVORÁVEL' THEN 1 ELSE 0 END) as cnm_desfavoravel,
                    SUM(CASE WHEN posicionamento_cnm = 'NEUTRO' THEN 1 ELSE 0 END) as cnm_neutro,
                    SUM(CASE WHEN posicionamento_cnm = 'FAVORÁVEL' AND aprovacao_camara = 'APROVADO' THEN 1 ELSE 0 END) as camara_cnm_favoravel,
                    SUM(CASE WHEN posicionamento_cnm = 'DESFAVORÁVEL' AND aprovacao_camara = 'APROVADO' THEN 1 ELSE 0 END) as camara_cnm_desfavoravel,
                    SUM(CASE WHEN posicionamento_cnm = 'NEUTRO' AND aprovacao_camara = 'APROVADO' THEN 1 ELSE 0 END) as camara_cnm_neutro,
                    SUM(CASE WHEN posicionamento_cnm = 'FAVORÁVEL' AND aprovacao_senado = 'APROVADO' THEN 1 ELSE 0 END) as senado_cnm_favoravel,
                    SUM(CASE WHEN posicionamento_cnm = 'DESFAVORÁVEL' AND aprovacao_senado = 'APROVADO' THEN 1 ELSE 0 END) as senado_cnm_desfavoravel,
                    SUM(CASE WHEN posicionamento_cnm = 'NEUTRO' AND aprovacao_senado = 'APROVADO' THEN 1 ELSE 0 END) as senado_cnm_neutro,
                    SUM(CASE WHEN posicionamento_cnm = 'FAVORÁVEL' AND sancionado_presidencia = 'SIM' THEN 1 ELSE 0 END) as presidencia_cnm_favoravel,
                    SUM(CASE WHEN posicionamento_cnm = 'DESFAVORÁVEL' AND sancionado_presidencia = 'SIM' THEN 1 ELSE 0 END) as presidencia_cnm_desfavoravel,
                    SUM(CASE WHEN posicionamento_cnm = 'NEUTRO' AND sancionado_presidencia = 'SIM' THEN 1 ELSE 0 END) as presidencia_cnm_neutro
                FROM proposicoes 
                WHERE area_tecnica = ?
            """, (area_tecnica,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'cnm_favoravel': row[0] or 0,
                    'cnm_desfavoravel': row[1] or 0,
                    'cnm_neutro': row[2] or 0,
                    'camara_cnm_favoravel': row[3] or 0,
                    'camara_cnm_desfavoravel': row[4] or 0,
                    'camara_cnm_neutro': row[5] or 0,
                    'senado_cnm_favoravel': row[6] or 0,
                    'senado_cnm_desfavoravel': row[7] or 0,
                    'senado_cnm_neutro': row[8] or 0,
                    'presidencia_cnm_favoravel': row[9] or 0,
                    'presidencia_cnm_desfavoravel': row[10] or 0,
                    'presidencia_cnm_neutro': row[11] or 0
                }
            else:
                return get_sample_statistics(area_tecnica)
    except:
        # Se houver erro, retornar dados de exemplo
        return get_sample_statistics(area_tecnica)

def get_estatisticas_gerais():
    """Retorna estatísticas gerais de todas as áreas"""
    try:
        areas = db_manager.get_areas_tecnicas()
        stats_gerais = {}
        
        for area in areas:
            stats_gerais[area['nome']] = get_estatisticas_por_area(area['nome'])
        
        return stats_gerais
    except Exception as e:
        return get_sample_statistics()

def get_proposicoes_por_area(area_tecnica):
    """Retorna proposições de uma área técnica específica"""
    try:
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM proposicoes 
                WHERE area_tecnica = ?
                ORDER BY data_criacao DESC
            """, (area_tecnica,))
            
            proposicoes = []
            for row in cursor.fetchall():
                proposicoes.append(dict(zip([col[0] for col in cursor.description], row)))
        
        return proposicoes
    except:
        # Se a tabela não existir, retornar lista vazia
        return []

def insert_proposicao(data):
    """Insere uma nova proposição no banco"""
    try:
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO proposicoes (
                    numero_projeto, ementa, casa_iniciadora, forma_apreciacao,
                    eixo_tematico, situacao, cabe_analise, prazo_analise,
                    analise_realizada, documento_analise, posicionamento_cnm,
                    prioridade, observacao, area_tecnica, data_criacao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['numero_projeto'],
                data['ementa'],
                data['casa_iniciadora'],
                data['forma_apreciacao'],
                data.get('eixo_tematico', ''),
                data['situacao'],
                data['cabe_analise'],
                data.get('prazo_analise', ''),
                data['analise_realizada'],
                data.get('documento_analise', ''),
                data['posicionamento_cnm'],
                data['prioridade'],
                data.get('observacao', ''),
                data['area_tecnica'],
                datetime.now().isoformat()
            ))
            
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        raise Exception(f"Erro ao inserir proposição: {str(e)}")

def update_proposicao_by_id(proposicao_id, data):
    """Atualiza uma proposição existente"""
    try:
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.execute("""
                UPDATE proposicoes SET
                    numero_projeto = ?, ementa = ?, casa_iniciadora = ?, forma_apreciacao = ?,
                    eixo_tematico = ?, situacao = ?, cabe_analise = ?, prazo_analise = ?,
                    analise_realizada = ?, documento_analise = ?, posicionamento_cnm = ?,
                    prioridade = ?, observacao = ?, data_atualizacao = ?
                WHERE id = ?
            """, (
                data.get('numero_projeto', ''),
                data.get('ementa', ''),
                data.get('casa_iniciadora', ''),
                data.get('forma_apreciacao', ''),
                data.get('eixo_tematico', ''),
                data.get('situacao', ''),
                data.get('cabe_analise', ''),
                data.get('prazo_analise', ''),
                data.get('analise_realizada', ''),
                data.get('documento_analise', ''),
                data.get('posicionamento_cnm', ''),
                data.get('prioridade', ''),
                data.get('observacao', ''),
                datetime.now().isoformat(),
                proposicao_id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        raise Exception(f"Erro ao atualizar proposição: {str(e)}")

def delete_proposicao_by_id(proposicao_id):
    """Exclui uma proposição"""
    try:
        with sqlite3.connect(db_manager.db_path) as conn:
            cursor = conn.execute("DELETE FROM proposicoes WHERE id = ?", (proposicao_id,))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        raise Exception(f"Erro ao excluir proposição: {str(e)}")

if __name__ == '__main__':
    # Criar tabela de proposições se não existir
    try:
        with sqlite3.connect(db_manager.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS proposicoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_projeto TEXT NOT NULL,
                    ementa TEXT NOT NULL,
                    casa_iniciadora TEXT NOT NULL,
                    forma_apreciacao TEXT NOT NULL,
                    eixo_tematico TEXT,
                    situacao TEXT NOT NULL,
                    cabe_analise TEXT NOT NULL,
                    prazo_analise TEXT,
                    analise_realizada TEXT NOT NULL,
                    documento_analise TEXT,
                    posicionamento_cnm TEXT NOT NULL,
                    prioridade TEXT NOT NULL,
                    observacao TEXT,
                    area_tecnica TEXT NOT NULL,
                    aprovacao_camara TEXT DEFAULT 'PENDENTE',
                    aprovacao_senado TEXT DEFAULT 'PENDENTE',
                    sancionado_presidencia TEXT DEFAULT 'PENDENTE',
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    except Exception as e:
        print(f"Erro ao criar tabela de proposições: {e}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
