# CHECKPOINT C1 — Projeto da Disciplina

## Participação Eleitoral de Eleitores com Deficiência na Paraíba: Subnotificação Cadastral e Abstenção nas Eleições de 2024

**Equipe:** Luciana Norat | Monica Vasconcelos
**Entrega:** 08/06/2026


## 1. Escopo (Definição do Problema)

### Problema de dados

Na Paraíba, não existe sistema que permita consultar, de forma integrada, como eleitores com deficiência (PCD) se distribuem por zona eleitoral. A proporção de PCD declarados nas zonas é consistentemente inferior ao esperado — indicando subnotificação cadastral. Identificar essas zonas permite ao TRE-PB planejar ações de atualização cadastral e garantir atendimento prioritário nas eleições de 2026. Complementarmente, a aplicação verifica se zonas com maior concentração de PCD apresentam taxas de abstenção mais elevadas, sinalizando barreiras de acesso ainda não superadas.

### Solução proposta

Pipeline ETL que extrai dois arquivos CSV do Portal de Dados Abertos do TSE (dadosabertos.tse.jus.br), transforma e integra dados de perfil do eleitorado e comparecimento/abstenção, e carrega o resultado no MongoDB. Sobre essa base são implementadas consultas analíticas expostas em dashboard interativo com filtros por município, zona eleitoral e tipo de deficiência.

Arquivos de entrada:

- `perfil_eleitor_secao_2024_PB.csv` — perfil do eleitorado por seção eleitoral (~1,8 milhão de registros)
- `perfil_comparecimento_abstencao_2024_PB.csv` — comparecimento e abstenção por zona eleitoral (~302 mil registros)

### Por que documentos/MongoDB?

Os dados eleitorais têm hierarquia natural (estado → município → zona → seção), que se mapeia diretamente para documentos JSON aninhados — evitando os múltiplos JOINs necessários em um PostgreSQL relacional. O esquema flexível do MongoDB também acomoda campos opcionais e variações entre os dois arquivos de entrada sem rigidez estrutural.


## 2. Entendimento da Fonte de Dados

### Fonte

Os dados são provenientes do Portal de Dados Abertos do Tribunal Superior Eleitoral (TSE), disponível em dadosabertos.tse.jus.br. O acesso é público, sem necessidade de cadastro ou autenticação. Os arquivos são disponibilizados em formato CSV compactado (ZIP), com atualização periódica após cada pleito eleitoral. A licença de uso é Creative Commons, permitindo uso livre para fins acadêmicos e de pesquisa.

### Aspectos legais/éticos (LGPD)

Os arquivos utilizados não contêm dados pessoais identificáveis — não há nome, CPF, título de eleitor ou qualquer informação que permita identificar individualmente um eleitor. Os dados são agregados por seção ou zona eleitoral, representando contagens e perfis estatísticos do eleitorado. Declaramos expressamente que o tratamento está em conformidade com a LGPD, uma vez que os dados são públicos, agregados e de natureza estatística.

### Metadados descritivos

| **Atributo** | **Descrição** |
|---|---|
| Fonte original | Portal de Dados Abertos do TSE — dadosabertos.tse.jus.br |
| Recorte geográfico | Estado da Paraíba (PB) |
| Ano de referência | 2024 (eleições municipais) |
| Formato | CSV, separado por ponto e vírgula, codificação Latin 1 |
| Volume — Arquivo 1 | ~1.810.720 registros (perfil por seção) |
| Volume — Arquivo 2 | ~302.947 registros (comparecimento por zona) |
| Frequência de atualização | Por ciclo eleitoral (última atualização: 29/04/2025) |
| Idioma | Português |
| Licença | Creative Commons — uso livre para fins acadêmicos |

### Dicionário de dados

**Arquivo 1: `perfil_eleitor_secao_2024_PB.csv`**

| **Campo** | **Tipo** | **Descrição** | **Exemplo** |
|---|---|---|---|
| SG_UF | String | Sigla da UF | PB |
| CD_MUNICIPIO | Inteiro | Código TSE do município | 19003 |
| NM_MUNICIPIO | String | Nome do município | JOÃO PESSOA |
| NR_ZONA | Inteiro | Número da zona eleitoral | 1 |
| NR_SECAO | Inteiro | Número da seção eleitoral | 42 |
| NR_LOCAL_VOTACAO | Inteiro | Número do local de votação | 1001 |
| NM_LOCAL_VOTACAO | String | Nome do local de votação | ESC. EST. PROF. MARIA... |
| DS_GENERO | String | Gênero do eleitor | FEMININO |
| DS_ESTADO_CIVIL | String | Estado civil | CASADO |
| DS_FAIXA_ETARIA | String | Faixa etária | 25 a 34 anos |
| DS_GRAU_ESCOLARIDADE | String | Grau de escolaridade | ENSINO MÉDIO COMPLETO |
| DS_RACA_COR | String | Raça/cor autodeclarada | Parda |
| QT_ELEITORES_PERFIL | Inteiro | Total de eleitores aptos neste perfil | 45 |
| QT_ELEITORES_DEFICIENCIA | Inteiro | Eleitores com deficiência ou mobilidade reduzida | 3 |
| QT_ELEITORES_BIOMETRIA | Inteiro | Eleitores com biometria cadastrada | 40 |
| TP_OBRIGATORIEDADE_VOTO | String | Voto obrigatório ou facultativo | Obrigatório |

**Arquivo 2: `perfil_comparecimento_abstencao_2024_PB.csv`**

