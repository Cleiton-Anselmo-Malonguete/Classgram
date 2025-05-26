from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import sqlite3
import os
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'k4U#v9p!Lz3$wq1F'  # Chave secreta para sessão
CORS(app)

def conectar():
    caminho = os.path.join(os.path.dirname(__file__), 'database', 'meusite.db')
    return sqlite3.connect(caminho, check_same_thread=False)
    
def conectar_disciplina():
    caminho = os.path.join(os.path.dirname(__file__), 'database', 'disciplina.db')
    return sqlite3.connect(caminho, check_same_thread=False)

@app.route('/')
def index():
    # Se o usuário estiver logado, redireciona para o menu
    if 'telefone' in session:
        return redirect(url_for('painel'))
    return redirect(url_for('login'))

# Página de cadastro
@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def registrar_usuario():
    dados = request.get_json()
    nome = dados.get("nome", "").strip().title()
    telefone = dados.get("telefone")
    senha = dados.get("senha")
    classe = dados.get("classe")
    sessao = dados.get("sessao")

    if not senha or len(senha) < 8:
        return jsonify({"mensagem": "A senha deve ter pelo menos 8 caracteres."}), 400

    senha_hash = generate_password_hash(senha)

    try:
        with conectar() as con:
            cursor = con.cursor()
            cursor.execute(
                "INSERT INTO usuarios (nome, telefone, senha, classe, curso) VALUES (?, ?, ?, ?, ?)",
                (nome, telefone, senha_hash, classe, sessao)
            )
            con.commit()
        return jsonify({"mensagem": "Usuário registrado com sucesso!"})
    except Exception as e:
        return jsonify({"mensagem": f"Erro ao registrar: {str(e)}"}), 500
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        dados = request.get_json()
        telefone = dados.get('telefone')
        senha = dados.get('senha')

        con = conectar()
        cursor = con.cursor()
        cursor.execute("SELECT senha FROM usuarios WHERE telefone = ?", (telefone,))
        user = cursor.fetchone()
        con.close()

        if user and check_password_hash(user[0], senha):
            session['telefone'] = telefone
            return jsonify({"mensagem": "Login bem-sucedido"})
        else:
            return jsonify({"mensagem": "Telefone ou senha incorretos!"}), 401

    if 'telefone' in session:
        return redirect(url_for('painel'))

    return render_template('login.html')
    
@app.route('/recuperar_senha', methods=['GET'])
def recuperar_senha():
    return render_template('recuperar_senha.html')

@app.route('/recuperar_senha', methods=['POST'])
def redefinir_senha():
    dados = request.get_json()
    telefone = dados.get("telefone")
    nova_senha = dados.get("nova_senha")

    if not telefone or not nova_senha or len(nova_senha) < 8:
        return jsonify({"sucesso": False, "mensagem": "Dados inválidos ou senha muito curta."}), 400

    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE telefone = ?", (telefone,))
        usuario = cursor.fetchone()

        if usuario:
            senha_hash = generate_password_hash(nova_senha) 
            cursor.execute("UPDATE usuarios SET senha = ? WHERE telefone = ?", (senha_hash, telefone))
            con.commit()
            con.close()
            return jsonify({"sucesso": True, "mensagem": "Senha redefinida com sucesso."})
        else:
            con.close()
            return jsonify({"sucesso": False, "mensagem": "Telefone não encontrado."}), 404

    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": f"Erro: {str(e)}"}), 500
    
# Menu (tela protegida)



@app.route('/painel')
def painel():
    if 'telefone' not in session:
        return redirect(url_for('login'))

    return render_template('painel.html', telefone=session['telefone'])


