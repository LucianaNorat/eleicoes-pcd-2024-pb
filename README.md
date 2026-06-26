# Participação Eleitoral de Eleitores com Deficiência na Paraíba: Subnotificação Cadastral e Abstenção nas Eleições de 2024

**Equipe:** Luciana Norat | Monica Vasconcelos


## 1. Escopo (Definição do Problema)

### Problema de dados

Na Paraíba, não existe sistema que permita consultar, de forma integrada, como eleitores com deficiência (PCD) se distribuem por zona eleitoral. A proporção de PCD declarados nas zonas é consistentemente inferior ao esperado — indicando subnotificação cadastral. Identificar essas zonas permite ao TRE-PB planejar ações de atualização cadastral e garantir atendimento prioritário nas eleições de 2026. Complementarmente, a aplicação verifica se zonas com maior concentração de PCD apresentam taxas de abstenção mais elevadas, sinalizando barreiras de acesso ainda não superadas.

### Solução proposta

Pipeline ETL que extrai dois arquivos CSV do Portal de Dados Abertos do TSE (dadosabertos.tse.jus.br), transforma e integra dados de perfil do eleitorado e comparecimento/abstenção, e carrega o resultado no MongoDB. Sobre essa base são implementadas consultas analíticas expostas em dashboard interativo com filtros por município, zona eleitoral e tipo de deficiência.


## Fontes de dados (TSE — Dados Abertos)

| Arquivo | Conteúdo | Volume |
|---|---|---|
| `perfil_eleitor_secao_2024_PB.csv` | Perfil demográfico do eleitorado por seção | ~1.810.720 registros |
| `perfil_comparecimento_abstencao_2024_PB.csv` | Comparecimento e abstenção por zona eleitoral | ~302.947 registros |
| `eleitorado_local_votacao_2024_PB.csv` | Acessibilidade dos locais de votação por seção | 13.240 registros |

Todos disponíveis em: https://dadosabertos.tse.jus.br — licença Creative Commons, uso livre para fins acadêmicos.

---

## Coleções carregadas no MongoDB

| Coleção | Documentos | Observação |
|---|---|---|
| `municipios` | 223 | Completo |
| `zonas` | 68 | Completo; `nmSede` enriquecido via PDF TRE-PB |
| `secoes` | 10.626 | Completo; inclui `dsSituAcessibilidade` |
| `perfis` | 904.077 | Amostra estratificada de 50% (limite do tier gratuito do Atlas) |
| `comparecimentoZona` | 76 | Completo |

---

## Como rodar

### Pré-requisitos

- [Git](https://git-scm.com/)
- [Python 3.10+](https://www.python.org/)
- Conta no [MongoDB Atlas](https://www.mongodb.com/atlas) com cluster criado e usuário com permissão de leitura/escrita

### 1. Clonar o repositório

```bash
git clone https://github.com/LucianaNorat/eleicoes-pcd-2024-pb.git
cd eleicoes-pcd-2024-pb
```

### 2. Descompactar o dashboard

```bash
unzip ~/Downloads/eleicoes_pcd_dashboard.zip
cd eleicoes_pcd_dashboard
```

### 3. Criar e ativar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate          # Windows
```

### 4. Instalar dependências

```bash
pip install -r requirements.txt
```

### 5. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Abra o arquivo `.env` e preencha a variável `MONGO_URI` com a string de conexão do seu cluster no MongoDB Atlas:

```env
MONGO_URI=mongodb+srv://<usuario>:<senha>@<cluster>.mongodb.net/eleicoes_pcd_2024?retryWrites=true&w=majority
```

> **Como obter a URI:** no painel do MongoDB Atlas, acesse seu cluster → botão **Connect** → **Drivers** → copie a string de conexão e substitua `<usuario>` e `<senha>` pelas credenciais do seu usuário de banco.

### 6. Rodar o dashboard

```bash
python manage.py runserver
```

Acesse em: http://localhost:8000

---

## Aspectos legais (LGPD)

Os arquivos utilizados não contêm dados pessoais identificáveis — todos os registros são agregados por combinações de características demográficas dentro de uma seção eleitoral. O tratamento está em conformidade com a LGPD (Lei n.º 13.709/2018), uma vez que os dados são públicos, agregados e de natureza estatística.

---

## Licença

MIT License