| **Campo** | **Tipo** | **Descrição** | **Exemplo** |
|---|---|---|---|
| SG_UF | String | Sigla da UF | PB |
| CD_MUNICIPIO | Inteiro | Código TSE do município | 19003 |
| NM_MUNICIPIO | String | Nome do município | JOÃO PESSOA |
| NR_ZONA | Inteiro | Número da zona eleitoral | 1 |
| NR_TURNO | Inteiro | Turno da eleição (1 ou 2) | 1 |
| DS_GENERO | String | Gênero | FEMININO |
| DS_FAIXA_ETARIA | String | Faixa etária | 35 a 44 anos |
| DS_GRAU_INSTRUCAO | String | Grau de instrução | ENSINO MÉDIO COMPLETO |
| DS_COR_RACA | String | Raça/cor | Parda |
| QT_APTOS | Inteiro | Total de eleitores aptos | 120 |
| QT_COMPARECIMENTO | Inteiro | Total que compareceu | 98 |
| QT_ABSTENCAO | Inteiro | Total que não compareceu | 22 |
| QT_COMPARECIMENTO_DEFICIENCIA | Inteiro | PCD que compareceram | 5 |
| QT_ABSTENCAO_DEFICIENCIA | Inteiro | PCD que não compareceram | 2 |
| QT_COMPAREC_DEFIC_OBRIGATORIO | Inteiro | PCD com voto obrigatório que compareceram | 4 |
| QT_ABST_DEFIC_OBRIGATORIO | Inteiro | PCD com voto obrigatório que não compareceram | 1 |


## 3. Requisitos de Dados (Perguntas que a Aplicação Responde)

As perguntas abaixo guiam toda a modelagem e cada uma delas se tornará uma consulta na Seção 7 e um elemento visual no dashboard (Seção 8):

- Quais municípios da Paraíba apresentam a menor proporção de eleitores PCD em relação ao total de eleitores, sinalizando possível subnotificação cadastral?
- Como se distribui a quantidade absoluta e relativa de eleitores com deficiência por zona eleitoral na Paraíba?
- As zonas eleitorais com maior concentração de eleitores PCD apresentam taxas de abstenção mais elevadas do que a média do estado?
- Qual é a taxa de abstenção específica dos eleitores PCD com voto obrigatório, comparada à dos eleitores sem deficiência na mesma zona?
- Como se distribui o perfil dos eleitores PCD por faixa etária e gênero nas zonas eleitorais da Paraíba?
- Quais são os locais de votação (nome e município) que concentram o maior número absoluto de eleitores PCD por seção?
- Existe diferença no padrão de abstenção de eleitores PCD entre municípios de grande porte (ex.: João Pessoa, Campina Grande) e municípios menores da Paraíba?


# CHECKPOINT C2


## 4. Modelo Conceitual (UML)

O modelo conceitual foi elaborado em notação UML (Unified Modeling Language) e representa as entidades do domínio eleitoral, seus atributos e os relacionamentos entre elas. O diagrama orienta o mapeamento para o MongoDB descrito na Seção 6.

### Diagrama de Classes UML

> **Figura 1** — Diagrama de classes UML do modelo conceitual para análise da participação eleitoral de eleitores com deficiência na Paraíba (Eleições 2024).

### Classes e Atributos

O modelo é composto por quatro classes principais: **Municipio**, **ZonaEleitoral**, **SecaoEleitoral** e **PerfilEleitor**, esta última com duas subclasses: **PerfilPCD** e **PerfilNaoPCD**. O relacionamento N:N entre Municipio e ZonaEleitoral é resolvido por arrays de referências bidirecionais, eliminando a necessidade de uma classe associativa separada.

| **Classe** | **Atributo** | **Tipo** | **Observação** |
|---|---|---|---|
| **Municipio** | | | |
| | cdMunicipio «PK» | Inteiro | Identificador único TSE |
| | nmMunicipio | String | Nome do município |
| | sgUf | String | Sigla da UF — sempre "PB" |
| | turnos {multivalorado} | Array[Int] | Ex: [1] ou [1, 2] |
| | zonas {multivalorado} | Array[Int] | Ex: [1, 64, 70, 76, 77] |
| **ZonaEleitoral** | | | |
| | nrZona «PK» | Inteiro | Número da zona eleitoral |
| | nmSede | String | Município sede da zona |
| | municipios {multivalorado} | Array[Int] | Ex: [19003, 19011, 19025] |
| **SecaoEleitoral** | | | |
| | nrZona «PK, FK» | Inteiro | Parte da chave composta |
| | nrSecao «PK» | Inteiro | Parte da chave composta |
| | localVotacao {composto} | Objeto | Local físico da seção |
| | + nrLocalVotacao | Inteiro | Número do local de votação |
| | + nmLocalVotacao | String | Nome do local de votação |
| **PerfilEleitor (pai)** | | | |
| | dsGenero | String | Gênero do grupo |
| | dsEstadoCivil | String | Estado civil |
| | dsFaixaEtaria | String | Faixa etária |
| | dsGrauEscolaridade | String | Grau de escolaridade (Arquivo 1) |
| | dsRacaCor | String | Raça/cor autodeclarada |
| | qtEletoresAptos | Inteiro | Total de eleitores no grupo |
| | tpObrigatoriedadeVoto | String | Obrigatório ou facultativo |
| | *qtEletoresBiometria [opcional]* | Inteiro | Eleitores com biometria cadastrada |
| | nrTurno | Inteiro | Turno da eleição |
| | qtComparecimento | Inteiro | Quantidade de eleitores que compareceram à votação |
| | qtAbstencao | Inteiro | Quantidade de eleitores que não compareceram à votação |
| **PerfilPCD (filha)** | | | |
| | qtEletoresDeficiencia | Inteiro | Eleitores com deficiência no grupo |
| **PerfilNaoPCD (filha)** | | | |
| | (sem atributos adicionais) | — | Herda todos os atributos de PerfilEleitor |

### Relacionamentos

