import psycopg2
import pandas as pd
from sqlalchemy import create_engine

DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME = "admin", "password123", "localhost", 5444, "mtg_analyzer_data"
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def processar_silver():
    print("1. Lendo JSONs da camada Bronze...")
    conexao = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    df_bronze = pd.read_sql("SELECT payload FROM bronze_scryfall_cards;", conexao)
    conexao.close()

    print("2. Achatando e limpando dados...")
    cartas = []
    for _, row in df_bronze.iterrows():
        dado = row['payload']
        if dado.get('object') == 'card':
            precos = dado.get('prices', {})

            cartas.append({
                'id_scryfall': dado.get('id'),
                'nome': dado.get('name'),
                'identidade_cor': ",".join(dado.get('color_identity', [])),
                'raridade': dado.get('rarity'),
                'preco_usd': float(precos.get('usd') or precos.get('usd_foil') or 0.0),
            })
    
    df_silver = pd.DataFrame(cartas)

    print("3. Salvando dados estruturados na camada Silver...")
    df_silver.to_sql('silver_mtg_cards', engine, if_exists='replace', index=False)

    print(f"Sucesso {len(df_silver)} cartas limpas e estruturadas.")

if __name__ == '__main__':
    processar_silver()