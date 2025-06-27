import ast
from time import sleep
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

from sheets import save_to_google_sheets

# Função para salvar os dados em um arquivo Excel
def save_to_sheets(data):    
    #data.to_excel(filename, index=False)
    save_to_google_sheets(data,0)
def scrap_feira_md():
    url_base = "https://www.feiradamadrugadasp.com.br"
    response = requests.get(url_base)
    products_data = []
    cont = 0
    total_produtos = 0
    if response.status_code != 200:
        print("Failed to retrieve the page")
        return []
    soup = BeautifulSoup(response.content, 'html.parser')
    # Seleciona todos os links dentro de elementos com a classe 'all-departments'
    categories = soup.select('.all-departments a')

    # Extrai os hrefs
    links_categorias = [a['href'] for a in categories if a.has_attr('href')]
 
    for link_categoria in links_categorias:
        if link_categoria == '/novidades-da-semana/?map=cl&sort=lancamentos':
            continue
        url_categoria = f"{url_base}{link_categoria}"        
        response = requests.get(url_categoria) 

        if response.status_code != 200:
            print(f"Failed to retrieve the page: {link_categoria}")
            continue
        
        soup = BeautifulSoup(response.content, 'html.parser')
        try:
            texto_paginacao = soup.find(class_="info").get_text(strip=True)
            total_paginas = int(list(map(int, re.findall(r'\d+', texto_paginacao))))
        except Exception as e:
            print(f"Erro ao extrair números da paginação para a categoria: {e}")
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
            # Remove duplicatas
            links_products = list(set(links_products))
            for link_product in links_products:
                url_product = f"{url_base}{link_product}"
                #url_product = "https://www.feiradamadrugadasp.com.br/camiseta-masculina-basica-lisa-sem-estampa-plus-size/p/220744/"
                item = soup.select_one('.item-product')
                codigo_sku = item.get('data-id') if item and item.has_attr('data-id') else 'N/A'
                response = requests.get(url_product)

                if response.status_code != 200:
                    print(f"Failed to retrieve the page: {url_product}")
                    continue
                
                product = BeautifulSoup(response.content, 'html.parser') 
                produto = product.find('h1', class_='name').text.strip()
                codigo = url_product.split('/')[-2]
                preco_custo = float(product.find('strong', class_='sale_price').text.strip().replace('R$ ','').replace('.','').replace(',','.'))
                preco_venda = round(float(preco_custo)* 1.1,2)
                categoria = url_categoria.split('/')[3].replace('-',' ').title()
                print(f"Processando categoria: {links_categorias.index(link_categoria) +1} de {len(categoria)+1} | página:{pagina} de {total_paginas} | Item: {links_products.index(link_product)+1} de {len(links_products)} | cont: {cont} de 100, faltam: {100-cont} para salvar, total_processado: {total_produtos}")
                #lista_cores = [label.get_text(strip=True) for label in product.select('.cor .values .value:not(.disabled)')]
                #lista_tamanhos = [label.get_text(strip=True) for label in product.select('.tam .values span')]
                lista_cores = [{
                    "Valores do Atributo 2": label.get_text(strip=True).replace('\n', '').replace('\t', ''),
                    "Estoque": 10
                } for label in product.select('.cor .values .value:not(.disabled)')]

                cores = [item['Valores do Atributo 2'] for item in lista_cores]
                lista_tamanhos = [{
                    "Valores do Atributo 1": label.get_text(strip=True).replace('\n', '').replace('\t', ''),
                    "Estoque": 10
                } for label in product.select('.tam .values span')]

                tamanhos = [item['Valores do Atributo 1'] for item in lista_tamanhos]
                paragrafos_1 = [
                    p.get_text(strip=True)  # Extrai o texto limpo
                    for p in product.select('div[itemprop="description"] p')  # Seletor CSS equivalente
                    if p.get_text(strip=True)  # Ignora parágrafos vazios
                ]
                paragrafos_2 = [
                    p.get_text(strip=True)  # Extrai o texto limpo
                    for p in product.select('div[itemprop="description"] li')  # Seletor CSS equivalente
                    if p.get_text(strip=True)  # Ignora parágrafos vazios
                ]
                description = ' '.join(paragrafos_1 + paragrafos_2)
                peso_produto = paragrafos_2[-2].replace('Peso do Produto:','')
                codigo_upc = paragrafos_2[-1].replace('Código UPC:','') 

                # Supondo que 'soup' já esteja definido com o HTML carregado
                imagens = product.select('#sly_carousel ul li a')

                lista_imagens = [
                    "https:" + link.get('big_img') if link.get('big_img') else ""
                    for link in imagens
                ]
                # Remove duplicatas e strings vazias
                lista_sem_duplicatas = list({img for img in lista_imagens if img})
                # Junta com vírgula e espaço
                lista_imagens_final = ", ".join(lista_sem_duplicatas) 
                if lista_cores:
                    df_cores = pd.DataFrame(lista_cores)
                    cores_str = ', '.join(cores)
                    cor = 'Cor'
                    cor_padrao = cores[0] if cores else ''
                else:
                    cor_padrao = cor = cores_str = df_cores = ""
                    
                if lista_tamanhos:
                    df_tamanhos = pd.DataFrame(lista_tamanhos)
                    tamanhos_str = ', '.join(tamanhos)
                    tamanho_meio = tamanhos[0] if tamanhos else ''
                    atributo1 = 'Tamanho'
                    atributo_global_2 = 1
                else:
                    tamanho_meio = atributo1 = tamanhos_str = df_tamanhos = ""
                    atributo_global_2 = 0
                # Cria o DataFrame imagem
                if len(lista_sem_duplicatas) >0:
                    df_imagens = pd.DataFrame(lista_sem_duplicatas)
                    df_imagens = df_imagens.transpose()
                    df_imagens.columns = [f'Imagem {i+1}' for i in range(len(df_imagens.columns))]
                else:
                    df_imagens =""
                
                df_final = process_products( [df_tamanhos,df_cores,df_imagens,{
                        'ID': codigo,
                        'SKU': codigo_sku,
                        'Código do Produto': codigo_upc,
                        'Preço promocional': 0,
                        "Tipo": "variable",
                        "GTIN UPC EAN ISBN": "",
                        'Nome': produto,
                        "Publicado": 1,
                        "Em Destaque": 0,
                        "Visibilidade no Catálogo": "visible",
                        "Descrição Curta": "",
                        "Descrição": description,
                        "Data de Preço Promocional Começa em": "",
                        "Data de Preço Promocional Termina em": "",
                        "Status do Imposto": "taxable",
                        "Classe de Imposto": "parent",
                        "Em Estoque": 0,
                        "Estoque": "",
                        "Quantidade Baixa de Estoque": 3,
                        "São Permitidas Encomendas": 0,
                        "Vendido Individualmente": 0,
                        "Peso (kg)": peso_produto,
                        "Comprimento (cm)": 32,
                        "Largura (cm)": 20,
                        "Altura (cm)": 12,
                        "Permitir avaliações de clientes?": 1,
                        "Nota de Compra": "",
                        "Preço Promocional": "",
                        "Preço de Custo": preco_custo,
                        "Preço de Venda": preco_venda,
                        "Categorias": categoria,
                        "Tags": "",
                        "Classe de Entrega": "",
                        "Imagens": lista_imagens_final,
                        "Limite de Downloads": "",
                        "Dias para Expirar o Download": "",
                        "Ascendente": f"id:{codigo}",
                        "Grupo de Produtos": "",
                        "Upsells": "",
                        "Venda Cruzada": "",
                        "URL Externa": "",
                        "Texto do Botão": "",
                        "Posição": 0,
                        "Brands": "",
                        "Nome do Atributo 1": atributo1,
                        "Valores do Atributo 1": tamanhos_str,
                        "Visibilidade do Atributo 1": 0,
                        "Atributo Global 1": atributo1,
                        "Atributo Padrão 1": tamanho_meio,
                        "Nome do Atributo 2": cor,
                        "Valores do Atributo 2": cores_str,
                        "Visibilidade do Atributo 2": 0,
                        "Atributo Global 2": atributo_global_2,
                        "Atributo Padrão 2": cor_padrao,
                        "Galpão": " Galpão 8"
                    }])
    
                products_data.append(df_final)
                df_final = pd.concat(products_data, ignore_index=True)
                df_final = df_final.fillna("")
                cont += 1
                total_produtos += 1
                if cont >= 100:
                    sleep(2)  # Pausa de 5 segundos a cada 100 produtos
                    print(f"Salvando +{cont} produtos processados até agora...")
                    save_to_sheets(df_final)
                    cont = 0

    return df_final
