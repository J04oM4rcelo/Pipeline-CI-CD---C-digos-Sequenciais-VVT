import sys
import os
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ================================================================
#  TESTES DA FUNÇÃO gerar_codigo
#  (Passos 4 e 5: formatação zerofill + composição do código)
# ================================================================

class TestGerarCodigo:
    """Testa composição: PAÍS + GRUPO + SEQ(zerofill) + TIPO."""

    # ── PASSO 5: COMPOSIÇÃO BÁSICA ──────────────────────

    def test_codigo_padrao_BRC0004A(self, produto_model, mock_db, grupo_com_max_3):
        """Testa o exemplo da especificação: BRC0004A."""
        mock_db.executar_consulta.return_value = grupo_com_max_3
        codigo, sec = produto_model.gerar_codigo("BR", "C", "A")
        assert codigo == "BRC0004A"

    def test_codigo_pais_US(self, produto_model, mock_db, grupo_vazio):
        """Testa código com país US."""
        mock_db.executar_consulta.return_value = grupo_vazio
        codigo, sec = produto_model.gerar_codigo("US", "A", "A")
        assert codigo == "USA0001A"

    def test_codigo_pais_AR(self, produto_model, mock_db, grupo_vazio):
        """Testa código com país AR."""
        mock_db.executar_consulta.return_value = grupo_vazio
        codigo, sec = produto_model.gerar_codigo("AR", "B", "B")
        assert codigo == "ARB0001B"

    # ── PASSO 4: ZEROFILL COM 4 DÍGITOS ─────────────────

    def test_zerofill_seq_1(self, produto_model, mock_db, grupo_vazio):
        """sec=1 deve virar '0001'."""
        mock_db.executar_consulta.return_value = grupo_vazio
        codigo, sec = produto_model.gerar_codigo("BR", "C", "A")
        assert sec == 1
        assert codigo == "BRC0001A"

    def test_zerofill_seq_15(self, produto_model, mock_db, seq_retorna_15):
        """sec=15 deve virar '0015'."""
        mock_db.executar_consulta.return_value = seq_retorna_15
        codigo, sec = produto_model.gerar_codigo("BR", "C", "A")
        assert sec == 15
        assert codigo == "BRC0015A"

    def test_zerofill_seq_100(self, produto_model, mock_db, seq_retorna_100):
        """sec=100 deve virar '0100'."""
        mock_db.executar_consulta.return_value = seq_retorna_100
        codigo, sec = produto_model.gerar_codigo("BR", "A", "B")
        assert sec == 100
        assert codigo == "BRA0100B"

    def test_zerofill_seq_1000(self, produto_model, mock_db, seq_retorna_1000):
        """sec=1000 deve virar '1000' (sem zeros à esquerda)."""
        mock_db.executar_consulta.return_value = seq_retorna_1000
        codigo, sec = produto_model.gerar_codigo("US", "C", "A")
        assert sec == 1000
        assert codigo == "USC1000A"

    def test_zerofill_seq_9999(self, produto_model, mock_db, seq_retorna_9999):
        """sec=9999 — limite máximo de 4 dígitos."""
        mock_db.executar_consulta.return_value = seq_retorna_9999
        codigo, sec = produto_model.gerar_codigo("BR", "C", "A")
        assert sec == 9999
        assert codigo == "BRC9999A"

    # ── TAMANHO DO CÓDIGO ────────────────────────────────

    def test_codigo_tem_8_caracteres(self, produto_model, mock_db, grupo_com_max_3):
        """O código deve ter exatamente 8 caracteres."""
        mock_db.executar_consulta.return_value = grupo_com_max_3
        codigo, sec = produto_model.gerar_codigo("BR", "C", "A")
        assert len(codigo) == 8

    def test_codigo_tem_8_caracteres_seq_1(self, produto_model, mock_db, grupo_vazio):
        """Mesmo com sec=1, código deve ter 8 caracteres."""
        mock_db.executar_consulta.return_value = grupo_vazio
        codigo, sec = produto_model.gerar_codigo("AR", "A", "B")
        assert len(codigo) == 8

    # ── CONVERSÃO PARA MAIÚSCULO ────────────────────────

    def test_entrada_minuscula_convertida(self, produto_model, mock_db, grupo_com_max_3):
        """Entradas em minúsculo devem virar maiúsculo."""
        mock_db.executar_consulta.return_value = grupo_com_max_3
        codigo, sec = produto_model.gerar_codigo("br", "c", "a")
        assert codigo == "BRC0004A"

    def test_entrada_mista_convertida(self, produto_model, mock_db, grupo_com_max_10):
        """Entradas mistas devem virar maiúsculo."""
        mock_db.executar_consulta.return_value = grupo_com_max_10
        codigo, sec = produto_model.gerar_codigo("Br", "c", "a")
        assert codigo == "BRC0011A"

    # ── ESTRUTURA DO CÓDIGO ──────────────────────────────

    def test_dois_primeiros_caracteres_sao_pais(self, produto_model, mock_db, grupo_com_max_3):
        """Os 2 primeiros caracteres representam o país."""
        mock_db.executar_consulta.return_value = grupo_com_max_3
        codigo, sec = produto_model.gerar_codigo("BR", "C", "A")
        assert codigo[:2] == "BR"

    def test_terceiro_caractere_e_grupo(self, produto_model, mock_db, grupo_com_max_3):
        """O 3º caractere representa o grupo."""
        mock_db.executar_consulta.return_value = grupo_com_max_3
        codigo, sec = produto_model.gerar_codigo("BR", "C", "A")
        assert codigo[2] == "C"

    def test_caracteres_4_a_7_sao_sequencia(self, produto_model, mock_db, grupo_com_max_3):
        """Os caracteres 4 a 7 representam a sequência."""
        mock_db.executar_consulta.return_value = grupo_com_max_3
        codigo, sec = produto_model.gerar_codigo("BR", "C", "A")
        assert codigo[3:7] == "0004"

    def test_ultimo_caractere_e_tipo(self, produto_model, mock_db, grupo_com_max_3):
        """O último caractere representa o tipo de alimento."""
        mock_db.executar_consulta.return_value = grupo_com_max_3
        codigo, sec = produto_model.gerar_codigo("BR", "C", "A")
        assert codigo[7] == "A"


