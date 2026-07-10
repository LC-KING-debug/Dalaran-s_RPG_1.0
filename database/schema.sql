CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS personagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    classe TEXT NOT NULL, -- Monge, Mago ou Assassino
    nivel INTEGER DEFAULT 1,
    exp INTEGER DEFAULT 0,
    hp_atual INTEGER NOT NULL,
    hp_max INTEGER NOT NULL,
    ataque INTEGER NOT NULL,
    defesa INTEGER NOT NULL,
    inventario TEXT DEFAULT 'Pocao de Vida', -- Salvaremos como string separada por vírgulas
    sala_atual TEXT DEFAULT 'Entrada de Dalaran',
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);