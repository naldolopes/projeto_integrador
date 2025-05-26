-- Script SQLite - Sistema de Farmácia
-- Atualizado para compatibilidade total com o backend Flask

-- Tabela: Usuario
CREATE TABLE Usuario (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('paciente', 'medico', 'admin'))
);

-- Tabela: Paciente
CREATE TABLE Paciente (
    id_paciente INTEGER PRIMARY KEY,
    cpf TEXT UNIQUE,
    telefone TEXT,
    endereco TEXT,
    FOREIGN KEY (id_paciente) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);

-- Tabela: Medico
CREATE TABLE Medico (
    id_medico INTEGER PRIMARY KEY,
    crm TEXT UNIQUE NOT NULL,
    especialidade TEXT NOT NULL,
    FOREIGN KEY (id_medico) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);

-- Tabela: Farmacia (atualizada com coordenadas geográficas)
CREATE TABLE Farmacia (
    id_farmacia INTEGER PRIMARY KEY AUTOINCREMENT,
    cnpj TEXT UNIQUE NOT NULL,
    nome_fantasia TEXT NOT NULL,
    endereco TEXT NOT NULL,
    telefone TEXT,
    responsavel_tecnico TEXT,
    latitude REAL,
    longitude REAL,
    CHECK (latitude IS NULL OR (latitude >= -90 AND latitude <= 90)),
    CHECK (longitude IS NULL OR (longitude >= -180 AND longitude <= 180)),
    CHECK ((latitude IS NULL AND longitude IS NULL) OR (latitude IS NOT NULL AND longitude IS NOT NULL))
);

-- Tabela: Medicamento
CREATE TABLE Medicamento (
    id_medicamento INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    principio_ativo TEXT NOT NULL,
    fabricante TEXT NOT NULL,
    codigo_barras TEXT UNIQUE,
    prescricao_obrigatoria INTEGER DEFAULT 0 CHECK (prescricao_obrigatoria IN (0,1))
);

-- Tabela: Receita (atualizada com novos campos)
CREATE TABLE Receita (
    id_receita INTEGER PRIMARY KEY AUTOINCREMENT,
    id_paciente INTEGER NOT NULL,
    id_medico INTEGER NOT NULL,
    data_emissao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_validade DATE,
    diagnostico TEXT NOT NULL,
    observacoes TEXT,
    status TEXT DEFAULT 'ativa' CHECK (status IN ('ativa', 'utilizada', 'cancelada', 'expirada')),
    FOREIGN KEY (id_paciente) REFERENCES Paciente(id_paciente),
    FOREIGN KEY (id_medico) REFERENCES Medico(id_medico)
);

-- Tabela: ReceitaMedicamento (nova tabela para relacionamento N:N)
CREATE TABLE ReceitaMedicamento (
    id_receita_medicamento INTEGER PRIMARY KEY AUTOINCREMENT,
    id_receita INTEGER NOT NULL,
    id_medicamento INTEGER NOT NULL,
    dosagem TEXT NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    posologia TEXT NOT NULL,
    observacoes TEXT,
    FOREIGN KEY (id_receita) REFERENCES Receita(id_receita) ON DELETE CASCADE,
    FOREIGN KEY (id_medicamento) REFERENCES Medicamento(id_medicamento),
    UNIQUE(id_receita, id_medicamento)
);

-- Tabela: Venda
CREATE TABLE Venda (
    id_venda INTEGER PRIMARY KEY AUTOINCREMENT,
    id_farmacia INTEGER NOT NULL,
    id_paciente INTEGER,
    id_receita INTEGER,
    data_venda DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valor_total REAL DEFAULT 0,
    FOREIGN KEY (id_farmacia) REFERENCES Farmacia(id_farmacia),
    FOREIGN KEY (id_paciente) REFERENCES Paciente(id_paciente),
    FOREIGN KEY (id_receita) REFERENCES Receita(id_receita)
);

-- Tabela: EstoqueFarmacia
CREATE TABLE EstoqueFarmacia (
    id_farmacia INTEGER NOT NULL,
    id_medicamento INTEGER NOT NULL,
    preco_unitario REAL NOT NULL CHECK (preco_unitario >= 0),
    quantidade_disponivel INTEGER NOT NULL DEFAULT 0 CHECK (quantidade_disponivel >= 0),
    estoque_minimo INTEGER DEFAULT 5,
    data_ultima_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_farmacia, id_medicamento),
    FOREIGN KEY (id_farmacia) REFERENCES Farmacia(id_farmacia) ON DELETE CASCADE,
    FOREIGN KEY (id_medicamento) REFERENCES Medicamento(id_medicamento)
);

-- Tabela: Notificacao
CREATE TABLE Notificacao (
    id_notificacao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    mensagem TEXT NOT NULL,
    data_envio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    foi_lida INTEGER DEFAULT 0 CHECK (foi_lida IN (0,1)),
    tipo TEXT DEFAULT 'info' CHECK (tipo IN ('info', 'alerta', 'erro')),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);

-- Índices para melhorar performance
CREATE INDEX idx_receita_paciente ON Receita(id_paciente);
CREATE INDEX idx_receita_medico ON Receita(id_medico);
CREATE INDEX idx_receita_status ON Receita(status);
CREATE INDEX idx_receita_data_validade ON Receita(data_validade);
CREATE INDEX idx_receita_medicamento_receita ON ReceitaMedicamento(id_receita);
CREATE INDEX idx_receita_medicamento_medicamento ON ReceitaMedicamento(id_medicamento);
CREATE INDEX idx_venda_farmacia ON Venda(id_farmacia);
CREATE INDEX idx_venda_data ON Venda(data_venda);
CREATE INDEX idx_notificacao_usuario ON Notificacao(id_usuario);
CREATE INDEX idx_notificacao_lida ON Notificacao(foi_lida);
CREATE INDEX idx_farmacia_coordenadas ON Farmacia(latitude, longitude);

