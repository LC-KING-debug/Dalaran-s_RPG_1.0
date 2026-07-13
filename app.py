from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
from routes.game import Game, CLASSES_DISPONIVEIS
from database.db import init_db, get_db_connection
from routes.auth import auth_bp  
import os

app = Flask(__name__)
app.secret_key = "dalaran_secret_key_fixed"

app.register_blueprint(auth_bp)
init_db()

jogos_ativos = {}

def carregar_jogo_para_memoria(user_id, personagem_row):
    """Reconstrói a partida extraindo colunas do DB para o formato exigido por Game.from_dict"""
    data = {
        "player": {
            "nome": personagem_row['nome'],
            "classe": personagem_row['classe'],
            "nivel": int(personagem_row['nivel']),
            "exp": int(personagem_row['exp']),
            "exp_necessaria": int(personagem_row['exp_necessaria']),
            "hp": int(personagem_row['hp']),
            "hp_max": int(personagem_row['hp_max']),
            "ataque": int(personagem_row['ataque']),
            "defesa": int(personagem_row['defesa']),
            "habilidade_especial": personagem_row['habilidade_especial'],
            "inventario": json.loads(personagem_row['inventario']) if personagem_row['inventario'] else {}
        },
        "sala_atual": personagem_row['sala_atual'],
        "inimigo_atual": json.loads(personagem_row['inimigo_atual']) if personagem_row['inimigo_atual'] else None
    }
    
    game_instance = Game.from_dict(data)
    jogos_ativos[user_id] = game_instance

def salvar_jogo_no_banco(user_id):
    """Salva os atributos dinâmicos a partir do retorno to_dict()"""
    if user_id in jogos_ativos:
        game = jogos_ativos[user_id]
        estado = game.to_dict()
        p = estado["player"]
        
        inventario_json = json.dumps(p["inventario"])
        inimigo_json = json.dumps(estado["inimigo_atual"]) if estado["inimigo_atual"] else None
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE personagens 
            SET nivel = ?, exp = ?, exp_necessaria = ?, hp = ?, hp_max = ?,
                ataque = ?, defesa = ?, inventario = ?, sala_atual = ?, inimigo_atual = ?
            WHERE usuario_id = ? AND nome = ?
        ''', (
            p["nivel"], p["exp"], p["exp_necessaria"], p["hp"], p["hp_max"],
            p["ataque"], p["defesa"], inventario_json, estado["sala_atual"], inimigo_json,
            session.get('user_id'), p["nome"]
        ))
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
        
    # Valida usando o próprio dicionário do game.py
    classes_validas = list(CLASSES_DISPONIVEIS.keys())
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

    # Cria instanciando o motor para obter todos os status base exatos de forma automática
    novo_jogo = Game(nome, classe)
    estado = novo_jogo.to_dict()
    p = estado["player"]
    
    inventario_json = json.dumps(p["inventario"])
    inimigo_json = json.dumps(estado["inimigo_atual"]) if estado["inimigo_atual"] else None

    cursor.execute('''
        INSERT INTO personagens (
            usuario_id, nome, classe, nivel, exp, exp_necessaria, hp, hp_max,
            ataque, defesa, habilidade_especial, inventario, sala_atual, inimigo_atual
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        session['user_id'], p["nome"], p["classe"], p["nivel"], p["exp"], p["exp_necessaria"],
        p["hp"], p["hp_max"], p["ataque"], p["defesa"], p["habilidade_especial"],
        inventario_json, estado["sala_atual"], inimigo_json
    ))
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