# ================================================================
#  TESTES DA FUNÇÃO _obter_proxima_sequencia
#  (Passos 1, 2 e 3)
# ================================================================

class TestObterProximaSequencia:
    """Testa o cálculo da próxima sequência por grupo."""

    # ── PASSO 1: CONSULTA FILTRA POR GRUPO ───────────────

    def test_consulta_filtra_por_grupo(self, produto_model, mock_db, grupo_vazio):
        """A query deve conter WHERE Grupo = %s."""
        mock_db.executar_consulta.return_value = grupo_vazio

        produto_model._obter_proxima_sequencia("C")

        mock_db.executar_consulta.assert_called_once()
        args = mock_db.executar_consulta.call_args
        query = args[0][0]
        params = args[0][1]
        query_limpa = " ".join(query.split())
        assert "WHERE Grupo = %s" in query_limpa
        assert params == ("C",)

    # ── PASSO 2: GRUPO SEM REGISTROS → 1 ────────────────

    def test_grupo_vazio_retorna_1(self, produto_model, mock_db, grupo_vazio):
        """Grupo sem registros deve retornar 1."""
        mock_db.executar_consulta.return_value = grupo_vazio
        resultado = produto_model._obter_proxima_sequencia("D")
        assert resultado == 1

    def test_grupo_novo_retorna_1(self, produto_model, mock_db, grupo_vazio):
        """Grupo completamente novo retorna 1."""
        mock_db.executar_consulta.return_value = grupo_vazio
        resultado = produto_model._obter_proxima_sequencia("Z")
        assert resultado == 1

    # ── PASSO 3: GRUPO COM REGISTROS → MAX + 1 ──────────

    def test_grupo_com_max_3_retorna_4(self, produto_model, mock_db, grupo_com_max_3):
        """MAX(sec)=3 → próximo = 4."""
        mock_db.executar_consulta.return_value = grupo_com_max_3
        resultado = produto_model._obter_proxima_sequencia("C")
        assert resultado == 4

    def test_grupo_com_max_10_retorna_11(self, produto_model, mock_db, grupo_com_max_10):
        """MAX(sec)=10 → próximo = 11."""
        mock_db.executar_consulta.return_value = grupo_com_max_10
        resultado = produto_model._obter_proxima_sequencia("C")
        assert resultado == 11

    def test_grupo_com_max_1_retorna_2(self, produto_model, mock_db, grupo_com_max_1):
        """MAX(sec)=1 → próximo = 2."""
        mock_db.executar_consulta.return_value = grupo_com_max_1
        resultado = produto_model._obter_proxima_sequencia("A")
        assert resultado == 2

    def test_grupo_com_max_9999_retorna_10000(self, produto_model, mock_db, grupo_com_max_9999):
        """MAX(sec)=9999 → próximo = 10000."""
        mock_db.executar_consulta.return_value = grupo_com_max_9999
        resultado = produto_model._obter_proxima_sequencia("C")
        assert resultado == 10000


