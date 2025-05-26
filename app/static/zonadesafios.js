document.addEventListener('DOMContentLoaded', carregarDesafios);

async function carregarDesafios() {
  const feed = document.querySelector(".conteiner");
  const resposta = await fetch("/postagensdesafios");
  const desafios = await resposta.json();

  desafios.forEach(post => {
    const desafio = document.createElement("div");
    desafio.classList.add("card");
    desafio.setAttribute("data-id", post.id);
    desafio.setAttribute("data-resposta", post.correta);
    desafio.setAttribute("data-respondido", "false"); // proteção extra

    desafio.innerHTML = `
      <div class="perfil">
        <img class="foto-perfil" src="/static/assets/avatar.png" alt="Foto do usuário">
        <div>
          <strong>${post.autor}</strong><br>
          <span>${post.data}</span>
        </div>
      </div>
      <div class="conteudo">
        <p>${post.enunciado}</p>
        <button class="alternativa" data-alternativa="A">${post.A}</button>
        <button class="alternativa" data-alternativa="B">${post.B}</button>
        <button class="alternativa" data-alternativa="C">${post.C}</button>
        <button class="alternativa" data-alternativa="D">${post.D}</button>
      </div>
    `;
    
    feed.appendChild(desafio);
  });
}
document.addEventListener("click", function (event) {
  if (event.target.classList.contains("alternativa")) {
    const alternativaClicada = event.target.getAttribute("data-alternativa");
    const card = event.target.closest(".card");

    if (!card) return;

    const jaRespondido = card.getAttribute("data-respondido");
    if (jaRespondido === "true") return;

    const respostaCorreta = card.getAttribute("data-resposta");

    if (alternativaClicada === respostaCorreta) {
      // Acertou
      event.target.style.backgroundColor = "green";
    } else {
      // Errou
      event.target.style.backgroundColor = "red";

      // Mostra a correta
      const alternativaCorretaElemento = card.querySelector(`[data-alternativa="${respostaCorreta}"]`);
      if (alternativaCorretaElemento) {
        alternativaCorretaElemento.style.backgroundColor = "green";
      }
    }

    // Marcar como respondido
    card.setAttribute("data-respondido", "true");
  }
});