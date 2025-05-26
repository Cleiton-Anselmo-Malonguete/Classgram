async function CadastrarUsuario(event) {
  event.preventDefault();

  const nome = document.querySelector("#nome").value;
  const telefone = document.querySelector("#telefone").value;
  const senha = document.querySelector("#senha").value;
  const confirmarSenha = document.querySelector("#confirmar_senha").value;
  const classe = document.querySelector("#classe").value;
  const sessao = document.querySelector("#sessao").value;

  if (senha !== confirmarSenha) {
    alert("Verifique a senha e tente novamente.");
    return;
  }

  try {
    const resposta = await fetch("/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome, telefone, senha, classe, sessao })
    });

    const dados = await resposta.json();

    if (resposta.ok) {
      alert(dados.mensagem);
      window.location.href = "/painel";
    } else {
      alert("Erro: " + dados.mensagem);
    }
  } catch (erro) {
    alert("Erro na conexão com o servidor.");
    console.error(erro);
  }
}