```text
Esrutura da aplicação:

Dalarans-RPG/
│
├── app.py                  # Inicializa o Flask
├── config.py               # Configurações
├── requirements.txt        # Requisitos para rodar
├── .env
│
├── database/
│   ├── db.py               # Conexão com MySQL
│   └── schema.sql          # Criação da estrutura do banco
│
├── routes/
│   ├── auth.py             # Login, cadastro, logout
│   └── game.py             # Comandos do jogo
│
├── templates/
│   ├── login.html          #Página de cadastro e login do jogo
│   └── index.html          #Página principal do game com terminal
│
└── static/
    ├── css/
    │   ├── login.css       #Estilização no arquivo login.html(preto e verde neon)
    │   └── game.css        #Estilização no arquivo index.html
    │
    └── js/
        ├── login.js        #Mudança de eventos e conectividade com fetch
        └── game.js
```
