import os 
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app

from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go

import numpy as np
import pandas as pd
import dash_table

from components import sidebar
from utils import *

df_base = pd.read_excel('Analise Carteira_D.ONE_UPDATED.xlsx', sheet_name='base_rec', skiprows= 2)
df_base = df_base[['Profissional', 'Data Comanda', 'Número Comanda','Serviço', 'Categoria', 'Cliente', 'Qtd.', 'Valor', 'Desconto', 'Total']]
df_base.dropna(inplace=True)
df_base['Data Comanda'] = pd.to_datetime(df_base['Data Comanda'])


df = df_base.copy()
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
qtd_compras = df.groupby('Cliente')['Número Comanda'].nunique()
df['Tempo entre Compras'] = (df['última visita'] - df['primeira visita']).dt.days
media_tempo_entre_compras = df.groupby('Cliente')['Tempo entre Compras'].mean()
ltv = total_gasto#/qtd_compras
df['LTV'] = df['Cliente'].map(ltv)

df['Classificação'] = df.apply(classify, axis=1)

###

layout = dbc.Col([
    dbc.Row([
        html.H1("Geral", style={
        'textAlign':'left',
        'color':'#C4956B',
        'fontSize':'30px',
        'font-weight': 'bold',
        }),
    ]),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody(html.Div([
                                dcc.Graph(id='historico_by_classify_geral', config={'displayModeBar': False})
                            ])),
                style={"background-color": "#E8CAB1", "height": "auto", "margin": "0"}  
            )
        ),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody(html.Div([
                                dcc.Graph(id='evolucao_geral', config={'displayModeBar': False})
                            ])),
                style={"background-color": "#E8CAB1", "height": "auto", "margin": "0"}  
            )
        ),
    ]),
    html.Br(),

    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody(html.Div([
                                dcc.Graph(id='comparacao_categoria_geral', config={'displayModeBar': False})
                            ])),
                style={"background-color": "#E8CAB1", "height": "auto", "margin": "0"}  
            )
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody(html.Div([
                                dcc.Graph(id='comparacao_servico_geral', config={'displayModeBar': False})
                            ])),
                style={"background-color": "#E8CAB1", "height": "auto", "margin": "0"}  
            )
        )
    ])
])


@app.callback(
    Output('historico_by_classify_geral', 'figure'),
    Input('input-dropdown-date-range', 'start_date'),
    Input('input-dropdown-date-range', 'end_date') 
)
def update_line_chart(begin_date, end_date):
    df2 = filter_date(df.copy(), begin_date, end_date )
    graf1 = df2.groupby(['ano-mes', 'Classificação'])[['Total']].sum().reset_index()

    # Transforme a coluna 'ano-mes' em um objeto de data
    graf1['data'] = graf1['ano-mes'].apply(lambda x: str(x) + '-01')
    graf1['data'] = pd.to_datetime(graf1['data'])

    cores_personalizadas = ['#FF5733', '#33FF57', '#3366FF', '#FF33A1']
    ordem_categorias = ['Campeões (High Profile)', 'Clientes fiéis', 'Clientes precisando de atenção', 'Em risco_High_LTV', 'Em risco_Low_LTV', 'FIéis em potencial', 'Outra classificação']

    fig = px.bar(graf1, x='data', y='Total', color='Classificação',
                title='Total arrecadado por Classificação ao longo do Tempo',
                labels={'Total': 'Total Arrecadado'},
                color_discrete_sequence=cores_personalizadas,
                category_orders={"Classificação": ordem_categorias})

    fig.update_traces(marker_line_width=0.5, marker_line_color='black', selector=dict(type='bar'))
    fig.update_layout(barmode='relative', template = 'plotly_white',
                    margin=dict(t=20, r=0, b=0, l=0),
                    plot_bgcolor='rgba(0,0,0,0)',  # Define a cor de fundo do gráfico (transparente)
                    paper_bgcolor='rgba(0,0,0,0)') # Define a cor de fundo do papel (transparente))
    fig.update_xaxes(title=None, tickformat='%Y-%m')
    fig.update_yaxes(title='Receita', gridwidth=0.1)
    fig.update_layout(title=None)
    fig.update_layout(autosize=True, height=200)

    return fig

@app.callback(
    Output('comparacao_categoria_geral', 'figure'),
    Input('input-dropdown-legend', 'value'),
    Input('input-dropdown-date-range', 'start_date'),
    Input('input-dropdown-date-range', 'end_date')
)
def update_graph2(legend, begin_date, end_date):
    receita_por_categoria = filter_date(df.copy(), begin_date, end_date )
    if legend == 'Receita':
        receita_por_categoria  = receita_por_categoria.groupby(['Categoria'])['Total'].sum().reset_index()
    elif legend == 'Quantidade':
            receita_por_categoria  = receita_por_categoria.groupby(['Categoria'])['Total'].count().reset_index()

    receita_por_categoria.columns = ['Categoria', f'{legend}']
    
    fig = px.bar(receita_por_categoria, x='Categoria', y=f'{legend}',
                labels={f'{legend}': f'{legend} Total'}, barmode='group')

    fig.update_traces(marker_line_width=0.5, marker_line_color='black', selector=dict(type='bar'))
    fig.update_layout(template = 'plotly_white',
                    margin=dict(t=20, r=0, b=0, l=0),
                    plot_bgcolor='rgba(0,0,0,0)',  # Define a cor de fundo do gráfico (transparente)
                    paper_bgcolor='rgba(0,0,0,0)') # Define a cor de fundo do papel (transparente))
    fig.update_layout(autosize=True, height=300)
    fig.update_xaxes(tickangle=30)


    return fig

