# tests/conftest.py

import sys
import os
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import ProdutoModel
from database import Database


# ══════════════════════════════════════════════════════════════
#  FIXTURES PARA TESTES UNITÁRIOS (mock)
# ══════════════════════════════════════════════════════════════

@pytest.fixture
def mock_db():
    """Cria um objeto Database FALSO (mock)."""
    db = MagicMock()
    db.connection = MagicMock()
    db.cursor = MagicMock()
    return db


@pytest.fixture
def produto_model(mock_db):
    """Retorna ProdutoModel com banco mockado."""
    return ProdutoModel(mock_db)


# ══════════════════════════════════════════════════════════════
#  FIXTURES PARA TESTES DE INTEGRAÇÃO (MySQL real)
# ══════════════════════════════════════════════════════════════

@pytest.fixture
def db_real():
    """
    Fixture que fornece conexão REAL com MySQL.
    Limpa a tabela antes e depois de cada teste.
    Pula o teste se MySQL não estiver disponível.
    """
    db = Database()
    try:
        if not db.conectar():
            pytest.skip("MySQL não disponível")
    except Exception:
        pytest.skip("MySQL não disponível")

    # Limpar tabela antes do teste
    db.executar_query("DELETE FROM codigos_sequenciais")
    db.executar_query("ALTER TABLE codigos_sequenciais AUTO_INCREMENT = 1")

    yield db

    # Limpar tabela após o teste
    try:
        db.executar_query("DELETE FROM codigos_sequenciais")
        db.desconectar()
    except Exception:
        pass


@pytest.fixture
def model_real(db_real):
    """ProdutoModel com conexão REAL ao MySQL."""
    return ProdutoModel(db_real)


# ══════════════════════════════════════════════════════════════
#  FIXTURES DE DADOS SIMULADOS (para testes unitários)
#
#  ⚠️  A chave DEVE ser 'proxima_seq' porque é o alias
#      usado na query SQL do models.py:
#
#      SELECT COALESCE(MAX(sec), 0) + 1 AS proxima_seq
# ══════════════════════════════════════════════════════════════

@pytest.fixture
def grupo_vazio():
    """Grupo sem registros → COALESCE(NULL, 0) + 1 = 1."""
    return [{'proxima_seq': 1}]


@pytest.fixture
def grupo_com_max_3():
    """Grupo com MAX(sec)=3 → 3 + 1 = 4."""
    return [{'proxima_seq': 4}]


@pytest.fixture
def grupo_com_max_10():
    """Grupo com MAX(sec)=10 → 10 + 1 = 11."""
    return [{'proxima_seq': 11}]


@pytest.fixture
def grupo_com_max_1():
    """Grupo com MAX(sec)=1 → 1 + 1 = 2."""
    return [{'proxima_seq': 2}]


@pytest.fixture
def grupo_com_max_9999():
    """Limite máximo de 4 dígitos → 9999 + 1 = 10000."""
    return [{'proxima_seq': 10000}]


@pytest.fixture
def seq_retorna_15():
    """Para testar zerofill com sec=15."""
    return [{'proxima_seq': 15}]


@pytest.fixture
def seq_retorna_100():
    """Para testar zerofill com sec=100."""
    return [{'proxima_seq': 100}]


@pytest.fixture
def seq_retorna_1000():
    """Para testar zerofill com sec=1000."""
    return [{'proxima_seq': 1000}]


@pytest.fixture
def seq_retorna_9999():
    """Para testar zerofill com sec=9999."""
    return [{'proxima_seq': 9999}]