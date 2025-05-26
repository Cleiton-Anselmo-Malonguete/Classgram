document.addEventListener('DOMContentLoaded', carregarDesafios);

async function carregarDesafios() {
  document.getElementById("continuar").style.display = "none";
  const disciplina = document.getElementById("disciplina").textContent;

  const resposta = await fetch('/quizzes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ disciplina: disciplina })
  });

  const dados = await resposta.json();

  if (resposta.status == 200) {
    document.querySelector(".pergunta").textContent = dados.pergunta;

    // Atualizar texto e substituir botões
    const botoesAntigos = document.querySelectorAll('.alternativa');
    const alternativas = [dados.A, dados.B, dados.C, dados.D];

    alternativas.forEach((texto, i) => {
      const botaoNovo = botoesAntigos[i].cloneNode(true);
      botaoNovo.textContent = texto;
      botaoNovo.style.backgroundColor = "";
      botoesAntigos[i].parentNode.replaceChild(botaoNovo, botoesAntigos[i]);
    });

    // Agora selecione novamente os botões atualizados
    const botoes = document.querySelectorAll('.alternativa');

    botoes.forEach((botao, i) => {
      botao.addEventListener('click', () => {
        const respostaSelecionada = botao;
        const correta = dados.correta.toUpperCase();
        let corretaElement = null;
        document.getElementById("continuar").style.display = "block";

        if (correta === 'A') corretaElement = botoes[0];
        else if (correta === 'B') corretaElement = botoes[1];
        else if (correta === 'C') corretaElement = botoes[2];
        else if (correta === 'D') corretaElement = botoes[3];

        if (corretaElement.textContent === respostaSelecionada.textContent) {
          fetch("/pontos", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ "pontos": 10 })
          })
        }
    

        corretaElement.style.backgroundColor = 'green';
        if (corretaElement !== respostaSelecionada) {
          respostaSelecionada.style.backgroundColor = 'red';
        }
      });
    });

  } else {
    alert('erro: ' + dados.mensagem);
  }
}