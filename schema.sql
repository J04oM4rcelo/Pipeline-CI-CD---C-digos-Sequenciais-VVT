-- ================================================================
--  SCRIPT SQL — Sistema de Códigos Sequenciais
--  Disciplina: Verificação, Validação e Testes (VV&T)
--
--  Padrão do código: PAIS + GRUPO + SEQUENCIA_4_DIGITOS + TIPO_ALIMENTO
--  Exemplo: BRC0004A
-- ================================================================

-- Criar banco de dados
CREATE DATABASE IF NOT EXISTS produtos_db
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE produtos_db;

-- Criar tabela codigos_sequenciais
CREATE TABLE IF NOT EXISTS codigos_sequenciais (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    codigo          VARCHAR(10)   NOT NULL UNIQUE,
    sec             INT           NOT NULL,
    Grupo           CHAR(1)       NOT NULL,
    Tipo_Alimento   CHAR(1)       NOT NULL,
    Pais            CHAR(2)       NOT NULL,

    -- Índices para otimização de consultas
    INDEX idx_grupo (Grupo),
    INDEX idx_pais  (Pais),
    INDEX idx_codigo (codigo)

) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;

-- ================================================================
--  DADOS DE REFERÊNCIA (conforme especificação)
-- ================================================================

INSERT INTO codigos_sequenciais (codigo, sec, Grupo, Tipo_Alimento, Pais) VALUES
    ('BRC0001A', 1, 'C', 'A', 'BR'),
    ('BRD0001I', 1, 'D', 'I', 'BR'),
    ('BRA0001K', 1, 'A', 'K', 'BR'),
    ('BRF0001F', 1, 'F', 'F', 'BR'),
    ('BRG0001A', 1, 'G', 'A', 'BR'),
    ('BRC0002A', 2, 'C', 'A', 'BR'),
    ('BRD0002K', 2, 'D', 'K', 'BR'),
    ('BRF0002A', 2, 'F', 'A', 'BR'),
    ('BRC0003C', 3, 'C', 'C', 'BR');

-- Verificação
SELECT '✅ Banco e tabela criados com sucesso!' AS status;
SELECT COUNT(*) AS registros_inseridos FROM codigos_sequenciais;