# ================================================================
#  TESTES DO PASSO 6 — gerar_codigo retorna (codigo, sec)
# ================================================================

class TestGerarCodigoRetorno:
    """Testa se gerar_codigo retorna a tupla correta."""

    def test_retorna_tupla(self, produto_model, mock_db, grupo_vazio):
        """Deve retornar uma tupla."""
        mock_db.executar_consulta.return_value = grupo_vazio
        resultado = produto_model.gerar_codigo("BR", "C", "A")
        assert isinstance(resultado, tuple)
        assert len(resultado) == 2

    def test_primeiro_elemento_e_string(self, produto_model, mock_db, grupo_vazio):
        """Primeiro elemento é o código (string)."""
        mock_db.executar_consulta.return_value = grupo_vazio
        codigo, sec = produto_model.gerar_codigo("BR", "C", "A")
        assert isinstance(codigo, str)

    def test_segundo_elemento_e_inteiro(self, produto_model, mock_db, grupo_vazio):
        """Segundo elemento é o sec (inteiro)."""
        mock_db.executar_consulta.return_value = grupo_vazio
        codigo, sec = produto_model.gerar_codigo("BR", "C", "A")
        assert isinstance(sec, int)

    def test_grupo_vazio_retorna_seq_1(self, produto_model, mock_db, grupo_vazio):
        """Grupo vazio: sec=1, código=BRC0001A."""
        mock_db.executar_consulta.return_value = grupo_vazio
        codigo, sec = produto_model.gerar_codigo("BR", "C", "A")
        assert sec == 1
        assert codigo == "BRC0001A"

    def test_grupo_novo_D_retorna_seq_1(self, produto_model, mock_db, grupo_vazio):
        """Grupo D novo: sec=1, código=BRD0001A."""
        mock_db.executar_consulta.return_value = grupo_vazio
        codigo, sec = produto_model.gerar_codigo("BR", "D", "A")
        assert sec == 1
        assert codigo == "BRD0001A"

    def test_grupo_com_max_3_retorna_seq_4(self, produto_model, mock_db, grupo_com_max_3):
        """MAX=3 → sec=4, código=BRC0004A."""
        mock_db.executar_consulta.return_value = grupo_com_max_3
        codigo, sec = produto_model.gerar_codigo("BR", "C", "A")
        assert sec == 4
        assert codigo == "BRC0004A"

    def test_grupo_com_max_10_retorna_seq_11(self, produto_model, mock_db, grupo_com_max_10):
        """MAX=10 → sec=11, código=BRC0011A."""
        mock_db.executar_consulta.return_value = grupo_com_max_10
        codigo, sec = produto_model.gerar_codigo("BR", "C", "A")
        assert sec == 11
        assert codigo == "BRC0011A"

    def test_pais_US(self, produto_model, mock_db, grupo_vazio):
        """Código com país US."""
        mock_db.executar_consulta.return_value = grupo_vazio
        codigo, sec = produto_model.gerar_codigo("US", "A", "A")
        assert codigo.startswith("US")
        assert codigo == "USA0001A"

    def test_pais_AR(self, produto_model, mock_db, grupo_vazio):
        """Código com país AR."""
        mock_db.executar_consulta.return_value = grupo_vazio
        codigo, sec = produto_model.gerar_codigo("AR", "B", "B")
        assert codigo.startswith("AR")
        assert codigo == "ARB0001B"

    def test_tipo_alimento_A(self, produto_model, mock_db, grupo_vazio):
        """Último caractere = A."""
        mock_db.executar_consulta.return_value = grupo_vazio
        codigo, _ = produto_model.gerar_codigo("BR", "C", "A")
        assert codigo[-1] == "A"

    def test_tipo_alimento_B(self, produto_model, mock_db, grupo_vazio):
        """Último caractere = B."""
        mock_db.executar_consulta.return_value = grupo_vazio
        codigo, _ = produto_model.gerar_codigo("BR", "C", "B")
        assert codigo[-1] == "B"

    def test_entrada_minuscula(self, produto_model, mock_db, grupo_vazio):
        """Minúsculo vira maiúsculo."""
        mock_db.executar_consulta.return_value = grupo_vazio
        codigo, _ = produto_model.gerar_codigo("br", "c", "a")
        assert codigo == "BRC0001A"
        assert codigo == codigo.upper()


