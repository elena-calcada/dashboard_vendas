import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

#Função que formata os números
def format_number(value, prefix = ''):
  for unit in ['', 'mil']:
    if value < 1000:
      return f'{prefix} {value: .2f} {unit}'
    value /= 1000
  return f'{prefix} {value: .2f} milhões'

# Título do Dashboard: https://docs.streamlit.io/develop/api-reference/text/st.title
st.title('DASHBOARD DE VENDAS :shopping_trolley:')

# Url da API
url = 'https://labdados.com/produtos'

############### FILTROS DA API ###############
# Os filtros abaixo já existem na API
# Por isso, serão codificados antes da leitura dos dados
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']
st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
  regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value=True)

if todos_anos:
  ano = ''
else:
  ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao': regiao.lower(), 'ano': ano} # Passar os parâmetros para a response da API

# Pegando dados da API
response = requests.get(url, params=query_string)

# Transformar a response em um JSON e em seguida em um DataFrame
data = pd.DataFrame.from_dict(response.json())

# Alterar o formato da coluna 'Data da Compra' para datetime
data['Data da Compra'] = pd.to_datetime(data['Data da Compra'], format='%d/%m/%Y')

############### FILTROS FORA DA API ###############
# Os filtros abaixo não estão prontos na API
# Por isso, serão codificados depois da leitura e transformação do dataframe
filtro_vendedores = st.sidebar.multiselect('Vendedores', data['Vendedor'].unique())
if filtro_vendedores:
  data = data[data['Vendedor'].isin(filtro_vendedores)] # Tudo agora para baixo também fica atrelado a vendedores

############### TABELAS ###############

# Criar tabla de receitas x estado
receita_estado = data.groupby('Local da compra')[['Preço']].sum()
# Criar tabela de latitde e longitude por estado e vamos unir essa tabela com a receita_estado
local_estado = data.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']]
# Fazendo um mergeando receita_estado e local_estado
data_maps = local_estado.merge(receita_estado, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

###### Receita mensal

# Criar tabela de receita mensal
receita_mensal = data.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].sum().reset_index()
# construir uma coluna com o nome do mês e outra com o ano
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

###### Receita x Categoria

# Criar tabela de receita por categoria do produto
receita_categoria = data.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

###### Qtde de vendas x Estado
qtde_vendas_estado = data.groupby('Local da compra')[['Preço']].count()
qtde_vendas_maps = local_estado.merge(qtde_vendas_estado, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

###### Qtde de vendas mensal
qtde_vendas_mensal = data.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].count().reset_index()
qtde_vendas_mensal['Ano'] = qtde_vendas_mensal['Data da Compra'].dt.year
qtde_vendas_mensal['Mes'] = qtde_vendas_mensal['Data da Compra'].dt.month_name()

###### Quantidade de vendas por categoria
qtde_vendas_categoria = data.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending=False)

###### Tabelas relacionadas a vendedores
vendedores = data.groupby('Vendedor')['Preço'].agg(['sum', 'count'])


############### VISUALIZAÇÕES ###############

# Visualização de métricas: https://docs.streamlit.io/develop/api-reference/data/st.metric
# Visualização de mapa: https://plotly.com/python/scatter-plots-on-maps/
fig_map_receita = px.scatter_geo(
  data_maps,
  lat='lat',
  lon='lon',
  scope='south america',
  size='Preço',
  template='seaborn',
  hover_name='Local da compra',
  hover_data={'lat': False, 'lon': False},
  title='Receita por estado'
)

fig_receita_mensal = px.line(
  receita_mensal,
  x='Mes',
  y='Preço',
  markers=True,
  range_y=(0, receita_mensal.max()),
  color='Ano',
  line_dash='Ano',
  title='Receita mensal'
)
fig_receita_mensal.update_layout(yaxis_title='Receita')

