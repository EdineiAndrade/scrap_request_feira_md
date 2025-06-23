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
        
        
        if not products:
            print(f"No products found on page: {link_categoria}")
            continue

        links = []
        for product in products:
            link = product.find('a', class_='product-link')
            if link and 'href' in link.attrs:
                links.append(link['href'])
            #if not links:
            

            # product_list = []
            # for product in products:
            #     name = product.find('h2', class_='product-title').text.strip()
            #     price = product.find('span', class_='product-price').text.strip()
            #     product_list.append({'name': name, 'price': price})

            #return product_list
if __name__ == "__main__":
    products = scrap_feira_md()
    