# Dados Necessários para Atualizar as Estatísticas

## Estatísticas Atuais (Mockadas)

As estatísticas mostradas no dashboard são atualmente **dados de exemplo** (mockados) no arquivo `api/app.py`. Para ter dados reais, você precisa:

## 1. Estrutura da Tabela `estatisticas_projetos`

```sql
CREATE TABLE estatisticas_projetos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area_tecnica TEXT NOT NULL,
    tipo_estatistica TEXT NOT NULL,
    valor INTEGER DEFAULT 0,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fonte TEXT,
    detalhes TEXT
);
```

## 2. Tipos de Estatísticas Necessárias

### A. Aprovação de Projetos de Lei Favoráveis ao Municipalismo
**Dados necessários:**
- Número de projetos aprovados
- Critério: Projetos favoráveis aos municípios
- Fonte: APIs da Câmara e Senado
- Filtro: Status = "Aprovado" + Análise de conteúdo

### B. Reprovação de Projetos de Lei Desfavoráveis ao Municipalismo
**Dados necessários:**
- Número de projetos reprovados
- Critério: Projetos desfavoráveis aos municípios
- Fonte: APIs da Câmara e Senado
- Filtro: Status = "Rejeitado" + Análise de conteúdo

### C. Projetos com Atuação da CNM - Aprovados (CNM Favorável)
**Dados necessários:**
- Número de projetos aprovados
- Critério: CNM se posicionou favoravelmente
- Fonte: Sistema interno da CNM
- Filtro: Status = "Aprovado" + Posicionamento CNM = "Favorável"

### D. Projetos com Atuação da CNM - Aprovados (CNM Desfavorável)
**Dados necessários:**
- Número de projetos aprovados
- Critério: CNM se posicionou contrariamente
- Fonte: Sistema interno da CNM
- Filtro: Status = "Aprovado" + Posicionamento CNM = "Contrário"

### E. Projetos com Atuação da CNM - Reprovados (CNM Favorável)
**Dados necessários:**
- Número de projetos reprovados
- Critério: CNM se posicionou favoravelmente
- Fonte: Sistema interno da CNM
- Filtro: Status = "Rejeitado" + Posicionamento CNM = "Favorável"

### F. Projetos com Atuação da CNM - Reprovados (CNM Desfavorável)
**Dados necessários:**
- Número de projetos reprovados
- Critério: CNM se posicionou contrariamente
- Fonte: Sistema interno da CNM
- Filtro: Status = "Rejeitado" + Posicionamento CNM = "Contrário"

## 3. Fontes de Dados Necessárias

### APIs Externas
1. **Câmara dos Deputados API**
   - Endpoint: `/proposicoes`
   - Dados: Status, conteúdo, votações
   - Filtros: Período, tipo de proposição

2. **Senado Federal API**
   - Endpoint: `/materias`
   - Dados: Status, conteúdo, votações
   - Filtros: Período, tipo de matéria

### Sistema Interno da CNM
1. **Banco de Posicionamentos**
   - Tabela com posicionamentos da CNM sobre projetos
   - Campos: ID do projeto, posicionamento, data, área técnica

2. **Sistema de Acompanhamento**
   - Registro de projetos monitorados pela CNM
   - Histórico de atuações e resultados

## 4. Implementação Necessária

### A. Criar Extrator de Estatísticas
```python
class EstatisticasExtractor:
    def extrair_estatisticas_projetos(self):
        # Lógica para extrair dados das APIs
        # Análise de conteúdo para determinar favorabilidade
        # Integração com sistema da CNM
        pass
```

### B. Análise de Conteúdo
- **Favorável ao Municipalismo:** Aumenta recursos, autonomia, competências dos municípios
- **Desfavorável ao Municipalismo:** Reduz recursos, limita autonomia, cria obrigações sem recursos

### C. Integração com Sistema CNM
- API ou banco de dados interno da CNM
- Sincronização de posicionamentos
- Histórico de atuações

## 5. Atualização Automática

### Frequência Sugerida
- **Estatísticas gerais:** Diária
- **Posicionamentos CNM:** Em tempo real
- **Análise de conteúdo:** Semanal

### Processo ETL
1. Extrair dados das APIs
2. Analisar conteúdo dos projetos
3. Consultar posicionamentos da CNM
4. Calcular estatísticas por área técnica
5. Salvar no banco de dados
6. Atualizar dashboard

## 6. Exemplo de Implementação

```python
# Em api/app.py, substituir dados mockados por:
def get_estatisticas_reais(area_tecnica):
    with sqlite3.connect('database/agenda_congresso.db') as conn:
        cursor = conn.execute("""
            SELECT tipo_estatistica, valor 
            FROM estatisticas_projetos 
            WHERE area_tecnica = ?
        """, (area_tecnica,))
        return dict(cursor.fetchall())
```

## 7. Próximos Passos

1. **Desenvolver extrator de estatísticas**
2. **Criar sistema de análise de conteúdo**
3. **Integrar com APIs da Câmara e Senado**
4. **Conectar com sistema interno da CNM**
5. **Implementar atualização automática**
6. **Substituir dados mockados por dados reais**