# ================================================================
#  TESTES DO MÉTODO inserir
# ================================================================

class TestInserir:
    """Testa o método inserir com banco mockado."""

    def test_inserir_chama_executar_query(self, produto_model, mock_db, grupo_com_max_3):
        """Ao inserir, deve executar INSERT."""
        mock_db.executar_consulta.return_value = grupo_com_max_3
        mock_db.executar_query.return_value = 1

        produto_model.inserir("BR", "C", "A")

        mock_db.executar_query.assert_called_once()
        query_chamada = mock_db.executar_query.call_args[0][0]
        assert "INSERT INTO codigos_sequenciais" in query_chamada

    def test_inserir_passa_parametros_corretos(self, produto_model, mock_db, grupo_com_max_3):
        """Parâmetros do INSERT devem estar corretos."""
        mock_db.executar_consulta.return_value = grupo_com_max_3
        mock_db.executar_query.return_value = 1

        produto_model.inserir("BR", "C", "A")

        params = mock_db.executar_query.call_args[0][1]
        assert params == ("BRC0004A", 4, "C", "A", "BR")

    def test_inserir_retorna_id_e_codigo(self, produto_model, mock_db, grupo_com_max_3):
        """Inserir deve retornar o ID e o código."""
        mock_db.executar_consulta.return_value = grupo_com_max_3
        mock_db.executar_query.return_value = 5

        resultado = produto_model.inserir("BR", "C", "A")

        assert 5 in resultado
        assert "BRC0004A" in resultado

    def test_inserir_com_falha(self, produto_model, mock_db, grupo_vazio):
        """Se INSERT falhar, todos os valores retornados são None."""
        mock_db.executar_consulta.return_value = grupo_vazio
        mock_db.executar_query.return_value = None

        resultado = produto_model.inserir("BR", "C", "A")

        assert all(v is None for v in resultado)

    def test_inserir_gera_codigo_automaticamente(self, produto_model, mock_db, grupo_vazio):
        """O código deve ser gerado automaticamente ao inserir."""
        mock_db.executar_consulta.return_value = grupo_vazio
        mock_db.executar_query.return_value = 1

        resultado = produto_model.inserir("BR", "C", "A")

        assert "BRC0001A" in resultado


# ================================================================
#  TESTES DE SEQUÊNCIAS INDEPENDENTES POR GRUPO
# ================================================================

class TestSequenciasIndependentes:
    """Valida que cada grupo mantém sequência própria."""

    def test_dois_grupos_diferentes(self, produto_model, mock_db):
        """Grupo C(max=3)→4, Grupo A(vazio)→1."""
        mock_db.executar_consulta.side_effect = [
            [{'proxima_seq': 4}],
            [{'proxima_seq': 1}],
        ]

        seq_c = produto_model._obter_proxima_sequencia("C")
        seq_a = produto_model._obter_proxima_sequencia("A")

        assert seq_c == 4
        assert seq_a == 1

    def test_tres_grupos_independentes(self, produto_model, mock_db):
        """Três grupos com sequências diferentes."""
        mock_db.executar_consulta.side_effect = [
            [{'proxima_seq': 11}],
            [{'proxima_seq': 6}],
            [{'proxima_seq': 1}],
        ]

        seq_a = produto_model._obter_proxima_sequencia("A")
        seq_b = produto_model._obter_proxima_sequencia("B")
        seq_c = produto_model._obter_proxima_sequencia("C")

        assert seq_a == 11
        assert seq_b == 6
        assert seq_c == 1

    def test_codigos_refletem_sequencias_independentes(self, produto_model, mock_db):
        """Códigos de grupos diferentes têm sequências próprias."""
        mock_db.executar_consulta.side_effect = [
            [{'proxima_seq': 4}],
            [{'proxima_seq': 1}],
        ]

        codigo_c, sec_c = produto_model.gerar_codigo("BR", "C", "A")
        codigo_a, sec_a = produto_model.gerar_codigo("BR", "A", "A")

        assert codigo_c == "BRC0004A"
        assert codigo_a == "BRA0001A"


