# main.py

from database import Database
from models import ProdutoModel


# ============================================================
#  EXIBIÇÃO FORMATADA
# ============================================================

def exibir_tabela(dados, titulo="RESULTADOS"):
    """Exibe os dados como tabela formatada no terminal."""
    if not dados:
        print("\n   ⚠️  Nenhum registro encontrado.\n")
        return

    print(f"\n{'═' * 78}")
    print(f"  {titulo}")
    print(f"{'═' * 78}")

    colunas = list(dados[0].keys())
    header = " │ ".join(f"{col:^12}" for col in colunas)
    print(f"  {header}")
    print(f"  {'─' * len(header)}")

    for row in dados:
        linha = " │ ".join(f"{str(v):^12}" for v in row.values())
        print(f"  {linha}")

    print(f"{'═' * 78}")
    print(f"  Total: {len(dados)} registro(s)\n")


def exibir_produto_unico(produto):
    """Exibe os detalhes de um único produto."""
    if not produto:
        print("\n   ⚠️  Produto não encontrado.\n")
        return

    print(f"\n  ┌───────────────────────────────────┐")
    print(f"  │       DETALHES DO PRODUTO         │")
    print(f"  ├───────────────────────────────────┤")
    print(f"  │  ID             : {produto['id']:<15} │")
    print(f"  │  Código         : {produto['codigo']:<15} │")
    print(f"  │  Sequência (sec): {produto['sec']:<15} │")
    print(f"  │  Grupo          : {produto['Grupo']:<15} │")
    print(f"  │  Tipo Alimento  : {produto['Tipo_Alimento']:<15} │")
    print(f"  │  País           : {produto['Pais']:<15} │")
    print(f"  └───────────────────────────────────┘\n")


# ============================================================
#  VALIDAÇÕES
# ============================================================

def validar_pais(pais):
    if len(pais) != 2 or not pais.isalpha():
        print("   ⚠️  País deve ter exatamente 2 letras (ex: BR, US, AR)")
        return False
    return True


def validar_grupo(grupo):
    if len(grupo) != 1 or not grupo.isalpha():
        print("   ⚠️  Grupo deve ter exatamente 1 letra (ex: C, A, B)")
        return False
    return True


def validar_tipo(tipo):
    if len(tipo) != 1 or not tipo.isalpha():
        print("   ⚠️  Tipo Alimento deve ter exatamente 1 letra (ex: A, B)")
        return False
    return True


# ============================================================
#  POPULAÇÃO INICIAL — sec agora é POR GRUPO
# ============================================================

def popular_banco(produto_model):
    """
    Insere dados de exemplo.
    A sequência é calculada AUTOMATICAMENTE por grupo.
    """

    print("\n📦 Inserindo produtos de exemplo...")
    print("─" * 50)

    produtos_iniciais = [
        # Grupo C — sec será 1, 2, 3, 4 automaticamente
        {'pais': 'BR', 'grupo': 'C', 'tipo_alimento': 'A'},
        {'pais': 'BR', 'grupo': 'C', 'tipo_alimento': 'A'},
        {'pais': 'BR', 'grupo': 'C', 'tipo_alimento': 'B'},
        {'pais': 'US', 'grupo': 'C', 'tipo_alimento': 'A'},

        # Grupo A — sec será 1, 2, 3 automaticamente
        {'pais': 'US', 'grupo': 'A', 'tipo_alimento': 'A'},
        {'pais': 'US', 'grupo': 'A', 'tipo_alimento': 'B'},
        {'pais': 'BR', 'grupo': 'A', 'tipo_alimento': 'A'},

        # Grupo B — sec será 1, 2 automaticamente
        {'pais': 'AR', 'grupo': 'B', 'tipo_alimento': 'A'},
        {'pais': 'AR', 'grupo': 'B', 'tipo_alimento': 'B'},
    ]

    produto_model.inserir_varios(produtos_iniciais)


# ============================================================
#  INSERÇÃO MANUAL
# ============================================================

