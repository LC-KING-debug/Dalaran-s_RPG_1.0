CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS personagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    classe TEXT NOT NULL,
    nivel INTEGER DEFAULT 1,
    exp INTEGER DEFAULT 0,
    exp_necessaria INTEGER DEFAULT 100,
    hp INTEGER NOT NULL,
    hp_max INTEGER NOT NULL,
    ataque INTEGER NOT NULL,
    defesa INTEGER NOT NULL,
    habilidade_especial TEXT NOT NULL,
    inventario TEXT NOT NULL, -- Será armazenado como JSON
    sala_atual TEXT NOT NULL,
    inimigo_atual TEXT, -- Será armazenado como JSON ou NULL
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);