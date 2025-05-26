document.addEventListener('DOMContentLoaded', carregarPostagens);

async function carregarPostagens() {
    const feed = document.getElementById('feed');
    try {
        const resposta = await fetch('/postagens');
        const postagens = await resposta.json();

        feed.innerHTML = ''; // limpa antes de adicionar
postagens.forEach(post => {
    const postagem = document.createElement('div');
    postagem.classList.add('postagem');
    postagem.setAttribute('data-id', post.id);
    
    postagem.innerHTML = `
        <div class="cabecalho-postagem">
            <img class="foto-perfil" src="/static/assets/avatar.png" alt="Foto do usuário">
            <div>
                <strong>${post.autor}</strong><br>
                <small>${post.data} • <i class="fas fa-users"></i></small>
            </div>
        </div>
        <div class="conteudo-postagem">
            <p>${post.conteudo}</p>
        </div>
        <div class="reacoes">
            <i class="fas fa-thumbs-up" style="color:blue;"></i> ${post.curtidas} curtidas
        </div>
        <div class="acoes-postagem">
            <button onclick='Gostar(this , ${post.id})'><i class="far fa-thumbs-up"></i> Gosto</button>
         <button onclick="irParaComentarios(${post.id})">
         <i class="far fa-comment"></i>${post.quantidade_comentarios}</button>
            <button><i class="fas fa-share"></i> Partilhar</button>
        </div>
        <div class="comentarios"></div>
    `;

    const comentariosDiv = postagem.querySelector('.comentarios');


    feed.appendChild(postagem);
});
        
    } catch (erro) {
        console.error('Erro ao carregar postagens:', erro);
        feed.innerHTML = '<p>Erro ao carregar postagens.</p>';
    }
}
function irParaComentarios(id) {
    window.location.href = `/comentarios/${id}`;
}
function irParaZonadesafios(){
  window.location.href="/zonadesafios"
}

function irParaDesafiosDisciplinas(disciplina) {
  const encodedDisciplina = encodeURIComponent(disciplina); // evita bugs com espaços
  window.location.href = `/desafios_disciplina/${encodedDisciplina}`;
}

function fecharModal() {
    document.getElementById('modal-comentario').style.display = 'none';
}

function enviarComentario(){
    const id_postagem = document.getElementById('comentario-id-postagem').value;
    const texto = document.getElementById('comentario-texto').value.trim();

    if (texto === '') return;

    fetch('/comentar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id_postagem: id_postagem, comentario: texto })
    })
    .then(res => res.json())
    .then(dados => {
        fecharModal();

        // Opcional: adicionar visualmente o novo comentário
        const postagem = document.querySelector(`.postagem[data-id="${id_postagem}"]`);
        let comentariosDiv = postagem.querySelector('.comentarios');

        if (!comentariosDiv) {
            comentariosDiv = document.createElement('div');
            comentariosDiv.classList.add('comentarios');
            postagem.appendChild(comentariosDiv);
        }

        const novoComentario = document.createElement('div');
        novoComentario.innerHTML = `<strong>${dados.autor}</strong>: ${dados.comentario}`;
        comentariosDiv.appendChild(novoComentario);
    });
}

function Gostar(botao, id_postagem) {
    fetch('/curtir', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id_postagem: id_postagem })
    })
    .then(res => res.json())
    .then(dados => {
        const icone = botao.querySelector('i');
        const texto = botao;

        if (dados.curtido) {
            icone.classList.remove('far');
            icone.classList.add('fas');
            texto.innerHTML = '<i class="fas fa-thumbs-up"></i> Gostou';
        } else {
            icone.classList.remove('fas');
            icone.classList.add('far');
            texto.innerHTML = '<i class="far fa-thumbs-up"></i> Gosto';
        }

        // Atualizar número de curtidas visível
        const reacoes = botao.closest('.postagem').querySelector('.reacoes');
        reacoes.innerHTML = `<i class="fas fa-thumbs-up" style="color:blue;"></i> ${dados.total_curtidas} curtidas`;
    });
}

