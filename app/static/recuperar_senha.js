document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const telefone = document.getElementById("telefone").value.trim();
        const novaSenha = document.getElementById("nova_senha").value;
        const confirmarSenha = document.getElementById("confirmar_senha").value;

        if (novaSenha.length < 8) {
            alert("A senha deve ter pelo menos 8 caracteres.");
            return;
        }

        if (novaSenha !== confirmarSenha) {
            alert("As senhas não coincidem.");
            return;
        }

        fetch("/recuperar_senha", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                telefone: telefone,
                nova_senha: novaSenha
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Erro ao atualizar senha");
            }
            return response.json();
        })
        .then(data => {
            alert("Senha redefinida com sucesso!");
            window.location.href = "/login";
        })
        .catch(error => {
            console.error("Erro:", error);
            alert("Erro ao redefinir a senha. Verifique o número ou tente novamente.");
        });
    });
});