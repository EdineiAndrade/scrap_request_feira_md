from bs4 import BeautifulSoup
import requests
import re

def scrap_feira_md():
    url_base = "https://www.feiradamadrugadasp.com.br"
    response = requests.get(url_base)
    
    if response.status_code != 200:
        print("Failed to retrieve the page")
        return []
    soup = BeautifulSoup(response.content, 'html.parser')
    # Seleciona todos os links dentro de elementos com a classe 'all-departments'
    categories = soup.select('.all-departments a')

    # Extrai os hrefs
    links_categorias = [a['href'] for a in categories if a.has_attr('href')]
 
    for link_categoria in links_categorias:
        url_categoria = f"{url_base}{link_categoria}"        
        response = requests.get(url_categoria) 

        if response.status_code != 200:
            print(f"Failed to retrieve the page: {link_categoria}")
            continue
        
        soup = BeautifulSoup(response.content, 'html.parser')
        texto_paginacao = soup.find(class_="info").get_text(strip=True)
        numeros = list(map(int, re.findall(r'\d+', texto_paginacao)))
        if len(numeros) >= 2:
            total_paginas = int(numeros[1])
        else:
            total_paginas = 1
        
        for pagina in range(1, total_paginas + 1):
            url_pagina = f"{url_categoria}?p={pagina}"
            response = requests.get(url_pagina)

            if response.status_code != 200:
                print(f"Failed to retrieve the page: {url_pagina}")
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extrai todos os links, ignorando '#' e vazios
            links_products = [
                div.select_one('a').get('href') 
                for div in soup.select('.item-product') 
                if div.select_one('a') and 
                div.select_one('a').get('href') and 
                div.select_one('a').get('href') != '#'
            ]
            
            for link_product in links_products:
                url_product = f"{url_base}{link_product}"
                url_product = "https://www.feiradamadrugadasp.com.br/camiseta-masculina-basica-lisa-sem-estampa-plus-size/p/220744/"
                item = soup.select_one('.item-product')
                data_id = item.get('data-id') if item and item.has_attr('data-id') else 'N/A'
                response = requests.get(url_product)

                if response.status_code != 200:
                    print(f"Failed to retrieve the page: {url_product}")
                    continue
                
                product = BeautifulSoup(response.content, 'html.parser') 
                name = product.find('h1', class_='name').text.strip()
                price = float(product.find('strong', class_='sale_price').text.strip().replace('R$ ','').replace('.','').replace(',','.'))
                cores = product.select('.cor .img img')
                lista_cores = [label.get_text(strip=True) for label in product.select('.cor .values .value:not(.disabled)')]
                lista_tamanhos = [label.get_text(strip=True) for label in product.select('.tam .values span')]
                print(f"Product ID: {data_id}, Name: {name}, Price: {price}, Colors: {lista_cores}")

            #return product_list
if __name__ == "__main__":
    products = scrap_feira_md()
    