# Controle Financeiro (P1)

Projeto da disciplina **Laboratório de Programação Full Stack** — Universidade de Vassouras.

Sistema de controle financeiro pessoal com orçamento por categoria/mês e
parcelamento automático de despesas.

## Entidades

- **Conta** — onde o dinheiro está (conta corrente, poupança, carteira, cartão).
- **Categoria** — classificação de receitas/despesas (ex.: Alimentação, Transporte, Salário).
- **Lançamento** — uma movimentação financeira (receita ou despesa), à vista ou parcelada.
- **Parcela** — cada parcela gerada automaticamente a partir de um lançamento parcelado, com sua própria data de vencimento.
- **Orçamento** — limite de gasto planejado para uma categoria em um mês/ano.

## Escopo do P1

- CRUD funcional das 5 entidades (via telas próprias e via Django Admin).
- Ao cadastrar um lançamento marcado como "parcelado", o sistema **gera as
  parcelas automaticamente** (uma por mês, a partir da data do lançamento),
  dividindo o valor total entre elas.
- Ao cadastrar um orçamento (categoria + mês/ano + valor limite), o sistema
  **calcula o quanto já foi gasto** naquela categoria/mês (somando as parcelas
  que vencem no período) e mostra o percentual usado.
- Dashboard com saldo das contas, orçamentos do mês atual e parcelas em aberto.

## Escopo planejado para o P2

- Múltiplos espaços/organizações (cada usuário pode ter mais de um "espaço financeiro").
- Papéis de usuário (dono, membro etc.) e controle de acesso.
- Dashboard mais completo com gráficos.
- API REST com Django REST Framework (DRF).

## Stack

- Python + Django
- Banco de dados: SQLite (facilita rodar localmente sem instalar servidor de banco)
- python-dotenv (credenciais e `SECRET_KEY` fora do código-fonte)
- Bootstrap (via CDN) só para o layout das telas

## Como rodar localmente

Pré-requisito: **Python 3.11+ instalado** (verifique com `python --version`).

```powershell
# 1. criar e ativar o ambiente virtual
python -m venv venv
venv\Scripts\activate

# 2. instalar as dependências
pip install -r requirements.txt

# 3. copiar o arquivo de variáveis de ambiente
copy .env.example .env

# 4. criar as tabelas no banco (gera as migrations pela primeira vez)
python manage.py makemigrations
python manage.py migrate

# 5. carregar os dados de exemplo (contas, categorias, lançamentos, parcelas e orçamento)
python manage.py loaddata dados_exemplo

# 6. criar um usuário admin
python manage.py createsuperuser

# 7. rodar o servidor
python manage.py runserver
```

Depois acesse:

- **http://127.0.0.1:8000/** — telas do sistema (dashboard, lançamentos, orçamentos, parcelas)
- **http://127.0.0.1:8000/admin/** — Django Admin (cadastro rápido de contas e categorias)

## Dados de exemplo

O arquivo `financas/fixtures/dados_exemplo.json` traz dados prontos para testar
(o `db.sqlite3` não vai para o Git). Depois do `loaddata` o sistema já tem:

- 2 contas (Nubank e Carteira), 4 categorias (Alimentação, Transporte, Lazer e Salário);
- 6 lançamentos de 23/09/2026, incluindo um "Fone de ouvido" parcelado em 3x (parcelas em set, out e nov/2026);
- 1 orçamento de Alimentação para 09/2026.

Com eles dá para testar direto as features do P1:

- **Busca e filtro** (tela Lançamentos): buscar `mercado` traz "Mercado Extra" e
  "Uber para o mercado"; somando o filtro de categoria **Transporte**, sobra só o
  "Uber para o mercado". Uma busca sem resultado (ex.: `pizza`) mostra a mensagem
  de "nenhum lançamento encontrado".
- **Validação do valor** (tela Novo lançamento): salvar com valor `0` ou `-50`
  mostra o erro "O valor do lançamento deve ser maior que zero."

## Fluxo sugerido para testar

1. No Admin, cadastre pelo menos uma **Conta** e algumas **Categorias**.
2. Nas telas do sistema, cadastre um **Lançamento** de despesa parcelado em,
   por exemplo, 3x — confira que 3 **Parcelas** foram criadas automaticamente,
   uma por mês.
3. Cadastre um **Orçamento** para a mesma categoria, no mês de vencimento de
   uma das parcelas, e veja a barra de progresso do quanto já foi usado.

## Estrutura do projeto

```
financeiro/       # configurações do projeto (settings, urls)
financas/         # app com models, views, forms, admin e templates
manage.py
requirements.txt
.env.example
```