@app.callback(
    Output('comparacao_servico_geral', 'figure'),
    Input('input-dropdown-profissional', 'value'),
    Input('input-dropdown-legend', 'value'),
    Input('input-dropdown-date-range', 'start_date'),
    Input('input-dropdown-date-range', 'end_date')
)
def update_graph3(Profissional, legend, begin_date, end_date):
    receita_por_categoria = filter_date(df.copy(), begin_date, end_date )
    if legend == 'Receita':
        receita_por_categoria  = receita_por_categoria.groupby(['Profissional','Serviço'])['Total'].sum().reset_index()
    elif legend == 'Quantidade':
            receita_por_categoria  = receita_por_categoria.groupby(['Profissional','Serviço'])['Total'].count().reset_index()

    receita_por_categoria.columns = ['Profissional','Serviço', f'{legend}']

    total_por_categoria = receita_por_categoria.groupby('Serviço')[f'{legend}'].sum().reset_index()
    total_por_categoria['Profissional'] = 'Total'
    receita_por_categoria = pd.concat([receita_por_categoria, total_por_categoria], ignore_index=True)


    receita_por_categoria = receita_por_categoria[(receita_por_categoria['Profissional'] == Profissional)]

    fig = px.bar(receita_por_categoria, x='Serviço', y=f'{legend}', color='Profissional',
                labels={f'{legend}': f'{legend}'}, barmode='group')

    fig.update_traces(marker_line_width=0.5, marker_line_color='black', selector=dict(type='bar'))
    fig.update_layout(barmode='relative', template = 'plotly_white',
                    margin=dict(t=20, r=0, b=0, l=0),
                    plot_bgcolor='rgba(0,0,0,0)',  # Define a cor de fundo do gráfico (transparente)
                    paper_bgcolor='rgba(0,0,0,0)') # Define a cor de fundo do papel (transparente))
    fig.update_layout(autosize=True, height=300)
    fig.update_xaxes(tickangle=30)


    return fig

@app.callback(
    Output('evolucao_geral', 'figure'),
    Input('input-dropdown-legend', 'value'),
    Input('input-dropdown-date-range', 'start_date'),
    Input('input-dropdown-date-range', 'end_date')
)
def update_graph4(legend, begin_date, end_date):
    receita_por_categoria = filter_date(df.copy(), begin_date, end_date )
    if legend == 'Receita':
        receita_por_categoria  = receita_por_categoria.groupby(['Data Comanda'])['Total'].sum().reset_index()#.set_index('Categoria').T
    elif legend == 'Quantidade':
        receita_por_categoria  = receita_por_categoria.groupby(['Data Comanda'])['Total'].count().reset_index()#.set_index('Categoria').T
    receita_por_categoria.columns = ['Data', f'{legend}']
    receita_por_categoria[f'{legend} Acumulada'] = receita_por_categoria[f'{legend}'].cumsum()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=receita_por_categoria['Data'],
        y=receita_por_categoria[f'{legend}'],
        name=f'{legend} Diária',
        marker_color='grey',
        showlegend=False  # Remove a legenda para este traço
    ))

    # Adicione a linha para a receita acumulada no eixo direito sem legenda
    fig.add_trace(go.Scatter(
        x=receita_por_categoria['Data'],
        y=receita_por_categoria[f'{legend} Acumulada'],
        name=f'{legend} Acumulada',
        yaxis='y2',  # Use o eixo secundário (y2)
        line=dict(color='black'),
        showlegend=False  # Remove a legenda para este traço
    ))

    # Atualize os rótulos dos eixos
    fig.update_layout(
                        xaxis=dict(title='Data'),
                        yaxis=dict(title=f'{legend} Diária', color='black'),
                        yaxis2=dict(title=f'{legend} Acumulada', color='gray', overlaying='y', side='right'),
    )



    fig.update_traces(marker_line_width=0.5, marker_line_color='black', selector=dict(type='bar'))
    fig.update_layout(barmode='relative', template = 'plotly_white',
                    margin=dict(t=20, r=0, b=0, l=0),
                    plot_bgcolor='rgba(0,0,0,0)',  # Define a cor de fundo do gráfico (transparente)
                    paper_bgcolor='rgba(0,0,0,0)') # Define a cor de fundo do papel (transparente))
    fig.update_layout(autosize=True, height=300)
    #fig.update_xaxes(tickangle=30)
    return fig