| **Relacionamento** | **Tipo** | **Descrição** |
|---|---|---|
| Municipio ↔ ZonaEleitoral | N:N (arrays bidirecionais) | A zona eleitoral é delimitada pela quantidade de eleitores, não pela divisão geográfica. A maioria das zonas da PB abrange mais de um município; por outro lado, municípios maiores (João Pessoa, Campina Grande, Santa Rita, Patos, Cajazeiras e Sousa) possuem mais de uma zona. O N:N é resolvido com arrays de referências bidirecionais: zonas em Municipio e municipios em ZonaEleitoral. Como o número de elementos é geograficamente limitado (máximo 7 municípios por zona e 5 zonas por município), essa abordagem é mais eficiente que uma coleção associativa separada, evitando $lookup desnecessários. |
| ZonaEleitoral → SecaoEleitoral | 1:N | Uma zona eleitoral contém várias seções. A seção é identificada pelo par (nrZona + nrSecao) — o número de seção se repete entre zonas diferentes, portanto apenas o par identifica uma seção de forma única no estado. |
| SecaoEleitoral → PerfilEleitor | Composição (1:N) | Um perfil de eleitor só existe dentro de uma seção eleitoral. Se a seção não existir, o perfil perde seu contexto. Um mesmo local de votação pode abrigar mais de uma seção eleitoral (relação 1:N). |
| PerfilEleitor → PerfilPCD / PerfilNaoPCD | Herança (generalização) | PerfilEleitor é a classe pai com atributos comuns a todos os perfis. PerfilPCD acrescenta qtEletoresDeficiencia. PerfilNaoPCD não acrescenta atributos — existe para distinguir semanticamente os dois subtipos. |

### Requisitos Obrigatórios Atendidos

| **Requisito** | **Onde aparece no modelo** |
|---|---|
| Atributo simples | cdMunicipio, nmMunicipio, nrZona, nmSede, nrSecao, dsGenero, entre outros |
| Atributo multivalorado | turnos e zonas em Municipio; municipios em ZonaEleitoral |
| Atributo composto | localVotacao em SecaoEleitoral — composto por nrLocalVotacao e nmLocalVotacao |
| Atributo opcional | qtEletoresBiometria em PerfilEleitor — nem todo eleitor tem biometria cadastrada |
| Composição | SecaoEleitoral ◆→ PerfilEleitor — o perfil não existe sem a seção |
| Herança/Generalização | PerfilEleitor → PerfilPCD e PerfilNaoPCD |


## 5. Projeto do Banco Orientado a Documentos (Mapeamento)

Esta seção documenta o alinhamento entre o modelo conceitual UML, os dados coletados nos arquivos do TSE e as coleções no MongoDB. O mapeamento é apresentado em dois quadros: o Quadro A relaciona cada atributo do modelo ao campo correspondente na fonte de dados; o Quadro B descreve como cada elemento do UML é implementado no MongoDB.

> *Arquivo 1: `perfil_eleitor_secao_2024_PB.csv` — perfil do eleitorado por seção (~1,8 milhão de registros)*
> *Arquivo 2: `perfil_comparecimento_abstencao_2024_PB.csv` — comparecimento e abstenção por zona (~302 mil registros)*

### Quadro A — Correspondência conceito ↔ dado coletado

| **Classe / Atributo** | **Campo na fonte (CSV)** | **Arquivo** | **Tipo geral** |
|---|---|---|---|
| **Municipio** | — | — | — |
| Municipio.cdMunicipio | CD_MUNICIPIO | Arquivo 1 e 2 | Inteiro |
| Municipio.nmMunicipio | NM_MUNICIPIO | Arquivo 1 e 2 | String |
| Municipio.sgUf | SG_UF | Arquivo 1 e 2 | String |
| Municipio.turnos | NR_TURNO | Arquivo 2 | Array de Inteiro |
| Municipio.zonas | NR_ZONA | Arquivo 1 e 2 | Array de Inteiro |
| **ZonaEleitoral** | — | — | — |
| ZonaEleitoral.nrZona | NR_ZONA | Arquivo 1 e 2 | Inteiro |
| ZonaEleitoral.nmSede | — | PDF TRE-PB | String |
| ZonaEleitoral.municipios | CD_MUNICIPIO | Arquivo 1 e 2 | Array de Inteiro |
| **SecaoEleitoral** | — | — | — |
| SecaoEleitoral.nrZona | NR_ZONA | Arquivo 1 | Inteiro |
| SecaoEleitoral.nrSecao | NR_SECAO | Arquivo 1 | Inteiro |
| SecaoEleitoral.localVotacao | — | — | Objeto composto |
| + nrLocalVotacao | NR_LOCAL_VOTACAO | Arquivo 1 | Inteiro |
| + nmLocalVotacao | NM_LOCAL_VOTACAO | Arquivo 1 | String |
| **PerfilEleitor (pai)** | — | — | — |
| PerfilEleitor.dsGenero | DS_GENERO | Arquivo 1 | String |
| PerfilEleitor.dsEstadoCivil | DS_ESTADO_CIVIL | Arquivo 1 | String |
| PerfilEleitor.dsFaixaEtaria | DS_FAIXA_ETARIA | Arquivo 1 | String |
| PerfilEleitor.dsGrauEscolaridade | DS_GRAU_ESCOLARIDADE (Arq.1) / DS_GRAU_INSTRUCAO (Arq.2) | Arquivo 1 e 2 | String |
| PerfilEleitor.dsRacaCor | DS_RACA_COR | Arquivo 1 | String |
| PerfilEleitor.qtEletoresAptos | QT_ELEITORES_PERFIL | Arquivo 1 | Inteiro |
| PerfilEleitor.tpObrigatoriedadeVoto | TP_OBRIGATORIEDADE_VOTO | Arquivo 1 | String |
| PerfilEleitor.qtEletoresBiometria | QT_ELEITORES_BIOMETRIA | Arquivo 1 | Inteiro |
| PerfilEleitor.nrTurno | NR_TURNO | Arquivo 2 | Inteiro |
| PerfilEleitor.qtComparecimento | QT_COMPARECIMENTO | Arquivo 2 | Inteiro |
| PerfilEleitor.qtAbstencao | QT_ABSTENCAO | Arquivo 2 | Inteiro |
| **PerfilPCD (filha)** | — | — | — |
| PerfilPCD.qtEletoresDeficiencia | QT_ELEITORES_DEFICIENCIA | Arquivo 1 | Inteiro |
| **PerfilNaoPCD (filha)** | — | — | — |
| (sem atributos adicionais) | — | — | — |

#### Notas de mapeamento

