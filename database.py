#Classe de conexão

# database.py

import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


class Database:
    """Gerencia a conexão com o banco de dados MySQL."""

    def __init__(self):
        self.connection = None
        self.cursor = None

    def conectar(self):
        """Estabelece conexão com o banco de dados."""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)

            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                info = self.connection.get_server_info()
                print(f"✅ Conectado ao MySQL Server versão {info}")
                print(f"📁 Banco de dados: {DB_CONFIG['database']}")
                return True

        except Error as e:
            print(f"❌ Erro ao conectar: {e}")
            return False

    def desconectar(self):
        """Encerra a conexão com o banco de dados."""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("\n🔌 Conexão encerrada com sucesso.")

    def executar_query(self, query, params=None):
        """Executa INSERT, UPDATE ou DELETE."""
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.lastrowid
        except Error as e:
            self.connection.rollback()
            print(f"❌ Erro na execução: {e}")
            return None

    def executar_consulta(self, query, params=None):
        """Executa SELECT e retorna os resultados."""
        try:
            self.cursor.execute(query, params)
            resultados = self.cursor.fetchall()
            return resultados
        except Error as e:
            print(f"❌ Erro na consulta: {e}")
            return []