# ================================================================
#  CONFIGURAÇÃO DO BANCO DE DADOS
#
#  Em ambiente CI/CD: usa variáveis de ambiente
#  Em ambiente local: usa valores padrão (fallback)
# ================================================================

import os

DB_CONFIG = {
    'host':     os.environ.get('DB_HOST',     'localhost'),
    'port':     int(os.environ.get('DB_PORT', '3306')),
    'user':     os.environ.get('DB_USER',     'root'),
    'password': os.environ.get('DB_PASSWORD', 'jm@2026'),
    'database': os.environ.get('DB_NAME',     'produtos_db'),
}