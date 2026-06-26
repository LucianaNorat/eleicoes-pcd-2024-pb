## Projeto da Disciplina de Banco de Dados
## Mestrado Profissional de Tecnologia da Informação

## Participação Eleitoral de Eleitores com Deficiência na Paraíba: Subnotificação Cadastral e Abstenção nas Eleições de 2024

**Equipe:** Luciana Norat | Monica Vasconcelos


## 1. Escopo (Definição do Problema)

### Problema de dados

Na Paraíba, não existe sistema que permita consultar, de forma integrada, como eleitores com deficiência (PCD) se distribuem por zona eleitoral. A proporção de PCD declarados nas zonas é consistentemente inferior ao esperado — indicando subnotificação cadastral. Identificar essas zonas permite ao TRE-PB planejar ações de atualização cadastral e garantir atendimento prioritário nas eleições de 2026. Complementarmente, a aplicação verifica se zonas com maior concentração de PCD apresentam taxas de abstenção mais elevadas, sinalizando barreiras de acesso ainda não superadas.

### Solução proposta

Pipeline ETL que extrai dois arquivos CSV do Portal de Dados Abertos do TSE (dadosabertos.tse.jus.br), transforma e integra dados de perfil do eleitorado e comparecimento/abstenção, e carrega o resultado no MongoDB. Sobre essa base são implementadas consultas analíticas expostas em dashboard interativo com filtros por município, zona eleitoral e tipo de deficiência.


# Como rodar

## 1. Descompactar dentro do repositório da Luciana
cd eleicoes-pcd-2024-pb
unzip ~/Downloads/eleicoes_pcd_dashboard.zip

## 2. Entrar na pasta
cd eleicoes_pcd_dashboard

## 3. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate          # Windows

## 4. Instalar dependências
pip install -r requirements.txt

## 5. Configurar variáveis de ambiente
cp .env.example .env
# Abrir .env e substituir <SENHA> pela senha real do MongoDB

## 6. Rodar
python manage.py runserver
# → http://localhost:8000