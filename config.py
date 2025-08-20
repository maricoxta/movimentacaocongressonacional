"""
Configurações do Dashboard Agenda Congresso - CNM
Centraliza todas as configurações do sistema
"""

import os
from pathlib import Path

# Diretórios do projeto
BASE_DIR = Path(__file__).parent
ETL_DIR = BASE_DIR / "etl"
API_DIR = BASE_DIR / "api"
WEB_DIR = BASE_DIR / "web"
DATABASE_DIR = BASE_DIR / "database"

# Configurações do banco de dados
DATABASE_CONFIG = {
    'path': DATABASE_DIR / "agenda_congresso.db",
    'backup_dir': DATABASE_DIR / "backups",
    'max_backups': 10
}

# Configurações da API
API_CONFIG = {
    'host': os.getenv('API_HOST', '0.0.0.0'),
    'port': int(os.getenv('API_PORT', 5000)),
    'debug': os.getenv('API_DEBUG', 'False').lower() == 'true',
    'cors_origins': ['http://localhost:3000', 'http://localhost:8000', 'http://127.0.0.1:8000']
}

# Configurações do ETL
ETL_CONFIG = {
    'update_interval': int(os.getenv('ETL_UPDATE_INTERVAL', 3600)),  # segundos
    'status_update_interval': int(os.getenv('ETL_STATUS_UPDATE_INTERVAL', 1800)),  # segundos
    'max_retries': int(os.getenv('ETL_MAX_RETRIES', 3)),
    'timeout': int(os.getenv('ETL_TIMEOUT', 30))
}

# Configurações das APIs externas
EXTERNAL_APIS = {
    'camara': {
        'base_url': 'https://dadosabertos.camara.leg.br/api/v2',
        'timeout': 30,
        'user_agent': 'ETL-Agenda-Congresso/1.0'
    },
    'senado': {
        'base_url': 'https://www12.senado.leg.br/dados-abertos',
        'timeout': 30,
        'user_agent': 'ETL-Agenda-Congresso/1.0'
    }
}

# Configurações de categorização
CATEGORIZACAO_CONFIG = {
    'score_minimo': float(os.getenv('CATEGORIZACAO_SCORE_MINIMO', 0.3)),
    'palavras_chave_peso': {
        'exata': 1.0,
        'variacao': 0.8,
        'radical': 0.6
    }
}

# Configurações do dashboard
DASHBOARD_CONFIG = {
    'auto_refresh_interval': int(os.getenv('DASHBOARD_AUTO_REFRESH', 3600000)),  # ms
    'notification_timeout': int(os.getenv('DASHBOARD_NOTIFICATION_TIMEOUT', 10000)),  # ms
    'max_events_per_page': int(os.getenv('DASHBOARD_MAX_EVENTS', 100))
}

# Configurações de logging
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'file': BASE_DIR / "logs" / "app.log",
    'max_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# Configurações de segurança
SECURITY_CONFIG = {
    'api_key_required': os.getenv('API_KEY_REQUIRED', 'False').lower() == 'true',
    'api_key_header': 'X-API-Key',
    'rate_limit': {
        'requests_per_minute': int(os.getenv('RATE_LIMIT_RPM', 60)),
        'burst': int(os.getenv('RATE_LIMIT_BURST', 100))
    }
}

# Configurações de monitoramento
MONITORING_CONFIG = {
    'health_check_interval': int(os.getenv('HEALTH_CHECK_INTERVAL', 300)),  # segundos
    'metrics_enabled': os.getenv('METRICS_ENABLED', 'True').lower() == 'true',
    'alert_email': os.getenv('ALERT_EMAIL', '')
}

# Configurações de backup
BACKUP_CONFIG = {
    'enabled': os.getenv('BACKUP_ENABLED', 'True').lower() == 'true',
    'schedule': os.getenv('BACKUP_SCHEDULE', '0 2 * * *'),  # 2h da manhã
    'retention_days': int(os.getenv('BACKUP_RETENTION_DAYS', 30))
}

# Configurações de cache
CACHE_CONFIG = {
    'enabled': os.getenv('CACHE_ENABLED', 'True').lower() == 'true',
    'ttl': int(os.getenv('CACHE_TTL', 300)),  # segundos
    'max_size': int(os.getenv('CACHE_MAX_SIZE', 1000))
}

# Configurações de desenvolvimento
DEV_CONFIG = {
    'mock_data': os.getenv('MOCK_DATA', 'False').lower() == 'true',
    'sample_events': int(os.getenv('SAMPLE_EVENTS', 50)),
    'debug_mode': os.getenv('DEBUG_MODE', 'False').lower() == 'true'
}

# Configurações de notificação
NOTIFICATION_CONFIG = {
    'email_enabled': os.getenv('EMAIL_NOTIFICATIONS', 'False').lower() == 'true',
    'smtp_server': os.getenv('SMTP_SERVER', ''),
    'smtp_port': int(os.getenv('SMTP_PORT', 587)),
    'smtp_user': os.getenv('SMTP_USER', ''),
    'smtp_password': os.getenv('SMTP_PASSWORD', ''),
    'notification_recipients': os.getenv('NOTIFICATION_RECIPIENTS', '').split(',')
}

# Configurações de estatísticas
STATISTICS_CONFIG = {
    'update_interval': int(os.getenv('STATS_UPDATE_INTERVAL', 3600)),  # segundos
    'history_days': int(os.getenv('STATS_HISTORY_DAYS', 90)),
    'auto_calculate': os.getenv('STATS_AUTO_CALCULATE', 'True').lower() == 'true'
}

def get_config():
    """Retorna todas as configurações em um dicionário"""
    return {
        'database': DATABASE_CONFIG,
        'api': API_CONFIG,
        'etl': ETL_CONFIG,
        'external_apis': EXTERNAL_APIS,
        'categorizacao': CATEGORIZACAO_CONFIG,
        'dashboard': DASHBOARD_CONFIG,
        'logging': LOGGING_CONFIG,
        'security': SECURITY_CONFIG,
        'monitoring': MONITORING_CONFIG,
        'backup': BACKUP_CONFIG,
        'cache': CACHE_CONFIG,
        'dev': DEV_CONFIG,
        'notification': NOTIFICATION_CONFIG,
        'statistics': STATISTICS_CONFIG
    }

def create_directories():
    """Cria diretórios necessários"""
    directories = [
        DATABASE_DIR,
        DATABASE_CONFIG['backup_dir'],
        BASE_DIR / "logs",
        BASE_DIR / "temp"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def validate_config():
    """Valida as configurações"""
    errors = []
    
    # Validar portas
    if not (1024 <= API_CONFIG['port'] <= 65535):
        errors.append(f"Porta da API inválida: {API_CONFIG['port']}")
    
    # Validar intervalos
    if ETL_CONFIG['update_interval'] < 60:
        errors.append("Intervalo de atualização do ETL deve ser >= 60 segundos")
    
    # Validar scores
    if not (0 <= CATEGORIZACAO_CONFIG['score_minimo'] <= 1):
        errors.append("Score mínimo deve estar entre 0 e 1")
    
    if errors:
        raise ValueError(f"Configurações inválidas:\n" + "\n".join(errors))
    
    return True