# ================================================================
#  TESTES DE ENTRADAS INVÁLIDAS
#  (Critério exigido na especificação)
# ================================================================

class TestEntradasInvalidas:
    """
    Valida que gerar_codigo levanta ValueError
    para entradas inválidas.
    """

    # ── VALORES VAZIOS ───────────────────────────────────

    def test_pais_vazio(self, produto_model):
        """País vazio deve lançar ValueError."""
        with pytest.raises(ValueError, match="País"):
            produto_model.gerar_codigo("", "C", "A")

    def test_grupo_vazio(self, produto_model):
        """Grupo vazio deve lançar ValueError."""
        with pytest.raises(ValueError, match="Grupo"):
            produto_model.gerar_codigo("BR", "", "A")

    def test_tipo_alimento_vazio(self, produto_model):
        """Tipo Alimento vazio deve lançar ValueError."""
        with pytest.raises(ValueError, match="Tipo Alimento"):
            produto_model.gerar_codigo("BR", "C", "")

    # ── VALORES NONE ─────────────────────────────────────

    def test_pais_none(self, produto_model):
        """País None deve lançar ValueError."""
        with pytest.raises(ValueError, match="País"):
            produto_model.gerar_codigo(None, "C", "A")

    def test_grupo_none(self, produto_model):
        """Grupo None deve lançar ValueError."""
        with pytest.raises(ValueError, match="Grupo"):
            produto_model.gerar_codigo("BR", None, "A")

    def test_tipo_alimento_none(self, produto_model):
        """Tipo Alimento None deve lançar ValueError."""
        with pytest.raises(ValueError, match="Tipo Alimento"):
            produto_model.gerar_codigo("BR", "C", None)

    # ── TAMANHO INCORRETO ────────────────────────────────

    def test_pais_uma_letra(self, produto_model):
        """País com 1 letra deve lançar ValueError."""
        with pytest.raises(ValueError, match="2 caracteres"):
            produto_model.gerar_codigo("B", "C", "A")

    def test_pais_tres_letras(self, produto_model):
        """País com 3 letras deve lançar ValueError."""
        with pytest.raises(ValueError, match="2 caracteres"):
            produto_model.gerar_codigo("BRA", "C", "A")

    def test_grupo_duas_letras(self, produto_model):
        """Grupo com 2 letras deve lançar ValueError."""
        with pytest.raises(ValueError, match="1 caractere"):
            produto_model.gerar_codigo("BR", "CC", "A")

    def test_tipo_duas_letras(self, produto_model):
        """Tipo com 2 letras deve lançar ValueError."""
        with pytest.raises(ValueError, match="1 caractere"):
            produto_model.gerar_codigo("BR", "C", "AA")

    # ── VALORES COM NÚMEROS ──────────────────────────────

    def test_pais_com_numero(self, produto_model):
        """País com número deve lançar ValueError."""
        with pytest.raises(ValueError, match="letras"):
            produto_model.gerar_codigo("B1", "C", "A")

    def test_grupo_com_numero(self, produto_model):
        """Grupo com número deve lançar ValueError."""
        with pytest.raises(ValueError, match="letras"):
            produto_model.gerar_codigo("BR", "1", "A")

    def test_tipo_com_numero(self, produto_model):
        """Tipo com número deve lançar ValueError."""
        with pytest.raises(ValueError, match="letras"):
            produto_model.gerar_codigo("BR", "C", "1")

    # ── SOMENTE ESPAÇOS ─────────────────────────────────

    def test_pais_somente_espacos(self, produto_model):
        """País com apenas espaços deve lançar ValueError."""
        with pytest.raises(ValueError, match="País"):
            produto_model.gerar_codigo("  ", "C", "A")

    def test_grupo_somente_espacos(self, produto_model):
        """Grupo com apenas espaços deve lançar ValueError."""
        with pytest.raises(ValueError, match="Grupo"):
            produto_model.gerar_codigo("BR", " ", "A")