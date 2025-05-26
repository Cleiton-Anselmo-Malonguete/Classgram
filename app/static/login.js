async function LogarUsuario(event) {
  event.preventDefault(); // Impede o recarregamento da página

  const telefone = document.getElementById("telefone").value;
  const senha = document.getElementById("senha").value;

  if (!telefone || !senha) {
    alert("Preencha todos os campos.");
    return;
  }

  try {
    const resposta = await fetch("/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ telefone, senha })
    });

    const dados = await resposta.json();

    if (resposta.ok) {
      alert("Login bem-sucedido!")
      window.location.href = "/painel";  // fecha a string corretamente
    } else {
      alert(dados.mensagem || "Erro ao fazer login");
    }
  } catch (error) {
    alert("Erro de conexão com o servidor");
  }
}