@app.route('/criarpost', methods=['POST'])
def criar_post():
    if 'telefone' not in session:
        return jsonify({'status': 'erro', 'mensagem': 'Usuário não autenticado'}), 401

    data = request.json
    conteudo = data.get('conteudo')
    telefone = session['telefone']

    con = conectar()
    cursor = con.cursor()
    # Busca o id do usuário pelo telefone
    cursor.execute("SELECT id FROM usuarios WHERE telefone = ?", (telefone,))
    usuario = cursor.fetchone()
    if not usuario:
        return jsonify({'status': 'erro', 'mensagem': 'Usuário não encontrado'}), 404
    usuario_id = usuario[0]

    cursor.execute('INSERT INTO postagens (id_usuario, conteudo) VALUES (?, ?)', (usuario_id, conteudo))
    con.commit()
    return jsonify({'status': 'sucesso', 'mensagem': 'Post criado com sucesso'})
    
@app.route('/postagens')
def postagens():
    con = conectar()
    cursor = con.cursor()

    postagens = cursor.execute('''
        SELECT p.id, p.conteudo, p.data_postagem, u.nome
        FROM postagens p
        JOIN usuarios u ON p.id_usuario = u.id
        ORDER BY p.data_postagem DESC
    ''').fetchall()

    lista_postagens = []
    for p in postagens:
        id_postagem = p[0]
        comentarios = cursor.execute('''
            SELECT c.comentario, c.data_comentario, u.nome
            FROM comentarios c
            JOIN usuarios u ON c.id_usuario = u.id
            WHERE c.id_postagem = ?
            ORDER BY c.data_comentario ASC
        ''', (id_postagem,)).fetchall()
        quantidade_comentarios= cursor.execute('SELECT COUNT(*) FROM comentarios WHERE id_postagem = ?',(id_postagem,)).fetchall()

        lista_postagens.append({
            'id': id_postagem,
            'conteudo': p[1],
            'data': p[2],
            'autor': p[3],
            'curtidas': contarCurtidas(id_postagem), 
            'quantidade_comentarios':quantidade_comentarios,
            'comentarios': [
                {
                    'autor': c[2],
                    'comentario': c[0],
                    'data': c[1]
                } for c in comentarios
            ]
        })

    con.close()
    return jsonify(lista_postagens)

@app.route("/postagensdesafios" , methods=["GET"])
def potagensdesafios():
  con = conectar()
  cursor = con.cursor()
  desafios = cursor.execute("SELECT p.titulo , p.enunciado , p.alternativa_a , p.alternativa_b , p.alternativa_c , p.alternativa_d , p.resposta_correta ,p.criado_em ,u.nome FROM zona_desafios p JOIN usuarios u ON id_usuario = u.id  ").fetchall()
  lista_desafios =[]
  for desafio in desafios:
    id_desafio=desafio[0]
    lista_desafios.append({
      "titulo": desafio[0],
      "enunciado": desafio[1],
      "A": desafio[2],
      "B": desafio[3],
      "C": desafio[4],
      "D": desafio[5],
      "correta": desafio[6],
      "data": desafio[7],
      "autor": desafio[8]
      })
  con.commit()
  con.close()
  return jsonify(lista_desafios)
  
  
def contarCurtidas(id_postagem):
    con = conectar()
    cursor = con.cursor()

    resultado = cursor.execute('''
        SELECT COUNT(*) FROM curtidas WHERE id_postagem = ?
    ''', (id_postagem,)).fetchone()

    con.close()
    return resultado[0] if resultado else 0 
    
@app.route('/criarpost', methods=['GET', 'POST'])
def criarpost():
    if 'telefone' not in session:
        return jsonify({"mensagem": "Usuário não autenticado."}), 401

    if request.method == 'POST':
        dados = request.get_json()
        conteudo = dados.get("conteudo", "").strip()
        telefone = session['telefone']

        if not conteudo:
            return jsonify({"mensagem": "A postagem não pode estar vazia."}), 400

        try:
            con = conectar()
            cursor = con.cursor()
            # Buscar ID do usuário com base no telefone da sessão
            cursor.execute("SELECT id FROM usuarios WHERE telefone = ?", (telefone,))
            usuario = cursor.fetchone()
            if usuario:
                id_usuario = usuario[0]
                cursor.execute("INSERT INTO postagens (id_usuario, conteudo) VALUES (?, ?)", (id_usuario, conteudo))
                con.commit()
                return jsonify({"mensagem": "Postagem criada com sucesso!"})
            else:
                return jsonify({"mensagem": "Usuário não encontrado"}), 404
        except Exception as e:
            return jsonify({"mensagem": f"Erro ao criar postagem: {str(e)}"}), 500
        finally:
            con.close()

    return render_template("criarpost.html")
 