def inserir_produto_manual(produto_model):
    """Coleta dados do usuário e insere um produto."""
    print("\n  ╔═══════════════════════════════════╗")
    print("  ║      INSERIR NOVO PRODUTO         ║")
    print("  ╚═══════════════════════════════════╝")
    print("  O código e a sequência são gerados")
    print("  AUTOMATICAMENTE com base no grupo.\n")

    pais = input("   País (2 letras, ex: BR): ").strip()
    if not validar_pais(pais):
        return

    grupo = input("   Grupo (1 letra, ex: C): ").strip()
    if not validar_grupo(grupo):
        return

    tipo = input("   Tipo Alimento (1 letra, ex: A): ").strip()
    if not validar_tipo(tipo):
        return

    print()
    produto_model.inserir(pais, grupo, tipo)


# ============================================================
#  MENU PRINCIPAL
# ============================================================

def menu_principal():
    print("\n" + "═" * 54)
    print("     🏭  SISTEMA DE PRODUTOS - produtos_db")
    print("═" * 54)
    print("  ── INSERÇÃO ──────────────────────────────────")
    print("   1 │ Popular banco (dados iniciais)")
    print("   2 │ Inserir novo produto")
    print("  ── CONSULTAS ─────────────────────────────────")
    print("   3 │ Listar TODOS os produtos")
    print("   4 │ Buscar por CÓDIGO")
    print("   5 │ Filtrar por PAÍS")
    print("   6 │ Filtrar por GRUPO")
    print("   7 │ Filtrar por TIPO DE ALIMENTO")
    print("   8 │ Contagem por GRUPO (mostra maior sec)")
    print("   9 │ Contagem por PAÍS")
    print("  ──────────────────────────────────────────────")
    print("   0 │ Sair")
    print("═" * 54)

    return input("  Escolha uma opção: ").strip()


# ============================================================
#  EXECUÇÃO PRINCIPAL
# ============================================================

def main():
    db = Database()

    if not db.conectar():
        print("💥 Não foi possível conectar ao banco. Encerrando.")
        return

    produto_model = ProdutoModel(db)

    try:
        while True:
            opcao = menu_principal()

            if opcao == "1":
                popular_banco(produto_model)

            elif opcao == "2":
                inserir_produto_manual(produto_model)

            elif opcao == "3":
                dados = produto_model.buscar_todos()
                exibir_tabela(dados, "TODOS OS PRODUTOS")

            elif opcao == "4":
                codigo = input("\n   Código (ex: BRC0004A): ").strip()
                produto = produto_model.buscar_por_codigo(codigo)
                exibir_produto_unico(produto)

            elif opcao == "5":
                pais = input("\n   País (ex: BR): ").strip()
                if validar_pais(pais):
                    dados = produto_model.buscar_por_pais(pais)
                    exibir_tabela(dados, f"PRODUTOS DO PAÍS: {pais.upper()}")

            elif opcao == "6":
                grupo = input("\n   Grupo (ex: C): ").strip()
                if validar_grupo(grupo):
                    dados = produto_model.buscar_por_grupo(grupo)
                    exibir_tabela(dados, f"PRODUTOS DO GRUPO: {grupo.upper()}")

            elif opcao == "7":
                tipo = input("\n   Tipo (ex: A): ").strip()
                if validar_tipo(tipo):
                    dados = produto_model.buscar_por_tipo_alimento(tipo)
                    exibir_tabela(dados, f"PRODUTOS DO TIPO: {tipo.upper()}")

            elif opcao == "8":
                dados = produto_model.contar_por_grupo()
                exibir_tabela(dados, "CONTAGEM POR GRUPO (com maior sec)")

            elif opcao == "9":
                dados = produto_model.contar_por_pais()
                total = produto_model.contar_produtos()
                exibir_tabela(dados, f"CONTAGEM POR PAÍS (Total: {total})")

            elif opcao == "0":
                print("\n   👋 Encerrando o sistema...")
                break

            else:
                print("   ⚠️  Opção inválida.")

    finally:
        db.desconectar()


if __name__ == "__main__":
    main()