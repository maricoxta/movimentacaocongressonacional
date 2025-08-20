-- Esquema do banco de dados para ETL da Câmara e Senado

-- Tabela de eventos
CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evento_id_externo TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL,
    data_inicio TEXT NOT NULL,
    data_fim TEXT NOT NULL,
    situacao TEXT NOT NULL,
    tema TEXT,
    tipo_evento TEXT NOT NULL,
    local_evento TEXT,
    link_evento TEXT,
    area_tecnica TEXT,
    fonte TEXT NOT NULL, -- 'camara' ou 'senado'
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de áreas técnicas
CREATE TABLE IF NOT EXISTS areas_tecnicas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL,
    descricao TEXT,
    palavras_chave TEXT -- palavras-chave para categorização automática
);

-- Tabela de estatísticas de projetos
CREATE TABLE IF NOT EXISTS estatisticas_projetos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area_tecnica TEXT NOT NULL,
    projetos_aprovados_favoraveis INTEGER DEFAULT 0,
    projetos_reprovados_desfavoraveis INTEGER DEFAULT 0,
    projetos_aprovados_cnm_favoravel INTEGER DEFAULT 0,
    projetos_aprovados_cnm_desfavoravel INTEGER DEFAULT 0,
    projetos_reprovados_cnm_favoravel INTEGER DEFAULT 0,
    projetos_reprovados_cnm_desfavoravel INTEGER DEFAULT 0,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de logs de atualização
CREATE TABLE IF NOT EXISTS logs_atualizacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_atualizacao TEXT NOT NULL,
    status TEXT NOT NULL,
    eventos_novos INTEGER DEFAULT 0,
    eventos_atualizados INTEGER DEFAULT 0,
    data_execucao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    detalhes TEXT
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_eventos_area_tecnica ON eventos(area_tecnica);
CREATE INDEX IF NOT EXISTS idx_eventos_data_inicio ON eventos(data_inicio);
CREATE INDEX IF NOT EXISTS idx_eventos_situacao ON eventos(situacao);
CREATE INDEX IF NOT EXISTS idx_eventos_fonte ON eventos(fonte);
