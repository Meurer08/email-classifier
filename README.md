📬 Email Classifier & Auto-Reply Generator

Aplicação web que classifica e-mails como Produtivos ou Improdutivos e gera automaticamente respostas adequadas utilizando modelos da Hugging Face.

🚀 Funcionalidades

Classificação de e-mails usando facebook/bart-large-mnli
Geração de respostas usando Qwen/Qwen2.5-1.5B-Instruct
Interface web simples e intuitiva
Salvamento local dos e-mails (localStorage)
Filtros por categoria
Exclusão de e-mails cadastrados
Backend em Flask com integração ao Hugging Face Inference API

🏗️ Estrutura do Projeto
O core da aplicação está concentrado no arquivo principal (app.py ou similar, onde o código foi implementado).

Rotas:

GET /: Página inicial/Status da API.

POST /generate: Rota principal para processar e-mails.

#Configurar o Ambiente e Instalar Dependências
1. Crie um ambiente virtual e instale todas as bibliotecas necessárias listadas no seu requirements.txt.

pip install -r requirements.txt

2. Executar a Aplicação
Inicie o servidor Flask executando o arquivo principal, que assume ser app.py.

python3 app.py