fig_data_maps = px.bar(
  data_maps.head(),
  x='Local da compra',
  y='Preço',
  text_auto=True,
  title='Top estados (receita)'
)
fig_data_maps.update_layout(yaxis_title='Receita')

fig_receita_categoria = px.bar(
  receita_categoria,
  text_auto=True,
  title='Receita por categoria'
)
fig_receita_categoria.update_layout(yaxis_title='Receita')

fig_qtde_vendas_maps = px.scatter_geo(
  qtde_vendas_maps,
  lat='lat',
  lon='lon',
  scope='south america',
  size='Preço',
  template='seaborn',
  hover_name='Local da compra',
  hover_data={'lat': False, 'lon': False},
  title='Receita por estado'
)

fig_qtde_vendas_mensal = px.line(
  qtde_vendas_mensal,
  x='Mes',
  y='Preço',
  markers=True,
  range_y=(0, qtde_vendas_mensal.max()),
  color='Ano',
  line_dash='Ano',
  title='Qtde de vendas mensal'
)
fig_qtde_vendas_mensal.update_layout(yaxis_title='Qtde de vendas')

fig_qtde_vendas_estado = px.bar(
  qtde_vendas_maps.head(),
  x='Local da compra',
  y='Preço',
  text_auto=True,
  title='Top estados (qtde de vendas)'
)
fig_qtde_vendas_estado.update_layout(yaxis_title='Qtde de vendas')

fig_qtde_vendas_categoria = px.bar(
  qtde_vendas_categoria,
  text_auto=True,
  title='Receita por categoria'
)
fig_qtde_vendas_categoria.update_layout(yaxis_title='Qtde de vendas')

# Visualização do satreamlit
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de vendas', 'Vendedores'])

with aba1:
  col1, col2 = st.columns(2)
  with col1:
    st.metric('Receita', format_number(data['Preço'].sum(), 'R$'))
    st.plotly_chart(fig_map_receita, use_container_width=True)
    st.plotly_chart(fig_data_maps, use_container_width=True)
  with col2:
    st.metric('Qtde de vendas', format_number(data.shape[0]))
    st.plotly_chart(fig_receita_mensal, use_container_width=True)
    st.plotly_chart(fig_receita_categoria, use_container_width=True)

with aba2:
  col1, col2 = st.columns(2)
  with col1:
    st.metric('Receita', format_number(data['Preço'].sum(), 'R$'))
    st.plotly_chart(fig_qtde_vendas_maps, use_container_width=True)
    st.plotly_chart(fig_qtde_vendas_estado, use_container_width=True)
  with col2:
    st.metric('Qtde de vendas', format_number(data.shape[0]))
    st.plotly_chart(fig_qtde_vendas_mensal, use_container_width=True)
    st.plotly_chart(fig_qtde_vendas_categoria, use_container_width=True)

with aba3:
  qtde_vendedores = st.number_input('Quantidade de vendedores', 2, 10, 5)
  col1, col2 = st.columns(2)
  with col1:
    st.metric('Receita', format_number(data['Preço'].sum(), 'R$'))
    fig_receita_vendedores = px.bar(
      vendedores[['sum']].sort_values('sum', ascending=False).head(qtde_vendedores),
      x='sum',
      y=vendedores[['sum']].sort_values('sum', ascending=False).head(qtde_vendedores).index,
      text_auto=True,
      title=f'Top {qtde_vendedores} vendedores (receita)'
    )
    st.plotly_chart(fig_receita_vendedores)
  with col2:
    st.metric('Qtde de vendas', format_number(data.shape[0]))
    fig_qtde_vendas_vendedores = px.bar(
      vendedores[['count']].sort_values('count', ascending=False).head(qtde_vendedores),
      x='count',
      y=vendedores[['count']].sort_values('count', ascending=False).head(qtde_vendedores).index,
      text_auto=True,
      title=f'Top {qtde_vendedores} vendedores (qtde_vendas)'
    )
    st.plotly_chart(fig_qtde_vendas_vendedores)



