from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime

def promo_game():
    # Configurando o Selenium
    driver = webdriver.Chrome()  # Use webdriver.Firefox() se estiver usando o Firefox
    driver.get('https://www.nuuvem.com/br-pt/catalog/platforms/pc/price/promo/sort/bestselling/sort-mode/desc')

    # Esperando a página carregar completamente (ajuste o tempo conforme necessário)
    time.sleep(5)  # Espera 5 segundos para garantir que a página carregue completamente

    # Capturando o HTML renderizado pelo JavaScript
    html_text = driver.page_source
    soup = BeautifulSoup(html_text, 'lxml')

    # Fechando o navegador
    driver.quit()

    # Extraindo os dados dos jogos
    games = soup.find_all('div', class_='product-card--grid')
    all_games_info = ""  # String para acumular as informações de todos os jogos

    for game in games:
        # Obtendo o nome do jogo
        game_name = game.find('h3', class_='product-title').text.strip()

        # Obtendo as plataformas disponíveis
        platforms = game.find_all('i', class_='icon')
        platform_names = ', '.join([platform['title'] for platform in platforms if 'title' in platform.attrs])

        # Obtendo o preço do jogo
        price_integer = game.select_one('.product-button__label .integer')
        price_decimal = game.select_one('.product-button__label .decimal')

        # Formatando o preço ou definindo como "Preço não disponível"
        if price_integer and price_decimal:
            price = f"R$ {price_integer.text.strip()}{price_decimal.text.strip()}"
        else:
            price = "Preço não disponível"

        # Acumulando informações de todos os jogos
        all_games_info += f"Nome do Jogo: {game_name}\n"
        all_games_info += f"Plataformas: {platform_names}\n"
        all_games_info += f"Preço: {price}\n"
        all_games_info += "-" * 40 + "\n"

    # Criar diretório 'promo' se não existir
    os.makedirs('promo', exist_ok=True)

    # Gerar nome de arquivo com timestamp para garantir que o nome do arquivo seja único
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'promo/promocoes_{timestamp}.txt'

    # Salvando todas as informações em um arquivo com o timestamp
    with open(filename, 'w') as file:
        file.write(all_games_info)

    # Informar que o arquivo foi salvo com sucesso
    print(f'File saved: {filename}')

if __name__ == '__main__':
    while True:
        # Executa a função para coletar e salvar informações de promoções de jogos
        promo_game()
        # Define o tempo de espera entre as execuções em minutos
        time_wait = 10  # Tempo de espera em minutos
        print(f'Waiting {time_wait} minutes...')
        # Aguarda o tempo definido antes de executar novamente
        time.sleep(time_wait * 60)
