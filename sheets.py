import os
import gspread
from google.oauth2.service_account import Credentials

def get_credentials_file():  

    return os.path.join("C:\\sh", "credentials.json") 
def get_id_sheet_file():  
    caminho = r"C:\sh\id_sheet.txt"  # Caminho correto
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as arquivo:
            linha = arquivo.readline().strip()  # Lê a primeira linha e remove espaços extras
            return linha
def authenticate_google_sheets():  
    #Autentica no Google Sheets e retorna o cliente gspread.    
    credentials_file = get_credentials_file()
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    # Verifica se o arquivo de credenciais existe antes de autenticar
    if not os.path.exists(credentials_file):
        raise FileNotFoundError(f"❌ Arquivo de credenciais não encontrado: {credentials_file}")

    credentials = Credentials.from_service_account_file(credentials_file, scopes=scopes)
    return gspread.authorize(credentials)

def save_to_google_sheets(data, numero_sheet):    
    sheet_id = get_id_sheet_file()  # ID da planilha
    client = authenticate_google_sheets()
    sheet = client.open_by_key(sheet_id).get_worksheet(numero_sheet)  # Abre a terceira aba
    
    # Apagar os dados atuais
    sheet.clear()
    
    mask = data["Valores do Atributo 1"].apply(lambda x: isinstance(x, (list, tuple)))  # Identifica apenas listas/tuplas
    data.loc[mask, "Valores do Atributo 1"] = data.loc[mask, "Valores do Atributo 1"].apply(lambda x: ", ".join(map(str, x)))

    # Transformar em lista de listas, incluindo os títulos
    data_to_upload = [data.columns.tolist()] + data.values.tolist()

    # Insere os dados no Google Sheets
    sheet.append_rows(data_to_upload)
    print("✅ Dados salvos no Google Sheets.")


