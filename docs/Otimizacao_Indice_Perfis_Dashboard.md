# Otimização de Performance — Consulta da Tabela `locais_votacao`

## Contexto

O dashboard (`eleicoes-pcd-2024-pb`) apresentava lentidão perceptível ao carregar a tabela **`locais_votacao`**, enquanto os gráficos do painel carregavam rapidamente. A investigação identificou que a consulta da tabela executa um `aggregate()` na coleção `perfis` (904.077 documentos), filtrando por `{"tipo": "PCD"}`, agrupando por `nrZona` + `nrSecao`, e ordenando o resultado.

Diferente dos gráficos — que agrupam apenas por `nrZona` (68 grupos) — a tabela agrupa por `nrZona` + `nrSecao` (até ~10.626 combinações possíveis), tornando-a naturalmente mais pesada.

## Pipeline analisada

```python
pipeline_tabela = [
    {"$match": {"tipo": "PCD"}},
    {"$group": {
        "_id": {"nrZona": "$nrZona", "nrSecao": "$nrSecao"},
        "totalPCD": {"$sum": 1}
    }},
    {"$sort": {"_id.nrZona": 1, "_id.nrSecao": 1}},
    {"$limit": 50}
]
```

## Metodologia

Para cada cenário, a consulta foi avaliada com:

```python
banco.command(
    "explain",
    {"aggregate": "perfis", "pipeline": pipeline_tabela, "cursor": {}},
    verbosity="executionStats"
)
```

## Resultados — evolução em três etapas

| Cenário | Índice usado | Estágio do plano | Tempo de execução | Documentos examinados | Chaves de índice examinadas |
|---|---|---|---|---|---|
| **1. Sem índice** | nenhum | `COLLSCAN` | 1759 ms | 904.077 | 0 |
| **2. Índice simples** | `tipo_1` | `IXSCAN → FETCH` | 157 ms | 12.032 | 12.032 |
| **3. Índice composto** | `tipo_1_nrZona_1_nrSecao_1` | `IXSCAN → PROJECTION_COVERED` | **26 ms** | **0** | 12.032 |

**Ganho total: de 1759 ms para 26 ms — aproximadamente 68x mais rápido.**

## Análise técnica

### Cenário 1 — Sem índice (COLLSCAN)
Sem nenhum índice cobrindo o campo `tipo`, o MongoDB examina **todos** os 904.077 documentos da coleção para encontrar os que satisfazem `{"tipo": "PCD"}` (apenas ~12 mil). É o gargalo clássico de uma varredura completa de coleção.

### Cenário 2 — Índice simples em `tipo`
Criado com:
```python
colecao_perfis.create_index("tipo")
```
O índice permite ao MongoDB localizar diretamente os 12.032 documentos PCD via `IXSCAN`, sem abrir os demais ~892 mil documentos. Porém, como o índice cobre apenas o campo `tipo`, o motor ainda precisa de um estágio `FETCH` — abrir cada um dos 12.032 documentos para ler os campos `nrZona` e `nrSecao`, necessários para o `$group`.

### Cenário 3 — Índice composto `{tipo, nrZona, nrSecao}`
Criado com:
```python
colecao_perfis.create_index([("tipo", 1), ("nrZona", 1), ("nrSecao", 1)])
```
Seguindo a regra ESR (Equality, Sort, Range), o campo de igualdade (`tipo`) vem primeiro, seguido dos campos usados no agrupamento/ordenação (`nrZona`, `nrSecao`).

Como o índice agora contém os três campos necessários à consulta, o MongoDB resolve tudo **apenas lendo o índice** — sem nunca abrir o documento original. Isso é confirmado pelo estágio `PROJECTION_COVERED` e por `totalDocsExamined: 0`. Trata-se de uma *covered query*: o nível mais eficiente de consulta possível, pois elimina o custo de acesso ao documento (`FETCH`).

O plano com o índice simples (`tipo_1` + `FETCH`) foi avaliado pelo otimizador do MongoDB e listado em `rejectedPlans` — evidência de que o motor de consultas compara alternativas e escolhe automaticamente o plano mais eficiente disponível.

### Limite da otimização por índice
Os 26 ms restantes correspondem ao trabalho que nenhum índice elimina: o `$group` (consolidar 12.032 documentos em 6.515 grupos por zona/seção) e o `$sort`/`$limit` finais. Índices otimizam a *localização* dos dados; o processamento sobre os dados já selecionados (agregações, ordenações) é custo computacional inerente à consulta.

## Conclusão

A criação do índice composto `{tipo: 1, nrZona: 1, nrSecao: 1}` na coleção `perfis` resolveu o gargalo de performance identificado na tabela `locais_votacao` do dashboard, reduzindo o tempo de execução de **1759 ms para 26 ms** e eliminando por completo a necessidade de leitura de documentos (`totalDocsExamined: 0`), por meio de uma *covered query*.

---
*Documentação gerada como parte do Checkpoint C4 — Projeto "Participação Eleitoral de Eleitores com Deficiência na Paraíba (2024)".*
