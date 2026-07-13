import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Tabela de Personagens (Persistência do RPG via Serialização do Motor)
    cursor.execute('''
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
            inventario TEXT NOT NULL,
            sala_atual TEXT NOT NULL,
            inimigo_atual TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    ''')
    
    conn.commit()
    conn.close()