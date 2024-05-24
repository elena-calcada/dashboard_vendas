import streamlit as st
import requests
import pandas as pd
import time

@st.cache_data
def converte_csv(df):
  return df.to_csv(index=False).encode('utf-8')

def mensagem_sucesso():
  sucesso = st.success('Arquivo baixado com sucesso!', icon="✅")
  time.sleep(5)
  sucesso.empty()

st.set_page_config(layout='wide')

st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'

response = requests.get(url)
data = pd.DataFrame.from_dict(response.json())
data['Data da Compra'] = pd.to_datetime(data['Data da Compra'], format='%d/%m/%Y')

############################## CRIAÇÃO DE FILTRO NO BODY ##############################
with st.expander('Colunas'):
  colunas = st.multiselect('Selecione as colunas', list(data.columns), list(data.columns))

############################## CRIAÇÃO DE FILTROS NO SIDEBAR ##############################
st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):
  produtos = st.multiselect('Selecione os produtos', data['Produto'].unique(), data['Produto'].unique())

with st.sidebar.expander('Categoria do produto'):
  categorias = st.multiselect('Selecione as categorias', data['Categoria do Produto'].unique(), data['Categoria do Produto'].unique())

with st.sidebar.expander('Preço do produto'):
  precos = st.slider('Selecione o preço', 0, 5000, (0, 5000))

with st.sidebar.expander('Frete do produto'):
  fretes = st.slider('Selecione o valor do frete', 0, 250, (0, 250))

with st.sidebar.expander('Data da compra'):
  data_compra = st.date_input('Selecione a data', (data['Data da Compra'].min(), data['Data da Compra'].max()))

with st.sidebar.expander('Nome do Vendedor'):
  vendedores = st.multiselect('Selecione os vendedores', data['Vendedor'].unique(), data['Vendedor'].unique())

with st.sidebar.expander('Nome do Estado'):
  estados = st.multiselect('Selecione os estados', data['Local da compra'].unique(), data['Local da compra'].unique())

with st.sidebar.expander('Avaliação do produto'):
  avaliacoes = st.slider('Selecione o valor da avaliação', 0, 5, (0, 5))

with st.sidebar.expander('Tipo de pagamento'):
  tipos_pagamento = st.multiselect('Selecione os tipos de pagamentos', data['Tipo de pagamento'].unique(), data['Tipo de pagamento'].unique())

with st.sidebar.expander('Quantidade de parcelas'):
  parcelas = st.slider('Selecione a quantidade de parcelas', 0, 24, (0, 24))

############################## CRIAÇÃO DAS FILTRAGENS ##############################
query = """ 
Produto in @produtos and \
`Categoria do Produto` in @categorias and \
@precos[0] <= Preço <= @precos[1] and \
@fretes[0] <= Frete <= @fretes[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
Vendedor in @vendedores and \
`Local da compra` in @estados and \
@avaliacoes[0] <= `Avaliação da compra` <= @avaliacoes[1] and \
`Tipo de pagamento` in @tipos_pagamento and \
@parcelas[0] <= `Quantidade de parcelas` <= @parcelas[1]
"""
dados_filtrados = data.query(query)
dados_filtrados = dados_filtrados[colunas]

st.markdown(f':blue[**{dados_filtrados.shape[0]}**] linhas e :blue[**{dados_filtrados.shape[1]}**] colunas')
st.dataframe(dados_filtrados)

st.markdown('Escreva um nome para o arquivo')
col1, col2 = st.columns(2)
with col1:
  nome_arquivo = st.text_input('', label_visibility='collapsed', value='dados')
  nome_arquivo+='.csv'
with col2:
  st.download_button('Download .csv', data = converte_csv(dados_filtrados), file_name=nome_arquivo, mime='text/csv', on_click=mensagem_sucesso)