@app.route('/comentarios/<int:id_postagem>')
def pagina_comentarios(id_postagem):
    con = conectar()
    cursor = con.cursor()

    postagem = cursor.execute('''
        SELECT p.id, p.conteudo, p.data_postagem, u.nome
        FROM postagens p
        JOIN usuarios u ON p.id_usuario = u.id
        WHERE p.id = ?
    ''', (id_postagem,)).fetchone()

    comentarios = cursor.execute('''
        SELECT c.comentario, c.data_comentario, u.nome
        FROM comentarios c
        JOIN usuarios u ON c.id_usuario = u.id
        WHERE c.id_postagem = ?
        ORDER BY c.data_comentario ASC
    ''', (id_postagem,)).fetchall()

    con.close()

    return render_template('comentarios.html',
        postagem=postagem,
        comentarios=comentarios,
        curtidas=contarCurtidas(id_postagem)  # ou 0 se não quiser agora
    )
    
@app.route('/comentar_ajax/<int:id_postagem>', methods=['POST'])
def comentar_ajax(id_postagem):
    dados = request.get_json()
    comentario = dados.get("comentario")
    telefone = session['telefone']

    con = conectar()
    cursor = con.cursor()
    # Busca o id do usuário pelo telefone
    cursor.execute("SELECT id FROM usuarios WHERE telefone = ?", (telefone,))
    usuario = cursor.fetchone()
    id_usuario=usuario[0]

    if not id_usuario or not comentario:
        return jsonify({'status': 'erro'})

    con = conectar()
    cursor = con.cursor()
    cursor.execute('''
        INSERT INTO comentarios (id_postagem, id_usuario, comentario)
        VALUES (?, ?, ?)
    ''', (id_postagem, id_usuario, comentario))
    con.commit()

    autor = cursor.execute('SELECT nome FROM usuarios WHERE id = ?', (id_usuario,)).fetchone()[0]
    data = cursor.execute('SELECT data_comentario FROM comentarios WHERE id = (SELECT MAX(id) FROM comentarios)').fetchone()[0]

    con.close()

    return jsonify({
        'status': 'ok',
        'autor': autor,
        'comentario': comentario,
        'data': data
    })

   
@app.route('/comentar/<int:id_postagem>', methods=['POST'])
def comentar(id_postagem):
    dados = request.get_json()
    comentario = dados.get("comentario")
      # ou o nome correto da sua sessão
    telefone = session['telefone']

    con = conectar()
    cursor = con.cursor()
    # Busca o id do usuário pelo telefone
    cursor.execute("SELECT id FROM usuarios WHERE telefone = ?", (telefone,))
    usuario = cursor.fetchone()
    id_usuario=usuario[0]

    if not id_usuario:
        return redirect('/login')

    con = conectar()
    cursor = con.cursor()
    cursor.execute('''
        INSERT INTO comentarios (id_postagem, id_usuario, comentario)
        VALUES (?, ?, ?)
    ''', (id_postagem, id_usuario, comentario))
    con.commit()
    con.close()

    return redirect(f'/comentarios/{id_postagem}')
    
