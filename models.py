from database import Database


class ProdutoModel:
    """
    Operações CRUD para a tabela 'codigos_sequenciais'.

    Padrão do código (VARCHAR 8):
        PAÍS (2) + GRUPO (1) + SEQUÊNCIA (4 zerofill) + TIPO_ALIMENTO (1)
        Exemplo: BRC0004A

    Regra da sequência (sec):
        - Calculada POR GRUPO
        - Se não há registros no grupo → sec = 1
        - Se há registros → sec = maior sec do grupo + 1
    """

    def __init__(self, db: Database):
        self.db = db

    # ================================================================
    #  VALIDAÇÃO DE ENTRADA
    # ================================================================

    def _validar_entrada(self, pais, grupo, tipo_alimento):
        """
        Valida os parâmetros de entrada.
        Lança ValueError se algum parâmetro for inválido.
        """
        # Verificar valores vazios ou None
        if not pais or not isinstance(pais, str) or len(pais.strip()) == 0:
            raise ValueError("País não pode ser vazio.")
        if not grupo or not isinstance(grupo, str) or len(grupo.strip()) == 0:
            raise ValueError("Grupo não pode ser vazio.")
        if not tipo_alimento or not isinstance(tipo_alimento, str) or len(tipo_alimento.strip()) == 0:
            raise ValueError("Tipo Alimento não pode ser vazio.")

        # Verificar tamanho
        if len(pais.strip()) != 2:
            raise ValueError("País deve ter exatamente 2 caracteres.")
        if len(grupo.strip()) != 1:
            raise ValueError("Grupo deve ter exatamente 1 caractere.")
        if len(tipo_alimento.strip()) != 1:
            raise ValueError("Tipo Alimento deve ter exatamente 1 caractere.")

        # Verificar se são letras
        if not pais.strip().isalpha():
            raise ValueError("País deve conter apenas letras.")
        if not grupo.strip().isalpha():
            raise ValueError("Grupo deve conter apenas letras.")
        if not tipo_alimento.strip().isalpha():
            raise ValueError("Tipo Alimento deve conter apenas letras.")

    # ================================================================
    #  PASSO 4: FORMATAR SEC COM ZEROFILL (4 dígitos)
    # ================================================================

    def _formatar_sequencia(self, sec):
        """
        Passo 4: Formata o sec para 4 dígitos com zeros à esquerda.

        Exemplos:
            1   → "0001"
            15  → "0015"
            999 → "0999"
        """
        return str(sec).zfill(4)

    # ================================================================
    #  PASSOS 1, 2 e 3: CALCULAR PRÓXIMA SEQUÊNCIA POR GRUPO
    # ================================================================

    def _obter_proxima_sequencia(self, grupo):
        """
        Passo 1: Consulta o MAIOR sec para o GRUPO informado.
        Passo 2: Se não houver registros para o grupo → retorna 1.
        Passo 3: Se houver registros → retorna maior sec + 1.

        Parâmetros:
            grupo (str): caractere do grupo (ex: 'C')

        Retorna:
            int: próximo valor de sec para aquele grupo
        """
        query = """
            SELECT COALESCE(MAX(sec), 0) + 1 AS proxima_seq
            FROM codigos_sequenciais
            WHERE Grupo = %s
        """
        resultado = self.db.executar_consulta(query, (grupo.upper(),))

        proxima_seq = resultado[0]['proxima_seq'] if resultado else 1

        print(f"   🔢 Grupo '{grupo.upper()}': próxima sequência = {proxima_seq}")

        return proxima_seq

    # ================================================================
    #  PASSOS 5 e 6: GERAR CÓDIGO E RETORNAR
    # ================================================================

    def gerar_codigo(self, pais, grupo, tipo_alimento):
        """
        Gera o código completo seguindo TODOS os 6 passos.

        Passo 0: Valida os parâmetros de entrada
        Passo 1: Consulta o maior sec do grupo
        Passo 2: Se não há registros → sec = 1
        Passo 3: Se há → sec = maior + 1
        Passo 4: Formata sec com zerofill (4 dígitos)
        Passo 5: Compõe PAIS + GRUPO + SEQ_4_DIGITOS + TIPO_ALIMENTO
        Passo 6: Retorna o código gerado e o sec calculado

        Parâmetros:
            pais (str)          : 2 caracteres (ex: 'BR')
            grupo (str)         : 1 caractere  (ex: 'C')
            tipo_alimento (str) : 1 caractere  (ex: 'A')

        Retorna:
            tuple: (codigo, sec)

        Lança:
            ValueError: se os parâmetros forem inválidos
        """

        # Passo 0 — validar entrada
        self._validar_entrada(pais, grupo, tipo_alimento)

        # Passos 1, 2 e 3 — calcular sec por grupo
        sec = self._obter_proxima_sequencia(grupo)

        # Passo 4 — formatar com zerofill
        seq_formatada = self._formatar_sequencia(sec)

        # Passo 5 — compor o código final
        codigo = f"{pais.upper()}{grupo.upper()}{seq_formatada}{tipo_alimento.upper()}"

        print(f"   🏷️  Código gerado: {codigo}")

        # Passo 6 — retornar código e sec
        return codigo, sec

    # ================================================================
    #  INSERT
    # ================================================================

    def inserir(self, pais, grupo, tipo_alimento):
        """
        Insere um novo produto gerando código e sec automaticamente.

        Parâmetros:
            pais (str)          : 2 caracteres (ex: 'BR')
            grupo (str)         : 1 caractere  (ex: 'C')
            tipo_alimento (str) : 1 caractere  (ex: 'A')

        Retorna:
            tuple: (id, codigo, sec) ou (None, None, None) se falhou
        """

        # Gera código e sec seguindo os 6 passos
        codigo, sec = self.gerar_codigo(pais, grupo, tipo_alimento)

        query = """
            INSERT INTO codigos_sequenciais (codigo, sec, Grupo, Tipo_Alimento, Pais)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            codigo,
            sec,
            grupo.upper(),
            tipo_alimento.upper(),
            pais.upper()
        )

        novo_id = self.db.executar_query(query, params)

        if novo_id:
            print(f"   ✅ Produto inserido │ ID: {novo_id} │ Código: {codigo} │ Sec: {sec}")
            return novo_id, codigo, sec

        return None, None, None

    def inserir_varios(self, lista_produtos):
        """
        Insere múltiplos produtos de uma vez.
        lista_produtos: lista de dicts com chaves: pais, grupo, tipo_alimento
        """
        inseridos = 0
        for produto in lista_produtos:
            id_novo, _, _ = self.inserir(
                pais=produto['pais'],
                grupo=produto['grupo'],
                tipo_alimento=produto['tipo_alimento']
            )
            if id_novo:
                inseridos += 1

        print(f"\n   📊 Total inserido: {inseridos}/{len(lista_produtos)}")
        return inseridos

    # ================================================================
    #  SELECT — CONSULTAS
    # ================================================================

    def buscar_todos(self):
        """Retorna todos os produtos ordenados pelo ID."""
        query = """
            SELECT id, codigo, sec, Grupo, Tipo_Alimento, Pais
            FROM codigos_sequenciais
            ORDER BY id
        """
        return self.db.executar_consulta(query)

    def buscar_por_codigo(self, codigo):
        """Busca um produto pelo código exato."""
        query = "SELECT * FROM codigos_sequenciais WHERE codigo = %s"
        resultados = self.db.executar_consulta(query, (codigo.upper(),))
        return resultados[0] if resultados else None

    def buscar_por_id(self, produto_id):
        """Busca um produto pelo ID."""
        query = "SELECT * FROM codigos_sequenciais WHERE id = %s"
        resultados = self.db.executar_consulta(query, (produto_id,))
        return resultados[0] if resultados else None

    def buscar_por_pais(self, pais):
        """Retorna todos os produtos de um país."""
        query = """
            SELECT id, codigo, sec, Grupo, Tipo_Alimento, Pais
            FROM codigos_sequenciais
            WHERE Pais = %s
            ORDER BY Grupo, sec
        """
        return self.db.executar_consulta(query, (pais.upper(),))

    def buscar_por_grupo(self, grupo):
        """Retorna todos os produtos de um grupo."""
        query = """
            SELECT id, codigo, sec, Grupo, Tipo_Alimento, Pais
            FROM codigos_sequenciais
            WHERE Grupo = %s
            ORDER BY sec
        """
        return self.db.executar_consulta(query, (grupo.upper(),))

    def buscar_por_tipo_alimento(self, tipo):
        """Retorna todos os produtos de um tipo de alimento."""
        query = """
            SELECT id, codigo, sec, Grupo, Tipo_Alimento, Pais
            FROM codigos_sequenciais
            WHERE Tipo_Alimento = %s
            ORDER BY Grupo, sec
        """
        return self.db.executar_consulta(query, (tipo.upper(),))

    def contar_produtos(self):
        """Retorna a contagem total de produtos."""
        query = "SELECT COUNT(*) AS total FROM codigos_sequenciais"
        resultado = self.db.executar_consulta(query)
        return resultado[0]['total'] if resultado else 0

    def contar_por_grupo(self):
        """Retorna contagem de produtos agrupada por grupo."""
        query = """
            SELECT Grupo, COUNT(*) AS quantidade, MAX(sec) AS maior_sec
            FROM codigos_sequenciais
            GROUP BY Grupo
            ORDER BY Grupo
        """
        return self.db.executar_consulta(query)

    def contar_por_pais(self):
        """Retorna contagem de produtos agrupada por país."""
        query = """
            SELECT Pais, COUNT(*) AS quantidade
            FROM codigos_sequenciais
            GROUP BY Pais
            ORDER BY quantidade DESC
        """
        return self.db.executar_consulta(query)