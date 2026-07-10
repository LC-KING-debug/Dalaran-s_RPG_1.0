from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from routes.game import Game, Personagem
from database.db import init_db, get_db_connection
from routes.auth import auth_bp  
import os

app = Flask(__name__)
app.secret_key = "dalaran_secret_key_fixed"

app.register_blueprint(auth_bp)
init_db()

jogos_ativos = {}

def carregar_jogo_para_memoria(user_id, personagem_row):
    p = Personagem(personagem_row['nome'], personagem_row['classe'])
    p.nivel = int(personagem_row['nivel'])
    p.hp = int(personagem_row['hp'])
    p.hp_max = int(personagem_row['hp_max'])
    p.exp = int(personagem_row['exp'])
    p.exp_necessaria = int(100 * (1.5 ** (p.nivel - 1)))
    
    for _ in range(1, p.nivel):
        p.ataque = int(p.ataque * 1.15)
        p.defesa = int(p.defesa * 1.15)
    
    inv_banco = personagem_row['inventario']
    if inv_banco:
        p.inventario = [item.strip() for item in inv_banco.split(',') if item.strip()]
    else:
        p.inventario = []
    
    game_instance = Game(p.nome, p.classe)
    game_instance.player = p
    jogos_ativos[user_id] = game_instance

def salvar_jogo_no_banco(user_id):
    if user_id in jogos_ativos:
        game = jogos_ativos[user_id]
        p = game.player
        inventario_str = ",".join(p.inventario)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE personagens 
            SET nivel = ?, exp = ?, hp = ?, hp_max = ?, inventario = ?
            WHERE usuario_id = ? AND nome = ?
        ''', (p.nivel, p.exp, p.hp, p.hp_max, inventario_str, session.get('user_id'), p.nome))
        conn.commit()
        conn.close()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login_view'))
    return redirect(url_for('tela_personagens_view'))

@app.route('/tela_personagens')
def tela_personagens_view():
    if 'user_id' not in session:
        return redirect(url_for('auth.login_view'))
    return render_template('tela_personagens.html')

@app.route('/game')
def game_view():
    if 'user_id' not in session:
        return redirect(url_for('auth.login_view'))
    if session['user_id'] not in jogos_ativos:
        return redirect(url_for('tela_personagens_view'))
    return render_template('index.html')

@app.route('/listar_personagens', methods=['GET'])
def listar_personagens():
    if 'user_id' not in session:
        return jsonify({"erro": "Não autenticado"}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nome, classe, nivel, hp, hp_max FROM personagens WHERE usuario_id = ?", 
        (session['user_id'],)
    )
    rows = cursor.fetchall()
    conn.close()
    
    lista = [dict(r) for r in rows]
    return jsonify({"status": "sucesso", "personagens": lista})

@app.route('/selecionar_personagem', methods=['POST'])
def selecionar_personagem():
    if 'user_id' not in session:
        return jsonify({"erro": "Não autenticado"}), 401
        
    dados = request.get_json() or {}
    nome = dados.get('nome')
    
    if not nome:
        return jsonify({"erro": "Nome do avatar não especificado"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM personagens WHERE usuario_id = ? AND nome = ?", 
        (session['user_id'], nome)
    )
    personagem_row = cursor.fetchone()
    conn.close()
    
    if not personagem_row:
        return jsonify({"erro": "Avatar não encontrado no sistema"}), 404
        
    user_id = session['user_id']
    carregar_jogo_para_memoria(user_id, personagem_row)
    
    return jsonify({
        "status": "sucesso",
        "status_inicial": jogos_ativos[user_id].player.status_formatado()
    })

@app.route('/criar_personagem', methods=['POST'])
def criar_personagem():
    if 'user_id' not in session:
        return jsonify({"erro": "Não autenticado"}), 401
        
    dados = request.get_json() or {}
    nome = dados.get('nome', '').strip()
    classe = dados.get('classe', '').strip()
    
    if not nome or not classe:
        return jsonify({"erro": "Dados insuficientes para criação."}), 400
        
    classes_validas = ["monge", "mago", "assassino"]
    if classe.lower() not in classes_validas:
        return jsonify({"erro": "Classe operacional inválida."}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM personagens WHERE usuario_id = ?", (session['user_id'],))
    if cursor.fetchone()['total'] >= 3:
        conn.close()
        return jsonify({"erro": "Limite máximo de 3 avatares atingido."}), 400
        
    cursor.execute("SELECT id FROM personagens WHERE usuario_id = ? AND nome = ?", (session['user_id'], nome))
    if cursor.fetchone():
        conn.close()
        return jsonify({"erro": "Você já possui um avatar com este nome."}), 400

    if classe.lower() == "monge":
        hp_base = 120
    elif classe.lower() == "mago":
        hp_base = 80
    else:
        hp_base = 95
    
    cursor.execute('''
        INSERT INTO personagens (usuario_id, nome, classe, hp, hp_max, inventario) 
        VALUES (?, ?, ?, ?, ?, 'Pocao de Vida')
    ''', (session['user_id'], nome, classe, hp_base, hp_base))
    conn.commit()
    
    cursor.execute("SELECT * FROM personagens WHERE usuario_id = ? AND nome = ?", (session['user_id'], nome))
    personagem_row = cursor.fetchone()
    conn.close()
    
    user_id = session['user_id']
    carregar_jogo_para_memoria(user_id, personagem_row)
    
    return jsonify({
        "status": "sucesso",
        "status_inicial": jogos_ativos[user_id].player.status_formatado()
    })

@app.route('/deletar_personagem', methods=['POST'])
def deletar_personagem():
    if 'user_id' not in session:
        return jsonify({"erro": "Não autenticado"}), 401
        
    dados = request.get_json() or {}
    nome = dados.get('nome')
    
    if not nome:
        return jsonify({"erro": "Nome inválido"}), 400
        
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM personagens WHERE usuario_id = ? AND nome = ?", (user_id, nome))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"erro": "Avatar não localizado."}), 404
        
    cursor.execute("DELETE FROM personagens WHERE usuario_id = ? AND nome = ?", (user_id, nome))
    conn.commit()
    conn.close()
    
    if user_id in jogos_ativos and jogos_ativos[user_id].player.nome == nome:
        del jogos_ativos[user_id]
        
    return jsonify({"status": "sucesso"})

@app.route('/comando', methods=['POST'])
def comando():
    user_id = session.get('user_id')
    if not user_id or user_id not in jogos_ativos:
        return jsonify({"logs": ["[SISTEMA] Erro: Conexão interrompida. Selecione seu avatar novamente."]}), 400
        
    dados = request.get_json() or {}
    cmd_texto = dados.get('comando', '')
    
    jogo = jogos_ativos[user_id]
    logs_resposta = jogo.process_command(cmd_texto)
    
    salvar_jogo_no_banco(user_id)
    
    return jsonify({
        "logs": logs_resposta,
        "status_jogador": jogo.player.status_formatado()
    })

if __name__ == '__main__':
    app.run(debug=True)