**`turnos` em Municipio** é um atributo derivado — construído a partir dos valores distintos de NR_TURNO registrados para cada município no Arquivo 2. Nas eleições municipais de 2024, o segundo turno ocorre apenas em municípios onde nenhum candidato a prefeito obteve 50% + 1 dos votos válidos no primeiro turno, e somente em municípios com eleitorado acima do limite legal. Na Paraíba, apenas João Pessoa e Campina Grande atingiram esse critério em 2024, resultando em `turnos: [1, 2]`; os demais municípios registram `turnos: [1]`. Nas eleições gerais (presidente e governador), a lógica é diferente: o segundo turno impacta todos os municípios do estado simultaneamente, pois o critério é nacional/estadual — nesse caso, todos os municípios da Paraíba teriam `turnos: [1, 2]`. A modelagem com array suporta ambos os cenários sem alteração de esquema, demonstrando a flexibilidade do MongoDB para diferentes ciclos eleitorais.

```js
// Eleições municipais 2024 — Paraíba
{ "_id": 19003, "nmMunicipio": "JOÃO PESSOA",    "turnos": [1, 2] }
{ "_id": 19427, "nmMunicipio": "CAMPINA GRANDE", "turnos": [1, 2] }
{ "_id": 19259, "nmMunicipio": "PATOS",          "turnos": [1]    }

// Eleições gerais — todos os municípios teriam segundo turno se aplicável
{ "_id": 19003, "nmMunicipio": "JOÃO PESSOA", "turnos": [1, 2] }
{ "_id": 19259, "nmMunicipio": "PATOS",       "turnos": [1, 2] }
```

**`zonas`** (em Municipio) **e `municipios`** (em ZonaEleitoral) são atributos derivados durante o ETL — construídos a partir dos valores distintos de NR_ZONA e CD_MUNICIPIO encontrados nos registros de cada município/zona. Esses arrays implementam a navegação bidirecional do relacionamento N:N: a partir de um município encontram-se suas zonas, e a partir de uma zona encontram-se seus municípios, sem necessidade de $lookup em coleção intermediária.

```js
// Coleção municipios
{ "_id": 19003, "nmMunicipio": "JOÃO PESSOA",   "turnos": [1, 2], "zonas": [1, 64, 70, 76, 77] }
{ "_id": 19011, "nmMunicipio": "ALAGOA GRANDE", "turnos": [1],    "zonas": [9] }

// Coleção zonas
{ "_id": 9, "nmSede": "Alagoa Grande", "municipios": [19011, 19025, 19321] }
{ "_id": 1, "nmSede": "João Pessoa",   "municipios": [19003] }
```

**`nmSede`** em ZonaEleitoral não consta nos CSVs do TSE — é obtido do documento oficial do TRE-PB que lista os municípios abrangidos por cada zona eleitoral, e inserido manualmente durante a etapa de transformação do ETL. A sede da zona eleitoral corresponde ao município onde está instalado o cartório eleitoral responsável por aquela zona. Esse enriquecimento manual é justificado pelo conhecimento institucional do TRE-PB e agrega valor analítico ao modelo, permitindo consultas diretas por município sede sem necessidade de cruzamento adicional de dados.

```js
// Coleção zonas — com nmSede enriquecido via PDF TRE-PB
{ "_id": 9,  "nmSede": "Alagoa Grande",   "municipios": [19011, 19025, 19321] }
{ "_id": 10, "nmSede": "Guarabira",       "municipios": [19259] }
{ "_id": 16, "nmSede": "Campina Grande",  "municipios": [19427] }
{ "_id": 22, "nmSede": "Campina Grande",  "municipios": [19427, 19031, 19283, 19500, 19585] }
```

> *Nota de implementação: O dicionário de enriquecimento será construído a partir do PDF oficial do TRE-PB e aplicado durante a transformação ETL no Checkpoint C3.*

**Atenção ETL — `dsGrauEscolaridade`:** o atributo dsGrauEscolaridade em PerfilEleitor apresenta uma inconsistência de nomenclatura entre as duas fontes de dados: o Arquivo 1 utiliza DS_GRAU_ESCOLARIDADE enquanto o Arquivo 2 utiliza DS_GRAU_INSTRUCAO para o mesmo conceito. Além da diferença de nome, os valores descritivos podem apresentar variações de texto entre os dois arquivos. A etapa de transformação do ETL no Checkpoint C3 será responsável por padronizar ambos os campos, aplicando um mapeamento explícito de valores para garantir consistência nas consultas analíticas.

```js
// Arquivo 1 — DS_GRAU_ESCOLARIDADE
{ "DS_GRAU_ESCOLARIDADE": "ENSINO MÉDIO COMPLETO" }
{ "DS_GRAU_ESCOLARIDADE": "SUPERIOR COMPLETO" }

// Arquivo 2 — DS_GRAU_INSTRUCAO
{ "DS_GRAU_INSTRUCAO": "MÉDIO COMPLETO" }
{ "DS_GRAU_INSTRUCAO": "SUPERIOR COMPLETO" }

// Após padronização no ETL — modelo MongoDB
{ "dsGrauEscolaridade": "ENSINO MÉDIO COMPLETO" }
{ "dsGrauEscolaridade": "SUPERIOR COMPLETO" }
```

**`qtEletoresBiometria`** em PerfilEleitor é opcional — nem todo eleitor tem biometria cadastrada. A coleta biométrica é realizada nos cartórios eleitorais durante o atendimento ordinário ao eleitor — alistamento eleitoral, revisão cadastral ou qualquer outro serviço presencial. Em 2014 e 2015 houve um recadastramento biométrico amplo promovido pela Justiça Eleitoral, mas durante a pandemia de COVID-19 essa coleta foi suspensa. Desde então, o recadastramento ocorre de forma gradual, à medida que os eleitores comparecem ao cartório para outros serviços. No MongoDB, a opcionalidade é tratada naturalmente pelo esquema flexível — documentos de perfis sem biometria simplesmente não incluem o campo, distinguindo semanticamente "não tem biometria cadastrada" de "tem zero eleitores com biometria".

