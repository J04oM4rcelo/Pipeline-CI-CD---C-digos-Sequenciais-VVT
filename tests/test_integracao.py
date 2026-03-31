"""
Testes de INTEGRAÇÃO — Conectam ao MySQL real.

Estes testes são executados automaticamente na pipeline CI/CD.
Em ambiente local, são pulados se o MySQL não estiver disponível.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import ProdutoModel
from database import Database


# ================================================================
#  TESTE DE CONEXÃO COM MYSQL
# ================================================================

class TestConexaoMySQL:
    """Valida a conexão Python ↔ MySQL."""

    def test_conexao_estabelecida(self, db_real):
        """Deve conectar ao MySQL com sucesso."""
        assert db_real.connection is not None
        assert db_real.connection.is_connected()

    def test_banco_de_dados_correto(self, db_real):
        """Deve estar conectado ao banco produtos_db."""
        resultado = db_real.executar_consulta("SELECT DATABASE() AS db")
        assert resultado[0]['db'] == 'produtos_db'

    def test_tabela_existe(self, db_real):
        """A tabela codigos_sequenciais deve existir."""
        resultado = db_real.executar_consulta(
            "SHOW TABLES LIKE 'codigos_sequenciais'"
        )
        assert len(resultado) > 0

    def test_estrutura_tabela(self, db_real):
        """A tabela deve ter as colunas corretas."""
        resultado = db_real.executar_consulta(
            "DESCRIBE codigos_sequenciais"
        )
        colunas = [row['Field'] for row in resultado]
        assert 'id' in colunas
        assert 'codigo' in colunas
        assert 'sec' in colunas
        assert 'Grupo' in colunas
        assert 'Tipo_Alimento' in colunas
        assert 'Pais' in colunas


# ================================================================
#  TESTE DE INSERÇÃO E GERAÇÃO DE CÓDIGO
# ================================================================

class TestInsercaoIntegracao:
    """Testa inserção real no banco de dados."""

    def test_inserir_primeiro_registro(self, model_real):
        """Deve inserir o primeiro registro com sec=1."""
        id_novo, codigo, sec = model_real.inserir("BR", "C", "A")

        assert id_novo is not None
        assert codigo == "BRC0001A"
        assert sec == 1

    def test_inserir_segundo_registro_mesmo_grupo(self, model_real):
        """sec deve incrementar para o mesmo grupo."""
        model_real.inserir("BR", "C", "A")
        id_novo, codigo, sec = model_real.inserir("BR", "C", "B")

        assert sec == 2
        assert codigo == "BRC0002B"

    def test_inserir_terceiro_registro_mesmo_grupo(self, model_real):
        """sec deve continuar incrementando."""
        model_real.inserir("BR", "C", "A")
        model_real.inserir("BR", "C", "A")
        id_novo, codigo, sec = model_real.inserir("BR", "C", "C")

        assert sec == 3
        assert codigo == "BRC0003C"

    def test_grupos_independentes_real(self, model_real):
        """Grupos diferentes devem ter sequências independentes."""
        _, cod_c, sec_c = model_real.inserir("BR", "C", "A")
        _, cod_d, sec_d = model_real.inserir("BR", "D", "I")
        _, cod_a, sec_a = model_real.inserir("BR", "A", "K")
        _, cod_c2, sec_c2 = model_real.inserir("BR", "C", "A")

        assert sec_c == 1 and cod_c == "BRC0001A"
        assert sec_d == 1 and cod_d == "BRD0001I"
        assert sec_a == 1 and cod_a == "BRA0001K"
        assert sec_c2 == 2 and cod_c2 == "BRC0002A"

    def test_dados_referencia_completo(self, model_real):
        """
        Reproduz a tabela de referência da especificação.
        Insere na mesma ordem e verifica os códigos.
        """
        entradas = [
            ("BR", "C", "A"),  # BRC0001A sec=1
            ("BR", "D", "I"),  # BRD0001I sec=1
            ("BR", "A", "K"),  # BRA0001K sec=1
            ("BR", "F", "F"),  # BRF0001F sec=1
            ("BR", "G", "A"),  # BRG0001A sec=1
            ("BR", "C", "A"),  # BRC0002A sec=2
            ("BR", "D", "K"),  # BRD0002K sec=2
            ("BR", "F", "A"),  # BRF0002A sec=2
            ("BR", "C", "C"),  # BRC0003C sec=3
        ]

        esperados = [
            ("BRC0001A", 1),
            ("BRD0001I", 1),
            ("BRA0001K", 1),
            ("BRF0001F", 1),
            ("BRG0001A", 1),
            ("BRC0002A", 2),
            ("BRD0002K", 2),
            ("BRF0002A", 2),
            ("BRC0003C", 3),
        ]

        for i, (pais, grupo, tipo) in enumerate(entradas):
            _, codigo, sec = model_real.inserir(pais, grupo, tipo)
            cod_esperado, sec_esperado = esperados[i]
            assert codigo == cod_esperado, f"Registro {i+1}: esperado {cod_esperado}, obteve {codigo}"
            assert sec == sec_esperado, f"Registro {i+1}: sec esperado {sec_esperado}, obteve {sec}"


# ================================================================
#  TESTE DE CONSULTAS
# ================================================================

class TestConsultasIntegracao:
    """Testa consultas reais no banco de dados."""

    def test_buscar_por_codigo(self, model_real):
        """Deve encontrar produto pelo código."""
        model_real.inserir("BR", "C", "A")

        resultado = model_real.buscar_por_codigo("BRC0001A")

        assert resultado is not None
        assert resultado['codigo'] == "BRC0001A"
        assert resultado['Pais'] == "BR"
        assert resultado['Grupo'] == "C"
        assert resultado['Tipo_Alimento'] == "A"
        assert resultado['sec'] == 1

    def test_buscar_codigo_inexistente(self, model_real):
        """Código inexistente deve retornar None."""
        resultado = model_real.buscar_por_codigo("ZZZ9999Z")
        assert resultado is None

    def test_buscar_todos(self, model_real):
        """Deve retornar todos os registros inseridos."""
        model_real.inserir("BR", "C", "A")
        model_real.inserir("BR", "D", "I")
        model_real.inserir("US", "A", "A")

        todos = model_real.buscar_todos()

        assert len(todos) == 3

    def test_buscar_por_grupo(self, model_real):
        """Deve filtrar por grupo."""
        model_real.inserir("BR", "C", "A")
        model_real.inserir("BR", "D", "I")
        model_real.inserir("BR", "C", "B")

        grupo_c = model_real.buscar_por_grupo("C")

        assert len(grupo_c) == 2
        assert all(r['Grupo'] == 'C' for r in grupo_c)

    def test_buscar_por_pais(self, model_real):
        """Deve filtrar por país."""
        model_real.inserir("BR", "C", "A")
        model_real.inserir("US", "C", "A")
        model_real.inserir("BR", "D", "I")

        brasil = model_real.buscar_por_pais("BR")

        assert len(brasil) == 2
        assert all(r['Pais'] == 'BR' for r in brasil)

    def test_contar_produtos(self, model_real):
        """Deve contar corretamente."""
        assert model_real.contar_produtos() == 0

        model_real.inserir("BR", "C", "A")
        model_real.inserir("BR", "D", "I")

        assert model_real.contar_produtos() == 2


# ================================================================
#  TESTE DE PREVENÇÃO DE DUPLICIDADE
# ================================================================

class TestDuplicidadeIntegracao:
    """Valida que códigos são únicos."""

    def test_codigos_unicos_mesmo_grupo(self, model_real):
        """Inserções no mesmo grupo geram códigos diferentes."""
        _, cod1, _ = model_real.inserir("BR", "C", "A")
        _, cod2, _ = model_real.inserir("BR", "C", "A")
        _, cod3, _ = model_real.inserir("BR", "C", "A")

        assert cod1 != cod2
        assert cod2 != cod3
        assert cod1 != cod3

    def test_sem_duplicidade_na_tabela(self, model_real):
        """A tabela não deve ter códigos duplicados."""
        for _ in range(5):
            model_real.inserir("BR", "C", "A")

        todos = model_real.buscar_por_grupo("C")
        codigos = [r['codigo'] for r in todos]

        assert len(codigos) == len(set(codigos)), "Códigos duplicados encontrados!"


# ================================================================
#  TESTE DO ZEROFILL COM BANCO REAL
# ================================================================

class TestZerofillIntegracao:
    """Valida o zerofill com inserções reais."""

    def test_zerofill_primeiros_registros(self, model_real):
        """Primeiros registros devem ter 0001, 0002, etc."""
        _, cod1, _ = model_real.inserir("BR", "C", "A")
        _, cod2, _ = model_real.inserir("BR", "C", "A")

        # Extrair parte numérica (posições 3 a 6)
        assert cod1[3:7] == "0001"
        assert cod2[3:7] == "0002"

    def test_codigo_sempre_8_caracteres(self, model_real):
        """Todos os códigos devem ter 8 caracteres."""
        for _ in range(5):
            _, codigo, _ = model_real.inserir("BR", "C", "A")
            assert len(codigo) == 8, f"Código {codigo} não tem 8 caracteres"