@app.route('/curtir', methods=['POST'])
def curtir_ou_descurtir():
    dados = request.json
    id_postagem = dados['id_postagem']
    telefone = session['telefone']# ou seu sistema de autenticação
    try:
      con = conectar()
      cursor = con.cursor()
      cursor.execute('SELECT id FROM usuarios WHERE telefone = ?' ,(telefone,))
      usuario = cursor.fetchone()
      id_usuario= usuario[0]
      con.commit()
      con.close()
    except Exception as e:
      return jsonify({"mensagem": f" usuario nao autenticado: {str(e)}"}), 500
      

    con = conectar()
    cursor = con.cursor()

    ja_curtiu = cursor.execute('SELECT 1 FROM curtidas WHERE id_postagem = ? AND id_usuario = ?', (id_postagem, id_usuario)).fetchone()

    if ja_curtiu:
        # Descurtir
        cursor.execute('DELETE FROM curtidas WHERE id_postagem = ? AND id_usuario = ?', (id_postagem, id_usuario))
        con.commit()
        curtiu = False
    else:
        # Curtir
        cursor.execute('INSERT INTO curtidas (id_postagem, id_usuario) VALUES (?, ?)', (id_postagem, id_usuario))
        con.commit()
        curtiu = True

    # Contar curtidas atualizadas
    total_curtidas = cursor.execute('SELECT COUNT(*) FROM curtidas WHERE id_postagem = ?', (id_postagem,)).fetchone()[0]
    con.close()

    return jsonify({
        'curtido': curtiu,
        'total_curtidas': total_curtidas
    })
    
@app.route('/desafios_disciplina/<disciplina>')
def desafios_disciplina(disciplina):
    # Aqui você pode usar o valor da disciplina recebido
    return render_template('desafios_disciplina.html', disciplina=disciplina)

from random import randint

@app.route('/quizzes', methods=["POST"])
def retornar_quizzes():
    dados = request.get_json()
    disciplina = dados.get("disciplina")

    if not disciplina:
        return jsonify({"mensagem": "Disciplina não fornecida"}), 400

    con = conectar_disciplina()

    try:
        cursor = con.cursor()
        # Verifica se a tabela é segura
        tabelas_permitidas = ["Matematica", "Fisica", "Quimica", "Biologia", "Lingua_Portuguesa", "Historia", "Geografia", "Ingles", "Filosofia", "Frances"]
        if disciplina not in tabelas_permitidas:
            return jsonify({"mensagem": "Disciplina inválida"}), 400

        total_query = f"SELECT COUNT(*) FROM {disciplina}"
        total = cursor.execute(total_query).fetchone()[0]

        if total == 0:
            return jsonify({"mensagem": "Nenhum quiz encontrado"}), 404

        id_quiz = randint(1, total)
        dados_query = f"SELECT * FROM {disciplina} WHERE id = ?"
        cursor.execute(dados_query, (id_quiz,))
        quiz = cursor.fetchone()

        con.close()

        if quiz:
            return jsonify({
                "pergunta": quiz[1],
                "A": quiz[2],
                "B": quiz[3],
                "C": quiz[4],
                "D": quiz[5],
                "correta": quiz[6]
            }), 200
        else:
            return jsonify({"mensagem": "Quiz não encontrado"}), 404

    except Exception as e:
        return jsonify({"mensagem": str(e)}), 500
@app.route("/pontos", methods=['POST'])
def atualizar_pontos():
    telefone = session.get('telefone')
    try:
        con = conectar()
        cursor = con.cursor()

        usuario = cursor.execute("SELECT id FROM usuarios WHERE telefone=?", (telefone,)).fetchone()
        if not usuario:
            return jsonify({'mensagem': "Usuário não encontrado", 'status': 400})

        id_usuario = usuario[0]
        dados = request.get_json()
        pontos = dados.get("pontos", 0)

        total = cursor.execute("SELECT total_pontos FROM pontos WHERE id_usuario=?", (id_usuario,)).fetchone()

        if total:  # já existe, então atualiza
            novo_total = total[0] + pontos
            cursor.execute("UPDATE pontos SET total_pontos=? WHERE id_usuario=?", (novo_total, id_usuario))
        else:  # ainda não tem, então insere
            cursor.execute("INSERT INTO pontos (id_usuario, total_pontos) VALUES (?, ?)", (id_usuario, pontos))

        con.commit()
        return jsonify({'mensagem': "Pontos inseridos com sucesso", 'status': 200})
    except Exception as e:
        return jsonify({'mensagem': f"Erro: {e}", 'status': 500})
      
  
@app.route("/zonadesafios")
def zona_desafios():
    return render_template("zonadesafios.html")
    

    

