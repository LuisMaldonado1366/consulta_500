# -*- coding: utf-8 -*-

import pandas as pd
from woocommerce import API
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from decouple import Config, RepositoryEnv
from connection import Connection
import json

env_config = Config(repository = RepositoryEnv(source = '.env'))
DATABASE_HOST = env_config.get('DATABASE_HOST', default = 'localhost')
DATABASE_PORT = env_config.get('DATABASE_PORT', default = 3306, cast = int)
DATABASE_USER = env_config.get('DATABASE_USER', default = 'root')
DATABASE_PASSWORD = env_config.get('DATABASE_PASSWORD', default = '', cast = str)
DATABASE_NAME = env_config.get('DATABASE_NAME', default = 'mydb')


connection: object = Connection(host = DATABASE_HOST,
                        port = DATABASE_PORT,
                        user = DATABASE_USER,
                        password = DATABASE_PASSWORD,
                        database = DATABASE_NAME)

scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

credentials = Credentials.from_service_account_file(
    filename = '.secrets/sheets_token.json',
    scopes = scopes)

gc = gspread.authorize(credentials)

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

gs = gc.open_by_url('https://docs.google.com/spreadsheets/d/1jcxu6fzJC-n83OAFWlUgQVL-g-tnLc1ZqJB5X44JW9I')
worksheet = gs.worksheet('Consulta 500 Pedidos')

wc_creds: pd.DataFrame = connection.fetch_data(table = 'stock_update_config',
                                            fields = ['endpoint_url', 'endpoint_keys'])\
    .to_dict(orient='records')[0]
wc_endpoint = wc_creds.get('endpoint_url')
wc_keys = json.loads(wc_creds.get('endpoint_keys'))

wcapi = API(
    url = f'https://{wc_endpoint}',
    consumer_key = wc_keys.get('customer_key'),
    consumer_secret = wc_keys.get('client_secret'),
    wp_api = True,
    version = 'wc/v3',
    query_string_auth = True,
    verify_ssl = True,
    timeout = 50
)

page = []
#orders = pd.DataFrame()

try:
    print('Reading orders from API.\n')
    for pages in range(1,6):
        response = wcapi.get(str('orders?per_page=100&page='+str(pages)))
        print(f'Response code: {response.status_code}')
        if response.status_code == 200:
            print('Reading ' + str(100 * pages) + ' orders...')
        data = response.json()
        for i in range(len(data)):
            page.append([data[i]['id'],
                        data[i]['date_created'],
                        data[i]['status'],
                        '1',
                        data[i]['line_items'][0]['quantity'],
                        data[i]['line_items'][0]['sku'],
                        data[i]['line_items'][0]['name'],
                        data[i]['line_items'][0]['total'],
                        data[i]['shipping_total'],
                        data[i]['total'],
                        data[i]['payment_method_title'],
                        data[i]['number'],
                        (float(data[i]['line_items'][0]['total'])/int(data[i]['line_items'][0]['quantity']))/1.16,
                        '1',
                        data[i]['line_items'][0]['sku'],
                        data[i]['line_items'][0]['quantity'],
                        '1',
                        data[i]['shipping']['city'],
                        data[i]['shipping']['state'],
                        data[i]['shipping']['postcode'],
                        data[i]['billing']['phone'],
                        #['']#
                        data[i]['shipping_lines'][0]['method_title']  
                        ])
            j = 1
            for j in range(1, len(data[i]['line_items'])):
                page.append([data[i]['id'],
                             ' ',
                             ' ',
                             j+1,
                             data[i]['line_items'][j]['quantity'],
                             data[i]['line_items'][j]['sku'],
                             data[i]['line_items'][j]['name'],
                             data[i]['line_items'][j]['total'],
                             ' ',
                             ' ',
                             ' ',
                             data[i]['id'],
                             (float(data[i]['line_items'][j]['total'])/int(data[i]['line_items'][j]['quantity']))/1.16,
                             '1',
                             data[i]['line_items'][j]['sku'],
                             data[i]['line_items'][j]['quantity'],
                             '1',
                             ' ',
                             ' ',
                             ' ',
                             ' ',
                             ' '
                             ])
            page.append([' ',
                         ' ',
                         ' ',
                         j+1,
                         ' ',
                         ' ',
                         'Envío',
                         ' ',
                         ' ',
                         ' ',
                         ' ',
                         data[i]['id'],
                         float(data[i]['shipping_total'])/1.16,
                         '1',
                         'E001',
                         '1',
                         '1',
                         ' ',
                         ' ',
                         ' ',
                         ' ',
                         ' ',
                         ])
    orders_df = pd.DataFrame(page)
    orders_df.columns = ['Número de Orden', 
                  'Hora Creación',
                  'Estado del Pedido', 
                  'Orden',	
                  'Cantidad',	
                  'SKU',	
                  'Descripción', 
                  'Precio', 
                  'Envío',	
                  'Total',
                  'Método de Pago', 
                  'Pedido', 
                  'Pre.sin IVA', 
                  'Clave Esquema Impuestos',
                  'SKU',
                  'Cantidad',
                  'Álmacen',	
                  'Colonia',
                  'Estado',
                  'C.P.',
                  'Teléfono',
                  'Tipo Envío']
    
    set_with_dataframe(worksheet = worksheet, dataframe = orders_df, include_index = False,
                       include_column_header = True, resize = True)
    
    print('\n\nSuccess getting orders.')

except:
    print('\n\nError getting orders.')