```js
// Perfil com biometria cadastrada — campo presente
{ "dsGenero": "FEMININO", "dsFaixaEtaria": "25 a 34 anos", "qtEletoresAptos": 45, "qtEletoresBiometria": 40, "tipo": "NAO_PCD" }

// Perfil sem biometria — campo ausente no documento
{ "dsGenero": "MASCULINO", "dsFaixaEtaria": "65 a 69 anos", "qtEletoresAptos": 12, "tipo": "NAO_PCD" }

// Perfil PCD com biometria parcial
{ "dsGenero": "FEMININO", "dsFaixaEtaria": "45 a 49 anos", "qtEletoresAptos": 8, "qtEletoresBiometria": 5, "qtEletoresDeficiencia": 8, "tipo": "PCD" }
```

**Registros agregados por perfil:** cada registro dos CSVs do TSE não representa um eleitor individual, mas um grupo de eleitores que compartilha o mesmo conjunto de características demográficas dentro de uma seção eleitoral. Para uma mesma seção podem existir múltiplos documentos na coleção perfis — um para cada combinação distinta de gênero, faixa etária, grau de escolaridade, raça/cor, estado civil e obrigatoriedade de voto. Essa granularidade agregada preserva o anonimato dos eleitores em conformidade com a LGPD, enquanto ainda permite análises estatísticas detalhadas por perfil demográfico. A quantidade total de eleitores de uma seção é obtida somando o campo qtEletoresAptos de todos os documentos daquela seção.

```js
// Três documentos distintos da mesma seção (nrZona: 1, nrSecao: 42)
{ "nrZona": 1, "nrSecao": 42, "dsGenero": "FEMININO",  "dsFaixaEtaria": "25 a 34 anos", "dsRacaCor": "Parda", "qtEletoresAptos": 45, "qtEletoresBiometria": 40, "tipo": "NAO_PCD" }
{ "nrZona": 1, "nrSecao": 42, "dsGenero": "MASCULINO", "dsFaixaEtaria": "25 a 34 anos", "dsRacaCor": "Parda", "qtEletoresAptos": 38, "qtEletoresBiometria": 35, "tipo": "NAO_PCD" }
{ "nrZona": 1, "nrSecao": 42, "dsGenero": "FEMININO",  "dsFaixaEtaria": "45 a 49 anos", "dsRacaCor": "Parda", "qtEletoresAptos": 8,  "qtEletoresBiometria": 5,  "qtEletoresDeficiencia": 8, "tipo": "PCD" }
```

### Quadro B — Mapeamento para o MongoDB

| **Elemento (modelo)** | **Tipo no UML** | **Implementação no MongoDB** | **Observação** |
|---|---|---|---|
| **Municipio** | | | |
| Municipio | Classe | Coleção municipios | Coleção principal |
| cdMunicipio | Atrib. simples | Campo _id | Chave primária do documento |
| nmMunicipio | Atrib. simples | Campo simples | Obrigatório |
| sgUf | Atrib. simples | Campo simples | Mantido por fidelidade à fonte TSE |
| turnos | Atrib. multivalorado | Array simples | Ex: [1] ou [1, 2] |
| zonas | Atrib. multivalorado | Array de referências | Ex: [1, 64, 70, 76, 77] |
| **ZonaEleitoral** | | | |
| ZonaEleitoral | Classe | Coleção zonas | Coleção principal |
| nrZona | Atrib. simples | Campo _id | Chave primária do documento |
| nmSede | Atrib. simples | Campo simples | Enriquecimento via PDF TRE-PB |
| municipios | Atrib. multivalorado | Array de referências | Ex: [19003, 19011, 19025] |
| **SecaoEleitoral** | | | |
| SecaoEleitoral | Classe | Coleção secoes | Coleção principal |
| nrZona + nrSecao | Chave composta | _id: {nrZona, nrSecao} | Garante unicidade do par zona+seção |
| nrZona | Atrib. simples (PK, FK) | Campo simples | Parte da chave; referência a zonas |
| nrSecao | Atrib. simples (PK) | Campo simples | Sem significado isolado — só faz sentido com nrZona |
| localVotacao | Atrib. composto | Documento embutido | Lido sempre junto com a seção |
| + nrLocalVotacao | Atrib. simples | Campo no embutido | Obrigatório |
| + nmLocalVotacao | Atrib. simples | Campo no embutido | Obrigatório |
| **PerfilEleitor / PerfilPCD / PerfilNaoPCD** | | | |
| PerfilEleitor | Classe pai | Coleção perfis | Coleção única — Padrão Polymorphic |
| PerfilPCD | Subclasse | Documento tipo: "PCD" | Campo tipo discrimina o subtipo |
| PerfilNaoPCD | Subclasse | Documento tipo: "NAO_PCD" | Campo tipo discrimina o subtipo |
| dsGenero | Atrib. simples | Campo simples | Obrigatório |
| dsEstadoCivil | Atrib. simples | Campo simples | Obrigatório |
| dsFaixaEtaria | Atrib. simples | Campo simples | Obrigatório |
| dsGrauEscolaridade | Atrib. simples | Campo simples | Padronizado no ETL — DS_GRAU_ESCOLARIDADE (Arq.1) e DS_GRAU_INSTRUCAO (Arq.2) |
| dsRacaCor | Atrib. simples | Campo simples | Obrigatório |
| qtEletoresAptos | Atrib. simples | Campo simples | Obrigatório |
| tpObrigatoriedadeVoto | Atrib. simples | Campo simples | Obrigatório |
| qtEletoresBiometria | Atrib. opcional | Campo simples | Pode estar ausente no documento |
| nrTurno | Atrib. simples | Campo simples | Obrigatório |
| qtComparecimento | Atrib. simples | Campo simples | Proveniente do Arquivo 2 — cruzamento no ETL |
| qtAbstencao | Atrib. simples | Campo simples | Proveniente do Arquivo 2 — cruzamento no ETL |
| qtEletoresDeficiencia | Atrib. simples (PerfilPCD) | Campo simples | Presente apenas quando tipo: "PCD" |

#### Notas de mapeamento — Decisões de design