@app.route("/adicionar_desafio", methods=["GET", "POST"])
def adicionar_desafio():
  if 'telefone' not in session:
        return redirect(url_for('login'))
        
  if request.method == "GET":
    return render_template("adicionardesafio.html")
  elif request.method == "POST":
    titulo=request.form["titulo"]  
    resposta_correta=request.form["resposta_correta"]
    a = request.form["alternativa_a"]
    b = request.form["alternativa_b"]
    c = request.form["alternativa_c"]
    d = request.form["alternativa_d"]
    enunciado= request.form["enunciado"]
    telefone=session['telefone']
    con=conectar()
    cursor=con.cursor()
    usuario = cursor.execute("SELECT id FROM usuarios WHERE telefone=?", (telefone,)).fetchone()
    id_usuario=usuario[0]
    con.execute('INSERT INTO zona_desafios(id_usuario , titulo, enunciado , alternativa_a , alternativa_b ,alternativa_c , alternativa_d , resposta_correta) VALUES(?,?,?,?,?,?,?,?)',(id_usuario,titulo,enunciado,a ,b,c,d,resposta_correta)) 
    con.commit()
    con.close()

    
    return  redirect("/zonadesafios")
  
@app.route("/perfil/<telefone>")
def perfil(telefone):
    con = conectar()
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Buscar dados do usuário
    cur.execute("SELECT id, nome, classe FROM usuarios WHERE telefone = ?", (telefone,))
    usuario = cur.fetchone()

    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    # Buscar pontos na tabela "pontos"
    cur.execute("SELECT total_pontos FROM pontos WHERE id_usuario = ?", (usuario["id"],))
    pontos = cur.fetchone()
    pontos = pontos[0] if pontos else 0

    # Total de seguidores (pessoas que seguem esse usuário)
    cur.execute("SELECT COUNT(*) FROM seguidores WHERE seguido = ?", (telefone,))
    total_seguidores = cur.fetchone()[0]

    # Total que ele segue (pessoas que esse usuário segue)
    cur.execute("SELECT COUNT(*) FROM seguidores WHERE seguidor = ?", (telefone,))
    total_seguindo = cur.fetchone()[0]

    # Total de postagens
   # Primeiro, busque o id do usuário pelo telefone (você já faz isso acima):
    id_usuario = usuario["id"]
    cur.execute("SELECT COUNT(*) FROM postagens WHERE id_usuario = ?", (id_usuario,))
    total_postagens = cur.fetchone()[0]


    dados = {
        "nome": usuario["nome"],
        "classe": usuario["classe"],
        "pontos": pontos,
        "total_postagens": total_postagens,
        "total_seguidores": total_seguidores,
        "total_seguindo": total_seguindo
    }

    return jsonify(dados)
    
@app.route("/irperfil")
def irperfil():
    telefone_logado = session.get("telefone")
    if not telefone_logado:
        return redirect("/login")
    return render_template("profile.html", telefone=telefone_logado)
    
@app.route("/postagens/<telefone>")
def postagens_por_telefone(telefone):
    pagina = int(request.args.get("pagina", 1))
    limite = 5
    offset = (pagina - 1) * limite

    conn = conectar()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    usuario = cursor.execute("SELECT id, nome FROM usuarios WHERE telefone=?", (telefone,)).fetchone()
    if not usuario:
        conn.close()
        return jsonify([])

    id_usuario = usuario["id"]
    nome_usuario = usuario["nome"]

    cursor.execute("""
        SELECT 
            p.id, 
            p.conteudo, 
            p.data_postagem AS data,
            (SELECT COUNT(*) FROM curtidas WHERE id_postagem = p.id) AS curtidas,
            (SELECT COUNT(*) FROM comentarios WHERE id_postagem = p.id) AS quantidade_comentarios
        FROM postagens p
        WHERE p.id_usuario = ?
        ORDER BY p.data_postagem DESC
        LIMIT ? OFFSET ?
    """, (id_usuario, limite, offset))

    postagens = []
    for row in cursor.fetchall():
        postagens.append({
            "id": row["id"],
            "autor": nome_usuario,
            "data": row["data"],
            "conteudo": row["conteudo"],
            "curtidas": row["curtidas"],
            "quantidade_comentarios": row["quantidade_comentarios"]
        })

    conn.close()
    return jsonify(postagens)

