import psycopg2
import requests
import json
from psycopg2.extras import Json
import time

DB_HOST = "localhost"
DB_PORT = 5444
DB_NAME = "mtg_analyzer_data"
DB_USER = "admin"
DB_PASS = "password123"

def conectar_banco():
    try:
        conexao = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conexao
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None

def criar_tabela(cursor):
    sql_create = """
    CREATE TABLE IF NOT EXISTS bronze_scryfall_cards(
        id SERIAL PRIMARY KEY,
        data_extracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        payload JSONB NOT NULL
    )
    """
    cursor.execute(sql_create)
    print("Tabela verificada/criada com sucesso.")
    
def buscar_dados_scryfall():
    url = "https://api.scryfall.com/cards/search"

    parametros = {
        "q": "legal:commander"
    }
    
    headers = {
        "User-Agent": "Scryfall Collector Test",
        "Accept": "application/json"
    }

    print("Iniciando extração da API do Scryfall...")

    conexao = conectar_banco()
    if not conexao:
        return
    try:
        cursor = conexao.cursor()
        criar_tabela(cursor)

        sql_insert = "INSERT INTO bronze_scryfall_cards (payload) VALUES (%s);"
        total_inserido = 0
        pagina_atual = 1

        while url: 
            print(f"Buscando página: {pagina_atual}...")

            resposta = requests.get(url, params=parametros if pagina_atual == 1 else None, headers=headers)

            if resposta.status_code == 200:
                dados = resposta.json()
                cartas = dados.get('data', [])

                for carta in cartas: 
                    cursor.execute(sql_insert, [Json(carta)])
                    total_inserido += 1

                conexao.commit()
                print(f" -> {len(cartas)} cartas salvas. Total acumulado: {total_inserido}")

                if dados.get('has_more'):
                    url = dados.get('next_page')
                    pagina_atual += 1
                    time.sleep(0.2)

                else:
                    print("\n Extração concluída! Não há mais cartas.")
                    url = None
            else: 
                print(f"Falha na extração. Código: {resposta.status_code}") 
                print(resposta.text)
                break

    except Exception as e:
        print(f"Erro durante a operação no banco: {e}")
        conexao.rollback()
    finally:
        cursor.close()
        conexao.close()
        print("\n Conexão com o banco fechada.")
        
        

if __name__ == "__main__":
    buscar_dados_scryfall()