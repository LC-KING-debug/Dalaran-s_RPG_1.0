from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET'])
def login_view():
    if 'user_id' in session:
        return redirect(url_for('game_view'))
    return render_template('login.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    dados = request.get_json() or {}
    username = dados.get('username', '').strip()
    password = dados.get('password', '').strip()
    
    if not username or not password:
        return jsonify({"message": "Preencha todos os campos."}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM usuarios WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"message": "Este operador já está registrado."}), 400
        
    password_hash = generate_password_hash(password)
    cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (username, password_hash))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "sucesso", "message": "Operador registrado com sucesso!"})

@auth_bp.route('/login', methods=['POST'])
def login():
    dados = request.get_json() or {}
    username = dados.get('username', '').strip()
    password = dados.get('password', '').strip()
    
    if not username or not password:
        return jsonify({"message": "Preencha todos os campos."}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
    usuario = cursor.fetchone()
    conn.close()
    
    if usuario and check_password_hash(usuario['password'], password):
        session['user_id'] = usuario['id']
        session['username'] = usuario['username']
        return jsonify({"status": "sucesso"})
        
    return jsonify({"message": "Credenciais inválidas. Acesso negado."}), 401

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login_view'))