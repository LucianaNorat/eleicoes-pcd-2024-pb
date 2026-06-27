# Otimização de Performance — Consulta Mais Frequente do Projeto (Checkpoint C3)

## Contexto

Antes de qualquer otimização, foi avaliada a consulta mais frequente do projeto: buscar perfis PCD de uma zona eleitoral específica.

```python
banco["perfis"].find({"nrZona": 1, "tipo": "PCD"})
```

Como a coleção `perfis` não tinha nenhum índice (além do `_id` padrão), essa consulta exigia uma varredura completa da coleção.

## Metodologia

A consulta foi avaliada com `explain()` antes e depois da criação do índice:

```python
banco["perfis"].find({"nrZona": 1, "tipo": "PCD"}).explain()
```

## Passo 1 — Antes do índice

```python
resultado_antes = banco["perfis"].find(
    {"nrZona": 1, "tipo": "PCD"}
).explain()

print(resultado_antes["executionStats"]["executionStages"]["stage"])
print(resultado_antes["executionStats"]["totalDocsExamined"])
print(resultado_antes["executionStats"]["nReturned"])
print(resultado_antes["executionStats"]["executionTimeMillis"])
```

**Resultado:** estágio `COLLSCAN`, com **904.077 documentos examinados** e **799 ms** de tempo de execução, para retornar apenas um pequeno subconjunto de documentos.

## Passo 2 — Criação do índice composto `{nrZona, tipo}`

```python
banco["perfis"].create_index([("nrZona", 1), ("tipo", 1)])
```

**Por que essa combinação de campos:** a consulta filtra por dois campos de **igualdade exata** ao mesmo tempo — `nrZona` e `tipo`. Pela regra ESR (Equality, Sort, Range), quando todos os campos são de igualdade, a ordem entre eles não afeta o desempenho da busca — por isso `{nrZona, tipo}` e `{tipo, nrZona}` seriam equivalentes neste caso específico.

## Passo 3 — Depois do índice

```python
resultado_depois = banco["perfis"].find(
    {"nrZona": 1, "tipo": "PCD"}
).explain()

print(resultado_depois["executionStats"]["executionStages"]["stage"])
print(resultado_depois["executionStats"]["totalDocsExamined"])
print(resultado_depois["executionStats"]["nReturned"])
print(resultado_depois["executionStats"]["executionTimeMillis"])

# Verificação do índice realmente utilizado
print(resultado_depois["executionStats"]["executionStages"]["inputStage"]["stage"])
print(resultado_depois["executionStats"]["executionStages"]["inputStage"]["indexName"])
```

**Resultado:** estágio `FETCH` (com `IXSCAN` no sub-estágio interno), usando o índice `nrZona_1_tipo_1`, com **428 documentos examinados** e **3 ms** de tempo de execução.

## Comparação

| Métrica | Sem índice | Com índice `nrZona_1_tipo_1` |
|---|---|---|
| **Estágio do plano** | `COLLSCAN` | `IXSCAN → FETCH` |
| **Tempo de execução** | 799 ms | **3 ms** |
| **Documentos examinados** | 904.077 | **428** |

**Ganho: de 799 ms para 3 ms — cerca de 266x mais rápido**, com a quantidade de documentos examinados reduzida de mais de 900 mil para apenas 428 (os que realmente satisfazem o filtro de zona + tipo).

## Análise técnica

Sem índice, o MongoDB precisa abrir cada um dos 904.077 documentos da coleção `perfis` para verificar se ele satisfaz `{"nrZona": 1, "tipo": "PCD"}` — uma varredura completa (`COLLSCAN`).

Com o índice composto `{nrZona: 1, tipo: 1}`, o MongoDB consulta diretamente a estrutura ordenada do índice (`IXSCAN`) para localizar os documentos que combinam zona 1 e tipo PCD, e só então abre (`FETCH`) os 428 documentos efetivamente encontrados — eliminando a necessidade de examinar os demais.

Esse índice foi a primeira otimização de performance aplicada ao projeto e serviu de base metodológica para a investigação posterior de lentidão na tabela `locais_votacao` do dashboard (documentada separadamente em `Otimizacao_Indice_Perfis_Dashboard.md`), que aplicou a mesma abordagem de comparação antes/depois via `explain()`.

## Observação sobre o Polymorphic Pattern

Essa consulta também evidencia, na prática, a utilidade do **Polymorphic Pattern** adotado na coleção `perfis`: o campo discriminador `tipo` (`"PCD"` / `"NAO_PCD"`) permite filtrar facilmente um subtipo específico de perfil dentro da mesma coleção, sem necessidade de `$lookup` entre coleções separadas.

---
*Documentação gerada como parte do Checkpoint C3 — Projeto "Participação Eleitoral de Eleitores com Deficiência na Paraíba (2024)".*