**N:N com arrays bidirecionais:** O relacionamento N:N entre Municipio e ZonaEleitoral é resolvido com arrays de referências em ambas as coleções — `zonas` em Municipio e `municipios` em ZonaEleitoral. Como o número de elementos é geograficamente limitado (máximo 7 municípios por zona e 5 zonas por município, como João Pessoa com zonas [1, 64, 70, 76, 77]), essa abordagem é mais eficiente que uma coleção associativa separada, evitando `$lookup` desnecessários nas consultas mais frequentes.

**Padrão Polymorphic:** A herança entre PerfilEleitor, PerfilPCD e PerfilNaoPCD é implementada com uma única coleção `perfis`. O campo `tipo` discrimina o subtipo — documentos com `tipo: "PCD"` possuem `qtEletoresDeficiencia`; documentos com `tipo: "NAO_PCD"` não possuem esse campo. Essa abordagem é adequada porque os dois subtipos compartilham a maioria dos atributos e são consultados em conjunto nas análises comparativas.

**Chave composta em SecaoEleitoral:** implementada como `_id` objeto — `{ "nrZona": 1, "nrSecao": 42 }`. O número de seção não tem significado isolado; só faz sentido associado a uma zona eleitoral. Um mesmo local de votação pode abrigar mais de uma seção eleitoral.

**Decisão embed × referência em PerfilEleitor:** embora PerfilEleitor seja conceitualmente parte de SecaoEleitoral (composição), é implementado como coleção separada referenciada por `nrZona + nrSecao`. Dado o volume de ~1,8 milhão de registros, embutir todos os perfis em cada seção excederia o limite de 16 MB do BSON (regras de Coupal, 2019).


# NOTA DE ACRÉSCIMO AO CHECKPOINT C2

*Participação Eleitoral de Eleitores com Deficiência na Paraíba: Subnotificação Cadastral e Abstenção nas Eleições de 2024*


## 6. Introdução e Justificativa do Acréscimo

Durante o planejamento do pipeline de ETL no Checkpoint C3, identificaram-se duas lacunas no modelo conceitual e no mapeamento para o MongoDB definidos no Checkpoint C2, descritas e corrigidas nesta nota. Ambos os ajustes foram avaliados sob a ótica do padrão de acesso aos dados ("dados lidos juntos ficam juntos") e das regras de Coupal (2019) para decisão entre embedding e referência: cardinalidade do relacionamento, limite de 16 MB do BSON, frequência de leitura conjunta e potencial de crescimento do relacionamento.

> *Esta nota deve ser lida em conjunto com o documento do Checkpoint C2 (entregue em 15/06/2026), que permanece válido em sua íntegra exceto pelos pontos aqui revisados. A Figura 1 do C2 (diagrama de classes UML) é reapresentada de forma atualizada na seção 5 desta nota, incorporando os dois ajustes descritos a seguir.*


## 7. Ajuste 1 — Terceira Fonte de Dados e Acessibilidade do Local de Votação

### Motivação

Nenhuma das duas fontes previstas no C1/C2 permite responder à pergunta de pesquisa sobre acessibilidade dos locais de votação. O Arquivo 1 (`perfil_eleitor_secao_2024_PB.csv`) fornece o perfil do eleitorado por seção, incluindo `nrLocalVotacao` e `nmLocalVotacao`, mas não contém informação de acessibilidade. O Arquivo 2 (`perfil_comparecimento_abstencao_2024_PB.csv`) fornece comparecimento e abstenção apenas com granularidade de zona eleitoral, sem qualquer referência a local de votação. Fez-se necessária, portanto, a incorporação de uma terceira fonte de dados — `eleitorado_local_votacao_2024_PB.csv` —, único arquivo do conjunto que contém o atributo `DS_SITU_SECAO_ACESSIBILIDADE`, vinculado a cada seção eleitoral por meio de seu local de votação.

### Impacto no modelo conceitual (UML)

A classe SecaoEleitoral é ajustada: seu atributo composto `localVotacao`, originalmente definido apenas com `nrLocalVotacao` e `nmLocalVotacao` (propriedades simples provenientes do Arquivo 1), passa a incluir também o atributo simples `dsSituAcessibilidade`, proveniente do Arquivo 3. Não há criação de classe nova nem alteração de cardinalidade — o ajuste ocorre dentro do atributo composto já existente.

#### Quadro A atualizado — Correspondência conceito ↔ dado coletado

| **Classe / Propriedade (modelo)** | **Metadado na fonte** | **Arquivo** | **Tipo geral** |
|---|---|---|---|
| SecaoEleitoral.localVotacao.dsSituAcessibilidade | DS_SITU_SECAO_ACESSIBILIDADE | Arquivo 3 | String |

#### Quadro B atualizado — Mapeamento para o MongoDB

| **Elemento (modelo)** | **Tipo no MC** | **Implementação no MongoDB** | **Observação** |
|---|---|---|---|
| localVotacao.dsSituAcessibilidade | Atributo simples (dentro de composto) | Campo simples embutido em localVotacao | Embedding — ver justificativa 7.3 |

### Decisão embedding × referência (regras de Coupal, 2019)

Optou-se por manter `localVotacao` embutido em `secoes` (sem criar a coleção `locaisVotacao`), pelos seguintes critérios:

- **Frequência de leitura conjunta:** a consulta mais frequente do projeto lê seção e local de votação simultaneamente; o embedding evita `$lookup` nessas consultas.
- **Cardinalidade e crescimento:** a relação seção→local de votação é N:1 (várias seções por local) e estável para os dados históricos de 2024, sem expectativa de crescimento dentro do próprio documento.
- **Limite de 16 MB do BSON:** o objeto composto `localVotacao` tem tamanho desprezível (poucos campos escalares), não havendo qualquer risco de aproximação do limite do BSON.
- **Redundância controlada:** como os dados de 2024 são históricos e não sofrerão atualização, a repetição do valor de acessibilidade entre seções do mesmo local não traz risco de inconsistência.

### Ressalva para a fase prospectiva (2026)