-- Triggers para manter integridade dos dados

-- Trigger para atualizar data de última atualização do estoque
CREATE TRIGGER update_estoque_timestamp 
    AFTER UPDATE ON EstoqueFarmacia
BEGIN
    UPDATE EstoqueFarmacia 
    SET data_ultima_atualizacao = CURRENT_TIMESTAMP 
    WHERE id_farmacia = NEW.id_farmacia AND id_medicamento = NEW.id_medicamento;
END;

-- Trigger para verificar validade da receita antes de criar venda
CREATE TRIGGER check_receita_validade_before_venda
    BEFORE INSERT ON Venda
    WHEN NEW.id_receita IS NOT NULL
BEGIN
    SELECT CASE
        WHEN (SELECT data_validade FROM Receita WHERE id_receita = NEW.id_receita) < DATE('now')
        THEN RAISE(FAIL, 'Receita expirada')
        WHEN (SELECT status FROM Receita WHERE id_receita = NEW.id_receita) != 'ativa'
        THEN RAISE(FAIL, 'Receita não está ativa')
    END;
END;

-- Trigger para marcar receita como utilizada após venda
CREATE TRIGGER mark_receita_utilizada_after_venda
    AFTER INSERT ON Venda
    WHEN NEW.id_receita IS NOT NULL
BEGIN
    UPDATE Receita 
    SET status = 'utilizada' 
    WHERE id_receita = NEW.id_receita AND status = 'ativa';
END;

-- Trigger para atualizar status de receitas expiradas
CREATE TRIGGER update_receita_expirada
    AFTER UPDATE ON Receita
    WHEN NEW.data_validade < DATE('now') AND NEW.status = 'ativa'
BEGIN
    UPDATE Receita 
    SET status = 'expirada' 
    WHERE id_receita = NEW.id_receita;
END;

-- Views úteis para consultas frequentes

-- View: Receitas com detalhes do médico e paciente
CREATE VIEW view_receitas_completas AS
SELECT 
    r.id_receita,
    r.data_emissao,
    r.data_validade,
    r.diagnostico,
    r.observacoes,
    r.status,
    up.nome as nome_paciente,
    up.email as email_paciente,
    p.cpf as cpf_paciente,
    um.nome as nome_medico,
    m.crm,
    m.especialidade,
    COUNT(rm.id_medicamento) as total_medicamentos
FROM Receita r
JOIN Paciente p ON r.id_paciente = p.id_paciente
JOIN Usuario up ON p.id_paciente = up.id_usuario
JOIN Medico m ON r.id_medico = m.id_medico
JOIN Usuario um ON m.id_medico = um.id_usuario
LEFT JOIN ReceitaMedicamento rm ON r.id_receita = rm.id_receita
GROUP BY r.id_receita;

-- View: Estoque baixo por farmácia
CREATE VIEW view_estoque_baixo AS
SELECT 
    f.nome_fantasia as farmacia,
    f.endereco,
    m.nome as medicamento,
    m.principio_ativo,
    e.quantidade_disponivel,
    e.estoque_minimo,
    e.preco_unitario
FROM EstoqueFarmacia e
JOIN Farmacia f ON e.id_farmacia = f.id_farmacia
JOIN Medicamento m ON e.id_medicamento = m.id_medicamento
WHERE e.quantidade_disponivel <= e.estoque_minimo;

-- View: Receitas próximas do vencimento (7 dias)
CREATE VIEW view_receitas_vencimento_proximo AS
SELECT 
    r.id_receita,
    r.data_validade,
    up.nome as nome_paciente,
    up.email as email_paciente,
    um.nome as nome_medico,
    r.diagnostico,
    julianday(r.data_validade) - julianday('now') as dias_para_vencer
FROM Receita r
JOIN Paciente p ON r.id_paciente = p.id_paciente
JOIN Usuario up ON p.id_paciente = up.id_usuario
JOIN Medico m ON r.id_medico = m.id_medico
JOIN Usuario um ON m.id_medico = um.id_usuario
WHERE r.status = 'ativa' 
  AND julianday(r.data_validade) - julianday('now') BETWEEN 0 AND 7;

-- Dados de exemplo para teste (opcional)
-- Descomente para inserir dados de exemplo

/*
-- Usuários de exemplo
INSERT INTO Usuario (nome, email, senha, tipo) VALUES 
('Dr. João Silva', 'joao.medico@email.com', 'senha_hash', 'medico'),
('Maria Santos', 'maria.paciente@email.com', 'senha_hash', 'paciente'),
('Admin Sistema', 'admin@sistema.com', 'senha_hash', 'admin');

-- Médico
INSERT INTO Medico (id_medico, crm, especialidade) VALUES 
(1, 'CRM12345', 'Cardiologia');

-- Paciente
INSERT INTO Paciente (id_paciente, cpf, telefone, endereco) VALUES 
(2, '12345678901', '11999999999', 'Rua das Flores, 123');

-- Farmácia
INSERT INTO Farmacia (cnpj, nome_fantasia, endereco, telefone, latitude, longitude) VALUES 
('12.345.678/0001-90', 'Farmácia Central', 'Av. Principal, 456', '1133334444', -23.5505, -46.6333);

-- Medicamentos
INSERT INTO Medicamento (nome, principio_ativo, fabricante, prescricao_obrigatoria) VALUES 
('Dipirona 500mg', 'Dipirona Sódica', 'Farmacêutica ABC', 0),
('Amoxicilina 500mg', 'Amoxicilina', 'Laboratório XYZ', 1);
*/