import os 
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app

from datetime import datetime, date, timedelta
import plotly.express as px
import numpy as np
import pandas as pd
import dash_table

from components import sidebar
from utils import *

df = pd.read_excel(r'Avec - Rel_31 - 2023-08-03T163756.008.xlsx')
df = df.drop(['CPF', 'Celular', 'Telefone'], axis=1)
df['Pacote'] = df['Pacote'].apply(lambda x: 'sim' if pd.isna(x) else 'nao')
df['Profissional'] = df['Profissional'].apply(lambda x: 'Outros/Indef' if pd.isna(x) else x)

clientes_s_visita = ranking_clientes(df)
clientes_mais_recentes = clientes_s_visita.sort_values(by='Tempo Sem Visita (dias)')

####
df_base = pd.read_excel('Analise Carteira_D.ONE_UPDATED.xlsx', sheet_name='base_rec', skiprows= 2)
df_base = df_base[['Profissional', 'Data Comanda', 'Número Comanda','Serviço', 'Categoria', 'Cliente', 'Qtd.', 'Valor', 'Desconto', 'Total']]
df_base.dropna(inplace=True)
df_base['Data Comanda'] = pd.to_datetime(df_base['Data Comanda'])


df = df_base.copy()

# Ordenando o DataFrame pela coluna 'Data Comanda'
df = df.sort_values(by='Data Comanda')

# Agrupando por Cliente para obter as datas da primeira e última visita
grouped = df.groupby('Cliente').agg({'Data Comanda': ['min', 'max']}).reset_index()
grouped.columns = ['Cliente', 'primeira visita', 'última visita']

unique_dates = df.drop_duplicates(['Cliente', 'Data Comanda'])[['Cliente', 'Data Comanda']]
grouped2 = unique_dates.groupby('Cliente')['Data Comanda'].count().reset_index()
grouped2.columns = ['Cliente', 'Visitas']

# Mesclando os dados agrupados de volta ao DataFrame original
df = pd.merge(df, grouped, on='Cliente', how='left')
df = pd.merge(df, grouped2, on='Cliente', how='left')

# Calculando o intervalo de dias entre a última visita e o dia de hoje
df['Ultima Compra'] = (datetime.today() - df['última visita']).dt.days

# Adicionando as colunas de ano-mes, mes e dia da semana
df['ano-mes'] = df['Data Comanda'].dt.to_period('M')
df['ano'] = df['Data Comanda'].dt.year
df['mes'] = df['Data Comanda'].dt.month_name()
df['dia da semana'] = df['Data Comanda'].dt.day_name()


#--- LTV
total_gasto = df.groupby('Cliente')['Total'].sum()

# Calcular a quantidade de vezes que cada cliente realizou uma compra
qtd_compras = df.groupby('Cliente')['Número Comanda'].nunique()

# Calcular a média de tempo entre compras para cada cliente
df['Tempo entre Compras'] = (df['última visita'] - df['primeira visita']).dt.days
media_tempo_entre_compras = df.groupby('Cliente')['Tempo entre Compras'].mean()

# Calcular o LTV para cada cliente
ltv = (total_gasto / qtd_compras) * media_tempo_entre_compras

# Adicionar o LTV calculado ao DataFrame original
df['LTV'] = df['Cliente'].map(ltv)


df['Classificação'] = df.apply(classify, axis=1)
print(df)




###