@app.route("/verificar_segue/<telefone_alvo>")
def verificar_segue(telefone_alvo):
    telefone_logado = session.get("telefone")

    # Se não estiver logado ou for o próprio perfil, não mostrar o botão
    if not telefone_logado or telefone_logado == telefone_alvo:
        return jsonify({
            "mostrar_botao": False,
            "segue": False
        })

    con = conectar()
    cur = con.cursor()
    cur.execute("""
        SELECT 1 FROM seguidores 
        WHERE seguidor = ? AND seguido = ?
    """, (telefone_logado, telefone_alvo))
    
    resultado = cur.fetchone()
    return jsonify({
        "mostrar_botao": True,
        "segue": resultado is not None
    })
 
@app.route("/seguir/<int:id_usuario>", methods=["POST"])
def seguir_usuario(id_usuario):
    telefone = session.get("telefone")
    if not telefone:
        return jsonify({"erro": "Não logado"}), 403

    con = conectar()
    con.row_factory = sqlite3.Row  # Adicione isso aqui
    cur = con.cursor()

    # Buscar o telefone do usuário a ser seguido
    cur.execute("SELECT telefone FROM usuarios WHERE id = ?", (id_usuario,))
    destino = cur.fetchone()
    if not destino:
        con.close()
        return jsonify({"erro": "Usuário a seguir não encontrado"}), 404

    telefone_destino = destino["telefone"]

    # Verifica se já está seguindo
    cur.execute("SELECT 1 FROM seguidores WHERE seguidor = ? AND seguido = ?", (telefone, telefone_destino))
    ja_segue = cur.fetchone()

    if ja_segue:
        cur.execute("DELETE FROM seguidores WHERE seguidor = ? AND seguido = ?", (telefone, telefone_destino))
    else:
        cur.execute("INSERT INTO seguidores (seguidor, seguido) VALUES (?, ?)", (telefone, telefone_destino))

    con.commit()
    con.close()
    return jsonify({"sucesso": True})
    
@app.route("/usuarios")
def usuarios():
    telefone_logado = session.get("telefone")
    if not telefone_logado:
        return redirect("/login")

    con = conectar()
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Buscar ID do usuário logado
    cur.execute("SELECT id FROM usuarios WHERE telefone = ?", (telefone_logado,))
    usuario_logado = cur.fetchone()
    if not usuario_logado:
        return redirect("/login")

    id_logado = usuario_logado["id"]

    # Selecionar usuários que o logado ainda não segue
    cur.execute("""
        SELECT u.id, u.nome
        FROM usuarios u
        WHERE u.id != ?
        AND u.id NOT IN (
            SELECT seguido FROM seguidores WHERE seguido = ?
        )
        LIMIT 20
    """, (id_logado, id_logado))
    
    sugeridos = cur.fetchall()

    return render_template("usuarios.html", usuarios=sugeridos)  


@app.route("/listar_usuarios")
def listar_usuarios():
    telefone = session.get("telefone")
    if not telefone:
        return jsonify([])

    con = conectar()
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Pega o ID do usuário logado
    usuario_logado = cur.execute("SELECT id FROM usuarios WHERE telefone=?", (telefone,)).fetchone()
    if not usuario_logado:
        return jsonify([])

    id_logado = usuario_logado["id"]

    # Pega todos os usuários, exceto ele mesmo
    usuarios = cur.execute("SELECT id, nome, classe FROM usuarios WHERE id != ?", (id_logado,)).fetchall()

    # Pega IDs que ele já segue
    seguindo = cur.execute("SELECT seguido FROM seguidores WHERE seguidor = ?", (telefone,)).fetchall()
    ids_seguindo = set(row["seguido"] for row in seguindo)

    lista = []
    for u in usuarios:
        lista.append({
            "id": u["id"],
            "nome": u["nome"],
            "classe": u["classe"],
            "seguindo": u["id"] in ids_seguindo
        })

    return jsonify(lista)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)