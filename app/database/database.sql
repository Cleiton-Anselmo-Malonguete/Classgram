-- Tabela de usuários
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    curso TEXT,
    classe TEXT,
    tipo TEXT DEFAULT 'aluno'  -- 'aluno' ou 'admin'
);

-- Tabela de desafios/apostas
CREATE TABLE apostas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT,
    data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
    criado_por INTEGER,
    FOREIGN KEY (criado_por) REFERENCES usuarios(id)
);

-- Participações dos usuários nas apostas
CREATE TABLE participacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER,
    id_aposta INTEGER,
    resposta TEXT,
    data_participacao TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY (id_aposta) REFERENCES apostas(id)
);

-- Postagens no mural ou feed
CREATE TABLE postagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER,
    conteudo TEXT NOT NULL,
    data_postagem TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);

-- Comentários nas postagens
CREATE TABLE comentarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_postagem INTEGER,
    id_usuario INTEGER,
    comentario TEXT,
    data_comentario TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_postagem) REFERENCES postagens(id),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);

-- Curtidas nas postagens
CREATE TABLE curtidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_postagem INTEGER,
    id_usuario INTEGER,
    data_curtida TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_postagem) REFERENCES postagens(id),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);

-- Recuperação de senhas
CREATE TABLE recuperacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telefone TEXT NOT NULL,
    codigo TEXT NOT NULL,
    expiracao TEXT,
    usado INTEGER DEFAULT 0  -- 0 = não usado, 1 = usado
);
-- Assinaturas dos usuários
CREATE TABLE assinaturas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER,
    plano TEXT NOT NULL, -- Ex: 'mensal', 'trimestral', 'anual'
    valor REAL NOT NULL, -- Valor pago
    data_inicio TEXT DEFAULT CURRENT_TIMESTAMP,
    data_fim TEXT,
    ativo INTEGER DEFAULT 1, -- 1 = ativo, 0 = expirado
    metodo_pagamento TEXT, -- Ex: 'M-Pesa', 'e-Mola'
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);
CREATE TABLE pontos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER,
    total_pontos INTEGER DEFAULT 0,
    atualizados_em TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);
CREATE TABLE medalhas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    imagem TEXT -- URL ou nome do arquivo da medalha
);

CREATE TABLE conquistas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER,
    id_medalha INTEGER,
    data_conquista TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY (id_medalha) REFERENCES medalhas(id)
);