layout = dbc.Col([
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody(html.Div([
                                dcc.Graph(id='line-chart')
                            ])),
                style={"background-color": "#E8CAB1"}  # Altere aqui a cor de fundo desejada
            )
        ),
        dbc.Col([
            #html.H1("Tempo sem ir ao salão", style = {'color':'black', 'fontSize':'18px', 'textAlign':'center','fontFamily': 'Cambria', 'fontWeight': 'bold'}),
            dbc.Card(
                dbc.CardBody(["Tempo de ausência",
                                dash_table.DataTable(
                                    id='tabela-clientes-s-visita',
                                    columns=[
                                        {'name': 'Cliente', 'id': 'Cliente'},
                                        {'name': 'Profissional', 'id': 'Profissional'},
                                        {'name': 'Dias', 'id': 'Tempo Sem Visita (dias)'},
                                        #{'name': 'Pacote', 'id': 'Data Comanda'},
                                    ],
                                    data=df.to_dict('records'), 
                                    page_size=5,
                                    style_cell={'color': 'black', 'fontSize': '10px', 'textAlign': 'center'},
                                    style_header={
                                            'backgroundColor': '#C4956B',  # Cor de fundo dos nomes das colunas
                                            'fontWeight': 'bold',
                                            'textAlign': 'center',  # Fonte em negrito para os nomes das colunas
                                            #'color': 'white',  # Cor do texto dos nomes das colunas
                                        },
                                    style_data_conditional=[
                                        {
                                            'if': {'row_index': 'odd'},  # Aplicar estilo em linhas ímpares
                                            'backgroundColor': '#F7E8DA'  # Cor de fundo das linhas ímpares
                                        },
                                        {
                                            'if': {'row_index': 'even'},  # Aplicar estilo em linhas pares
                                            'backgroundColor': '#E8CAB1'  # Cor de fundo das linhas pares
                                        },
                                    ],
                                    style_as_list_view=True,
                                ),
                              ]),
                style={"background-color": "#E8CAB1", 'textAlign': 'center', 'fontSize': '16px', 'color':'black'} 
            )
        ]),
        dbc.Col([
            #html.H1("Tempo sem ir ao salão", style = {'color':'black', 'fontSize':'18px', 'textAlign':'center','fontFamily': 'Cambria', 'fontWeight': 'bold'}),
            dbc.Card(
                dbc.CardBody(["Clientes mais recentes",
                                dash_table.DataTable(
                                    id='tabela-clientes-mais_recente',
                                    columns=[
                                        {'name': 'Cliente', 'id': 'Cliente'},
                                        {'name': 'Profissional', 'id': 'Profissional'},
                                        {'name': 'Dias', 'id': 'Tempo Sem Visita (dias)'},
                                        #{'name': 'Pacote', 'id': 'Data Comanda'},
                                    ],
                                    data=df.to_dict('records'), 
                                    page_size=5,
                                    style_cell={'color': 'black', 'fontSize': '10px', 'textAlign': 'center'},
                                    style_header={
                                            'backgroundColor': '#C4956B',  # Cor de fundo dos nomes das colunas
                                            'fontWeight': 'bold',
                                            'textAlign': 'center',  # Fonte em negrito para os nomes das colunas
                                            #'color': 'white',  # Cor do texto dos nomes das colunas
                                        },
                                    style_data_conditional=[
                                        {
                                            'if': {'row_index': 'odd'},  # Aplicar estilo em linhas ímpares
                                            'backgroundColor': '#F7E8DA'  # Cor de fundo das linhas ímpares
                                        },
                                        {
                                            'if': {'row_index': 'even'},  # Aplicar estilo em linhas pares
                                            'backgroundColor': '#E8CAB1'  # Cor de fundo das linhas pares
                                        },
                                    ],
                                    style_as_list_view=True,
                                ),
                              ]),
                style={"background-color": "#E8CAB1", 'textAlign': 'center', 'fontSize': '16px', 'color':'black'} 
            )
        ]),
    ])
])

@app.callback(
    Output('tabela-clientes-s-visita', 'data'),
    Input('filtro-classe-cliente', 'value')
)
def atualizar_tabela_por_classe(value):
    if value == 'Todos':
        return clientes_s_visita.to_dict('records')
    else:
        filtered_df = clientes_s_visita[clientes_s_visita['classe'] == value]
        return filtered_df.to_dict('records')
    
@app.callback(
    Output('tabela-clientes-mais_recente', 'data'),
    Input('filtro-classe-cliente', 'value')
)
def atualizar_tabela_por_classe(value):
    if value == 'Todos':
        return clientes_mais_recentes.to_dict('records')
    else:
        filtered_df = clientes_mais_recentes[clientes_mais_recentes['classe'] == value]
        return filtered_df.to_dict('records')
    

@app.callback(
    Output('line-chart', 'figure'),
    Input('input-dropdown', 'value')  # Adicione aqui os inputs que deseja utilizar
)
def update_line_chart(ano):  # Adicione os parâmetros que deseja receber
    ano = datetime.now().year
    df_ano = filter_date(df.copy(), f'{ano}-01-01', f'{ano}-12-31')
    df_ano = df_ano.groupby(['ano', 'mes'])[['dia da semana']].count()
    df_ano = df_ano.rename(columns={'dia da semana': f'{ano}'})
    df_ano.reset_index(inplace=True)
    df_ano = df_ano.rename(columns={'mes': 'Mes'})

    ano_anterior = ano - 1
    df_ano_anterior = filter_date(df.copy(), f'{ano_anterior}-01-01', f'{ano_anterior}-12-31')
    df_ano_anterior = df_ano_anterior.groupby(['ano', 'mes'])[['dia da semana']].count()
    df_ano_anterior = df_ano_anterior.rename(columns={'dia da semana': f'{ano_anterior}'})
    df_ano_anterior.reset_index(inplace=True)

    comp = pd.concat([df_ano, df_ano_anterior], axis=1)
    comp = comp[['mes', f'{ano}', f'{ano_anterior}']]

    fig_comparacao = px.line(comp, x='mes', y=[f'{ano}', f'{ano_anterior}'])

    colors = ['#C4956B', '#F7E8DA']  # Defina as cores das linhas aqui
    for i, color in enumerate(colors):
        fig_comparacao.update_traces(
            line=dict(color=color),
            selector=dict(name=f'{ano}' if i == 0 else f'{ano_anterior}')
        )

    fig_comparacao.update_layout(
        xaxis_title=None,
        yaxis_title='Quantidade de clientes',
        template='none',  # Define o tema escuro
        plot_bgcolor='rgba(0,0,0,0)',  # Define a cor de fundo do gráfico (transparente)
        paper_bgcolor='rgba(0,0,0,0)'  # Define a cor de fundo do papel (transparente)
    )

    fig_comparacao.update_xaxes(gridwidth=0.2)  # Define a espessura das linhas de grade do eixo X
    fig_comparacao.update_yaxes(gridwidth=0.2)

    return fig_comparacao