def process_products(products):
    df_tamanhos, df_cores, df_imagens, produto_dict = products
    try:
                        # Otimização: Evitar múltiplos concat e explode desnecessários
        df_produto = pd.DataFrame([produto_dict])
        if len(df_imagens) > 0:
            df_produto = pd.concat([df_produto, df_imagens], axis=1)

        if len(df_cores) <= 1 and len(df_tamanhos) > 1:
            coluna_atributo = "Valores do Atributo 1"
            df_explodido = df_produto.explode(coluna_atributo).reset_index(drop=True)
            df_explodido[coluna_atributo] = df_explodido[coluna_atributo].apply(lambda x: x.split(", ") if x == "P, M, G, GG" else ast.literal_eval(x) if isinstance(x, str) else x)
            df_explodido = df_explodido.explode(coluna_atributo).reset_index(drop=True)
        elif len(df_cores) <= 1 and len(df_tamanhos) <= 1:
            df_explodido = df_produto.explode("Valores do Atributo 1").reset_index(drop=True)
        else:
            coluna_atributo = "Valores do Atributo 2"
            df_explodido = df_produto.explode(coluna_atributo).reset_index(drop=True)
            df_explodido[coluna_atributo] = df_explodido[coluna_atributo].str.split(", ")
            df_explodido = df_explodido.explode(coluna_atributo, ignore_index=True)

        df_explodido = df_explodido.drop(columns=["Estoque"])
        if len(df_imagens) > 0:
            numero_imagens = df_imagens.shape[1]
            df_explodido.iloc[:, -numero_imagens:] = ""

        df_explodido["Tipo"] = "variation"
        df_explodido[["Descrição", "Peso (kg)", "Comprimento (cm)", "Largura (cm)", "Altura (cm)", "Categorias", "Visibilidade do Atributo 1", "Atributo Padrão 1", "Quantidade Baixa de Estoque", "Imagens"]] = None
        df_produto[["Classe de Imposto", "Ascendente", "Preço de Custo", "Preço de Venda"]] = None
        df_explodido["Permitir avaliações de clientes?"] = 0
        df_explodido["Posição"] = df_explodido.index + 1
        df_explodido["ID"] = df_explodido["ID"].astype(str) + df_explodido["Posição"].astype(str)

        if len(df_cores) <= 1 and len(df_tamanhos) <= 1:
            df_final = df_produto
            pd.set_option('future.no_silent_downcasting', True)
            df_final = df_final.fillna("").astype(str)
            df_final["Tipo"] = "simple"
        else:
            df_ref = df_tamanhos if coluna_atributo == "Valores do Atributo 1" else df_cores
            df_final = df_explodido.merge(df_ref[[coluna_atributo, "Estoque"]], on=coluna_atributo, how="left")
            pd.set_option('future.no_silent_downcasting', True)
            df_final = df_final.fillna("").astype(str)
            df_final["Em Estoque"] = df_final["Estoque"]
            df_final["Tipo"] = "variation"
            df_final = pd.concat([df_produto, df_final], ignore_index=True)

        return df_final
    except Exception as e:
        print(f"Erro ao processar o produto url_product: {e}")
if __name__ == "__main__":
    products = scrap_feira_md()
    if products is not None:
        save_to_sheets(products)
    else:
        print("No products found or an error occurred during scraping.")
    print("Scraping completed successfully.")