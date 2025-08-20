# Dashboard Agenda Congresso - CNM

Sistema ETL completo para extração, processamento e visualização de dados da agenda da Câmara dos Deputados e do Senado Federal, focado no municipalismo brasileiro.

## 🎯 Objetivo

Acompanhar semanalmente os eventos dos próximos 7 dias relacionados a áreas específicas do municipalismo, com categorização automática e dashboard responsivo.

## 🏗️ Arquitetura

O sistema é composto por:

- **ETL Backend**: Scripts Python para extração e processamento
- **Banco de Dados**: SQLite para armazenamento estruturado
- **API REST**: Flask para servir dados ao frontend
- **Dashboard Frontend**: Interface responsiva em HTML/CSS/JavaScript

## 📋 Funcionalidades

### Extração de Dados
- ✅ Eventos das comissões da Câmara dos Deputados
- ✅ Sessões do plenário da Câmara
- ✅ Eventos das comissões do Senado
- ✅ Agenda geral do Senado
- ✅ Atualização automática a cada hora

### Categorização Automática
- ✅ 18 áreas técnicas do municipalismo
- ✅ Categorização baseada em palavras-chave
- ✅ Sistema de score para relevância
- ✅ Eventos não categorizados em seção separada

### Dashboard
- ✅ Interface responsiva e moderna
- ✅ Seleção por área técnica
- ✅ Estatísticas de projetos de lei
- ✅ Filtros por status e tipo de evento
- ✅ Notificações de novos eventos
- ✅ Atualização automática

## 🚀 Instalação

### Pré-requisitos
- Python 3.8+
- pip
- Navegador web moderno

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd Agenda.teste
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure o banco de dados
O banco será criado automaticamente na primeira execução.

## 🏃‍♂️ Execução

### 1. Inicializar o banco e executar ETL
```bash
# Executar ETL uma vez
python etl/etl_main.py uma-vez

# Ou agendar execução automática
python etl/etl_main.py agendar
```

### 2. Iniciar a API
```bash
python api/app.py
```

### 3. Abrir o dashboard
Abra o arquivo `web/index.html` no navegador ou sirva via servidor local:

```bash
# Usando Python
cd web
python -m http.server 8000

# Usando Node.js
npx serve web
```

## 📊 Estrutura do Banco de Dados

### Tabelas Principais

#### `eventos`
- `id`: Chave primária
- `evento_id_externo`: ID único do evento na fonte
- `nome`: Título do evento
- `data_inicio`: Data e hora de início (formato: "23/07/2025 às 15:45")
- `data_fim`: Data e hora de fim
- `situacao`: Status (Em Andamento, Encerrada, Cancelada)
- `tema`: Tema do evento
- `tipo_evento`: Tipo (Audiência Pública, Sessão, etc.)
- `local_evento`: Local do evento
- `link_evento`: URL do evento
- `area_tecnica`: Área técnica categorizada
- `fonte`: Origem (camara/senado)

#### `areas_tecnicas`
- `id`: Chave primária
- `nome`: Nome da área técnica
- `descricao`: Descrição da área
- `palavras_chave`: Palavras-chave para categorização

#### `estatisticas_projetos`
- Estatísticas de projetos de lei por área técnica
- Taxas de aprovação/reprovação
- Dados de atuação da CNM

## 🎨 Áreas Técnicas

1. **Assistência Social e Segurança Alimentar e Nutricional**
2. **Consórcios Públicos**
3. **Contabilidade Pública**
4. **Cultura**
5. **Defesa Civil**
6. **Desenvolvimento Rural**
7. **Educação**
8. **Finanças**
9. **Jurídico**
10. **Meio Ambiente e Saneamento**
11. **Mulheres**
12. **Obras, Transferências e Parcerias**
13. **Orçamento Público**
14. **Planejamento Territorial e Habitação**
15. **Previdência**
16. **Saúde**
17. **Transporte e Mobilidade**
18. **Turismo**

## 🔧 Configuração

### Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:

```env
# Configurações do banco
DB_PATH=database/agenda_congresso.db

# Configurações da API
API_HOST=0.0.0.0
API_PORT=5000

# Configurações do ETL
ETL_UPDATE_INTERVAL=3600  # segundos
```

### Personalização de Palavras-chave
Edite o arquivo `etl/database_manager.py` para ajustar as palavras-chave de cada área técnica.

## 📈 Monitoramento

### Logs
Os logs de execução são armazenados na tabela `logs_atualizacao`:
- Tipo de atualização
- Status (SUCESSO/ERRO)
- Quantidade de eventos novos/atualizados
- Detalhes da execução

### Endpoints de Monitoramento
- `GET /api/health`: Status da API
- `GET /api/logs`: Histórico de execuções
- `GET /api/areas/contadores`: Contadores por área

## 🔄 Atualização Automática

O sistema possui dois tipos de atualização:

1. **ETL Completo** (a cada hora)
   - Extrai novos dados das APIs
   - Categoriza eventos
   - Atualiza banco de dados

2. **Atualização de Status** (a cada 30 minutos)
   - Verifica mudanças de status
   - Atualiza situações dos eventos

## 🎯 Estatísticas de Projetos

O dashboard exibe estatísticas de projetos de lei:

- ✅ Aprovação de projetos favoráveis ao Municipalismo
- ❌ Reprovação de projetos desfavoráveis ao Municipalismo
- 🤝 Projetos com atuação da CNM (favorável/desfavorável)
- 📊 Taxas de sucesso por área técnica

## 🚨 Notificações

O sistema detecta novos eventos e exibe notificações:
- Pop-up automático para novos eventos
- Categorização automática por área técnica
- Auto-close após 10 segundos

## 📱 Responsividade

O dashboard é totalmente responsivo:
- ✅ Desktop (1200px+)
- ✅ Tablet (768px - 1199px)
- ✅ Mobile (320px - 767px)

## 🛠️ Desenvolvimento

### Estrutura de Arquivos
```
Agenda.teste/
├── etl/                    # Scripts ETL
│   ├── database_manager.py
│   ├── extractor_camara.py
│   ├── extractor_senado.py
│   ├── categorizador.py
│   └── etl_main.py
├── api/                    # API Flask
│   └── app.py
├── web/                    # Frontend
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── database/               # Banco de dados
│   └── schema.sql
├── requirements.txt
└── README.md
```

### Adicionando Novas Fontes
1. Crie um novo extrator em `etl/`
2. Implemente os métodos de extração
3. Adicione ao `etl_main.py`
4. Teste a integração

### Personalizando Categorização
1. Edite palavras-chave em `database_manager.py`
2. Ajuste scores em `categorizador.py`
3. Teste com dados reais

## 🐛 Troubleshooting

### Problemas Comuns

**ETL não executa**
- Verifique conexão com internet
- Confirme APIs estão acessíveis
- Verifique logs em `database/logs_atualizacao`

**Dashboard não carrega**
- Confirme API está rodando na porta 5000
- Verifique CORS está habilitado
- Teste endpoint `/api/health`

**Categorização incorreta**
- Ajuste palavras-chave da área
- Verifique score mínimo (0.3)
- Teste com eventos específicos

### Logs de Debug
```bash
# Ver logs do ETL
python etl/etl_main.py uma-vez

# Ver logs da API
python api/app.py --debug

# Verificar banco
sqlite3 database/agenda_congresso.db
```

## 📄 Licença

Este projeto foi desenvolvido para a CNM (Confederação Nacional de Municípios).

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no repositório
- Consulte a documentação da API
- Verifique os logs de execução

---

**Desenvolvido com ❤️ para o municipalismo brasileiro**