Esta decisão é válida especificamente para a base histórica de 2024. Para a análise prospectiva das eleições de 2026 (Fase 2 da dissertação), deve-se considerar que: (i) seções eleitorais podem ser remanejadas para locais de votação diferentes dos de 2024; (ii) novas seções podem ser criadas em função do crescimento do eleitorado; e (iii) a quantidade total de seções tende a aumentar. O pipeline de ETL para os dados de 2026 não deve, portanto, assumir que o mapeamento seção→local de votação de 2024 permanece válido, devendo recarregar os dados de localização e acessibilidade a partir dos arquivos do TSE correspondentes ao novo pleito.


## 8. Ajuste 2 — Granularidade de Comparecimento e Abstenção

### Problema identificado

No modelo do C2, `qtComparecimento` e `qtAbstencao` foram alocados na coleção `perfis`, no nível de cada perfil demográfico de uma seção eleitoral. O Arquivo 2 (`perfil_comparecimento_abstencao_2024_PB.csv`), porém, fornece esses dados apenas com granularidade de zona eleitoral e turno, sem nenhuma quebra por seção ou por característica demográfica. Manter esses campos em `perfis` atribuiria a todos os perfis de uma mesma zona valores idênticos de comparecimento/abstenção — uma falsa granularidade, incompatível com o nível de detalhe real da fonte de dados.

### Decisão de modelagem

Foi criada uma nova coleção, `comparecimentoZona`, com chave composta `{nrZona, nrTurno}`, dedicada exclusivamente aos dados de comparecimento e abstenção:

```js
// comparecimentoZona
{
  "_id": { "nrZona": 1, "nrTurno": 1 },
  "qtComparecimento": 45230,
  "qtAbstencao": 8120,
  "qtComparecimentoDeficiencia": 980,
  "qtAbstencaoDeficiencia": 210
}
```

Essa separação preserva a fidelidade de `perfis` ao seu propósito original (caracterização demográfica do eleitorado por seção) e facilita a expansão do projeto para os dados prospectivos de 2026, já que novos turnos/eleições podem ser inseridos como novos documentos em `comparecimentoZona` sem alterar a coleção `zonas`.

### Impacto no modelo conceitual (UML)

Os atributos `qtComparecimento`, `qtAbstencao`, `qtComparecimentoDeficiencia` e `qtAbstencaoDeficiencia` são removidos da classe PerfilEleitor. É incluída uma nova classe, **ComparecimentoAbstencaoZona**, associada a ZonaEleitoral com multiplicidade 1:N (uma zona pode ter um registro de comparecimento por turno).

#### Quadro A atualizado — Correspondência conceito ↔ dado coletado

| **Classe / Propriedade (modelo)** | **Metadado na fonte** | **Arquivo** | **Tipo geral** |
|---|---|---|---|
| ComparecimentoAbstencaoZona.nrTurno | NR_TURNO | Arquivo 2 | Inteiro |
| ComparecimentoAbstencaoZona.qtComparecimento | QT_COMPARECIMENTO | Arquivo 2 | Inteiro |
| ComparecimentoAbstencaoZona.qtAbstencao | QT_ABSTENCAO | Arquivo 2 | Inteiro |
| ComparecimentoAbstencaoZona.qtComparecimentoDeficiencia | QT_COMPARECIMENTO_DEFICIENCIA | Arquivo 2 | Inteiro |
| ComparecimentoAbstencaoZona.qtAbstencaoDeficiencia | QT_ABSTENCAO_DEFICIENCIA | Arquivo 2 | Inteiro |

#### Quadro B atualizado — Mapeamento para o MongoDB

| **Elemento (modelo)** | **Tipo no MC** | **Implementação no MongoDB** | **Observação** |
|---|---|---|---|
| ComparecimentoAbstencaoZona | Classe | Coleção nova | _id composto {nrZona, nrTurno} |
| ZonaEleitoral → ComparecimentoAbstencaoZona | Associação 1:N | Referência lógica via nrZona (sem $lookup embutido) | Combinada via agregação nas consultas de abstenção × PCD |

### Decisão embedding × referência (regras de Coupal, 2019)

Optou-se por referência (coleção separada), e não por embedding em `zonas`, pelos seguintes critérios:

- **Crescimento do relacionamento:** comparecimento/abstenção é um fato vinculado a cada eleição e turno; embutir em `zonas` exigiria um array crescente a cada novo pleito (2024, 2026, 2028...), tornando o documento da zona instável ao longo do tempo.
- **Natureza do dado distinta:** `zonas` representa identidade e geografia eleitoral (atributo relativamente estável), enquanto `comparecimentoZona` representa um fato analítico por eleição — separar por natureza evita misturar metadado estrutural com dado de medição.
- **Frequência de leitura conjunta moderada:** embora a pergunta central do projeto cruze concentração de PCD por zona com abstenção, esse cruzamento ocorre em consultas analíticas específicas (via agregação), e não em toda leitura de `zonas` — não há ganho relevante de performance que justifique o acoplamento por embedding.
- **Limite de 16 MB do BSON:** não é uma restrição ativa dado o volume de zonas na Paraíba, mas a separação evita qualquer acoplamento futuro caso o projeto venha a incorporar múltiplos pleitos no mesmo cluster.

### Consultas analíticas afetadas

As consultas que relacionam concentração de PCD por zona com taxas de abstenção (núcleo da pergunta de pesquisa do projeto) passam a requerer a combinação de dados agregados de `perfis` (por zona) com `comparecimentoZona`, via `$lookup` ou agregação em pipeline com múltiplos estágios.


## 9. Síntese das Alterações

| **Item alterado** | **C2 (original)** | **C3 (revisado nesta nota)** |
|---|---|---|
| localVotacao | nrLocalVotacao, nmLocalVotacao (Arquivo 1) | + dsSituAcessibilidade (Arquivo 3) |
| qtComparecimento / qtAbstencao | Campos em perfis (nível de perfil/seção) | Movidos para nova coleção comparecimentoZona (nível zona+turno) |
| Fontes de dados | 2 arquivos do TSE | 3 arquivos do TSE |

![Figura 1 (revisada)](diagrama_uml_atualizado.png)
## 10. Diagrama de Classes UML Atualizado (Figura 1 revisada)

