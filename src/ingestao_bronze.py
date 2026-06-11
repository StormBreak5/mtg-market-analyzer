import requests
import json

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
    resposta = requests.get(url, params=parametros, headers=headers)

    if resposta.status_code == 200:
        dados = resposta.json()
        total_cards = dados.get('total_cards', 0)

        print(f"Sucesso! {total_cards} cartas encontradas.")
        print("-" * 50)

        primeira_carta = dados['data'][0]
        print("Estrutura do JSON da primeira carta (Dados Brutos): \n")
        print(json.dumps(primeira_carta, indent=4, ensure_ascii=False))

    else:
        print(f"Falha na extração. Código de erro: {resposta.status_code}")
        print(f"Detalhes do Erro:", resposta.text)

if __name__ == "__main__":
    buscar_dados_scryfall()