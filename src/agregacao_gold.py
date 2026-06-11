import pandas as pd
from sqlalchemy import create_engine

DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME = "admin", "password123", "localhost", 5444, "mtg_analyzer_data"
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

def processar_gold():
    print("1. Lendo dados limpos da camada Silver...")
    df_silver = pd.read_sql("SELECT * FROM silver_mtg_cards;", engine)
    
    print("2. Gerando Dataset 1: Índice de Fetch Lands")
    fetches = [
        "Polluted Delta",
        "Verdant Catacombs",
        "Scalding Tarn",
        "Misty Rainforest",
        "Marsh Flats",
        "Flooded Strand",
        "Wooded Foothills",
        "Arid Mesa",
        "Bloodstained Mire",
        "Windswept Heath"
    ]

    df_fetches = df_silver[df_silver['nome'].isin(fetches)]
    custo_total = df_fetches['preco_usd'].sum()

    df_gold_mana_cost = pd.DataFrame([{
        'metrica': 'Custo de fetches',
        'valor_total_usd': round(custo_total, 2)
    }])

    print("3. Gerando Dataset 2: Top 10 staples mais caras WUBRG")

    df_silver['is_wubrg'] = df_silver['identidade_cor'].apply(
        lambda x: set(str(x).split(',')) == {'W', 'U', 'B', 'R', 'G'}
    )
    
    df_gold_wubrg = df_silver[df_silver['is_wubrg']].sort_values(by='preco_usd', ascending=False).head(10)
    df_gold_wubrg = df_gold_wubrg[['nome', 'raridade', 'identidade_cor', 'preco_usd']]

    print("4. Gerando Dataset Gold 3: Top 15 cartas mais caras do formato Commander...")

    df_gold_top_geral = df_silver.sort_values(by='preco_usd', ascending=False).head(15)
    df_gold_top_geral = df_gold_top_geral[['nome', 'raridade', 'identidade_cor', 'preco_usd']]

    print("5. Salvando Datasets na Camada Gold...")
    df_gold_mana_cost.to_sql('gold_kpi_mana_grixis', engine, if_exists='replace', index=False)
    df_gold_wubrg.to_sql('gold_top10_wubrg', engine, if_exists='replace', index=False)
    df_gold_top_geral.to_sql('gold_top15_geral', engine, if_exists='replace', index=False)

    print("\nKPI: Custo de fetches")
    print("-" * 40)
    print(df_gold_mana_cost.to_string(index=False))
    
    print("\nRanking: Top 10 cartas WUBRG mais caras")
    print("-" * 40)
    print(df_gold_wubrg.to_string(index=False))

    print("\nRanking: Top 15 cartas mais caras do formato Commander")
    print("-" * 40)
    print(df_gold_top_geral.to_string(index=False))

if __name__ == "__main__":
    processar_gold()