O diagrama a seguir reapresenta o modelo conceitual completo do Checkpoint C2 (Figura 1 daquele documento), incorporando os dois ajustes descritos nas seções 7 e 8 desta nota. Classes inalteradas mantêm a cor original; classes alteradas e a classe nova são destacadas em contorno coral, com a respectiva mudança anotada na mesma cor.

> **Figura 1 (revisada)** — Diagrama de classes UML atualizado com os ajustes da Nota de Acréscimo ao Checkpoint C2: inclusão de `dsSituAcessibilidade` em `SecaoEleitoral.localVotacao` (Ajuste 1) e criação da classe `ComparecimentoAbstencaoZona`, com remoção de `qtComparecimento`/`qtAbstencao` de PerfilEleitor (Ajuste 2).


# NOTA DE ACRÉSCIMO AO CHECKPOINT C1

## 11. Introdução e Justificativa do Acréscimo

Durante o planejamento do pipeline de ETL no Checkpoint C3, a equipe incorporou uma
terceira fonte de dados — `eleitorado_local_votacao_2024_PB.csv` — não prevista nas
seções 2 e 3 do Checkpoint C1 (entregue em 08/06/2026). Essa fonte foi necessária para
responder à pergunta de pesquisa sobre acessibilidade dos locais de votação.

## 12. Atualização — Fontes de Dados (seção 2)

O texto original do C1 afirmava que os arquivos de entrada eram dois. Esse trecho passa
a ser lido como **três arquivos de entrada**, com a inclusão do terceiro:

- `eleitorado_local_votacao_2024_PB.csv` — relação entre seções eleitorais, locais de
  votação e situação de acessibilidade de cada seção (13.240 registros na Paraíba).

## 13. Atualização — Metadados Descritivos (seção 2)

| **Atributo** | **Descrição** |
|---|---|
| Volume — Arquivo 3 | 13.240 registros (eleitorado_local_votacao, recorte PB) |
| Formato — Arquivo 3 | CSV, separado por ponto e vírgula, codificação Latin 1 |
| Fonte — Arquivo 3 | Portal de Dados Abertos do TSE (mesma fonte e licença dos demais) |

## 14. Atualização — Dicionário de Dados (seção 2)

**Arquivo 3: `eleitorado_local_votacao_2024_PB.csv`**

| **Campo** | **Tipo** | **Descrição** | **Exemplo** |
|---|---|---|---|
| SG_UF | String | Sigla da UF | PB |
| CD_MUNICIPIO | Inteiro | Código TSE do município | 19003 |
| NM_MUNICIPIO | String | Nome do município | JOÃO PESSOA |
| NR_ZONA | Inteiro | Número da zona eleitoral | 1 |
| NR_SECAO | Inteiro | Número da seção eleitoral | 42 |
| NR_LOCAL_VOTACAO | Inteiro | Número do local de votação | 1001 |
| NM_LOCAL_VOTACAO | String | Nome do local de votação | ESC. EST. ... |
| DS_SITU_SECAO_ACESSIBILIDADE | String | Situação de acessibilidade da seção | Com acessibilidade / Sem acessibilidade |

# SEÇÃO 7 DO CHECKPOINT C3 — Pipeline ETL, Consultas e Desempenho

## 15. Síntese da Implementação (Seção 7 da Especificação)

O pipeline completo (Bronze → Silver → Gold → Carga), as consultas e os índices estão
implementados no notebook `Eleitores_pcd_2024.ipynb` (pasta raiz deste repositório).
Esta seção resume os principais resultados, em conformidade com os itens a) a f)
exigidos.

### 15.1 Carga (item c)

5 coleções carregadas no MongoDB Atlas (banco `eleicoes_pcd_2024`):

| Coleção | Documentos | Observação |
|---|---|---|
| municipios | 223 | Completo |
| zonas | 68 | Completo, nmSede enriquecido via PDF TRE-PB |
| secoes | 10.626 | Completo, com dsSituAcessibilidade (Arquivo 3) |
| perfis | 904.077 | Amostra estratificada de 50% (limite do tier gratuito do Atlas — ver seção 4.3.1 do notebook) |
| comparecimentoZona | 76 | Completo |

### 15.2 Índices e Desempenho (item e)

Consulta testada: perfis PCD de uma zona específica (`{nrZona: 1, tipo: "PCD"}`).

| | Antes do índice | Depois do índice |
|---|---|---|
| Estágio | COLLSCAN | FETCH → IXSCAN |
| Documentos examinados | 904.077 | 428 |
| Documentos retornados | 428 | 428 |
| Tempo de execução | 799 ms | 3 ms |

Índice composto criado: `{nrZona: 1, tipo: 1}` (ambos os campos são de igualdade —
a regra ESR não impõe ordem específica neste caso).

### 15.3 Consultas (item d)

| Requisito | Onde está implementado | Resultado-destaque |
|---|---|---|
| Find com filtro e projeção | Seção 6.1 do notebook | — |
| Dot notation (estrutura embutida) | Seção 6.2 | 5.559 de 10.626 seções (52%) sem acessibilidade |
| `$elemMatch` (array) | Seção 6.3 | — |
| Aggregation (`$match/$group/$sort/$project`) | Seção 6.4 | Zona 77 (João Pessoa) lidera com 2,92% de PCD |
| `$lookup` (perfis × comparecimentoZona) | Seção 6.5 | Zona 76: 23,41% de abstenção, apesar de só a 8ª em % de PCD — indício de que outros fatores além da concentração de PCD influenciam a abstenção |
| `$graphLookup` | Não aplicável | Modelo não possui relacionamento hierárquico recursivo |

### 15.4 Schema Design Pattern (item f)

**Polymorphic Pattern**, aplicado na coleção `perfis`: documentos `PerfilPCD` e
`PerfilNaoPCD` convivem na mesma coleção, discriminados pelo campo `tipo`. O campo
`qtEletoresDeficiencia` só existe em documentos `tipo: "PCD"`. Essa escolha evita
fragmentação em consultas comparativas (PCD vs. não-PCD), que são o núcleo analítico
do projeto. Justificativa completa na seção 7 do notebook.

