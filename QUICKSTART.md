# 🚀 Guia de Início Rápido - Dashboard Agenda Congresso

## ⚡ Início Super Rápido (5 minutos)

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Popular com dados de exemplo
```bash
python populate_sample.py
```

### 3. Iniciar sistema completo
```bash
python start.py
```

### 4. Escolher opção 2 (Sistema completo)
O sistema irá:
- ✅ Executar ETL inicial
- ✅ Iniciar API na porta 5000
- ✅ Abrir dashboard no navegador
- ✅ Configurar atualização automática

---

## 📋 Funcionalidades Principais

### 🎯 Dashboard
- **18 áreas técnicas** do municipalismo
- **Estatísticas de projetos** de lei
- **Filtros** por status e tipo
- **Notificações** de novos eventos
- **Responsivo** para mobile/tablet/desktop

### 🔄 ETL Automático
- **Extração** da Câmara e Senado
- **Categorização** automática por área
- **Atualização** a cada hora
- **Logs** de execução

### 📊 Dados Estruturados
- Eventos com datas formatadas
- Links para detalhes
- Status em tempo real
- Fonte (Câmara/Senado)

---

## 🛠️ Comandos Úteis

### Executar apenas ETL
```bash
python etl/etl_main.py uma-vez
```

### Iniciar apenas API
```bash
python api/app.py
```

### Verificar saúde da API
```bash
curl http://localhost:5000/api/health
```

### Popular dados de exemplo
```bash
python populate_sample.py
```

---

## 📱 Acessos

- **Dashboard**: http://localhost:5000 (após iniciar API)
- **API**: http://localhost:5000/api
- **Health Check**: http://localhost:5000/api/health

---

## 🎨 Áreas Técnicas Disponíveis

1. Assistência Social e Segurança Alimentar
2. Consórcios Públicos
3. Contabilidade Pública
4. Cultura
5. Defesa Civil
6. Desenvolvimento Rural
7. Educação
8. Finanças
9. Jurídico
10. Meio Ambiente e Saneamento
11. Mulheres
12. Obras, Transferências e Parcerias
13. Orçamento Público
14. Planejamento Territorial e Habitação
15. Previdência
16. Saúde
17. Transporte e Mobilidade
18. Turismo

---

## 🔧 Configuração Avançada

### Variáveis de Ambiente
Crie um arquivo `.env`:
```env
API_PORT=5000
ETL_UPDATE_INTERVAL=3600
CATEGORIZACAO_SCORE_MINIMO=0.3
```

### Personalizar Palavras-chave
Edite `etl/database_manager.py` para ajustar categorização.

---

## 🐛 Solução de Problemas

### ETL não executa
```bash
# Verificar logs
python etl/etl_main.py uma-vez
```

### API não inicia
```bash
# Verificar porta
netstat -an | grep 5000
```

### Dashboard não carrega
```bash
# Verificar API
curl http://localhost:5000/api/health
```

---

## 📞 Suporte

- 📖 **Documentação completa**: `README.md`
- 🐛 **Issues**: Abra no repositório
- 📧 **Email**: [seu-email@exemplo.com]

---

**🎉 Pronto! Seu dashboard está funcionando!**
