# Dalaran's RPG 1.0

OBS: Projeto ainda em desenvolvimento

Estrutura da aplicação:

meu-rpg-flask/
├── database/                    -> [Pasta] Controle e persistência do banco de dados
│   ├── __init__.py              -> Inicializador do pacote Python da pasta
│   ├── db.py                    -> Configura a conexão e funções do SQLite
│   ├── schema.sql               -> Estrutura das tabelas (usuarios e personagens)
│   └── dalaran.db               -> [Ignorado] Arquivo do banco de dados local
│
├── routes/                      -> [Pasta] Lógica e inteligência por trás das telas
│   ├── __init__.py              -> Inicializador do pacote Python da pasta
│   ├── auth.py                  -> Cuida do login, registro e controle de senhas
│   └── game.py                  -> É o motor do jogo (classes Personagem, Inimigo e salas)
│
├── static/                      -> [Pasta] Arquivos visuais enviados ao navegador
│   ├── assets/                  -> [Pasta] Imagens, ícones e efeitos sonoros do RPG
│   ├── css/                     -> [Pasta] Estilos visuais das páginas
│   │   ├── game.css             -> Visual estilo terminal preto e verde do console
│   │   └── login.css            -> Visual da tela de entrada e cadastro
│   └── js/                      -> [Pasta] Scripts assíncronos (comunicação com Python)
│       ├── game.js              -> Envia comandos e atualiza o terminal do jogo sem recarregar
│       └── login.js             -> Valida formulários e faz o envio seguro do login
│
├── templates/                   -> [Pasta] Estrutura das páginas HTML que o Flask renderiza
│   ├── index.html               -> A tela principal do jogo (o console de comandos)
│   └── login.html               -> A tela inicial de login e registro de novas contas
│
├── .env                         -> [Ignorado] Guarda chaves secretas de ambiente em segurança
├── .gitignore                   -> Lista de arquivos que o Git não deve subir para o GitHub
├── a fazeres.txt                -> Suas notas e anotações pessoais de desenvolvimento
├── app.py                       -> O servidor central do Flask que une o banco, rotas e front-end
├── database.db                  -> [Ignorado] Arquivo do banco de dados local (raiz)
├── readme.md                    -> Documentação explicativa do seu projeto para o GitHub
└── requirements.txt             -> Lista de dependências (Flask, Werkzeug) para rodar o app