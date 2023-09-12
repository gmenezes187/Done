import os 
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from app import app
from components.dashboards import *
from datetime import datetime, date, timedelta
import plotly.express as px
import numpy as np
import pandas as pd

from components import dashboards

profissionais = pd.unique(df['Profissional'])
profissionais = np.sort(profissionais)

layout = dbc.Col([
    html.H1("D.One", style={
        'textAlign':'center',
        'color':'#C4956B',
    }),
    html.P("Análise de performance", style={
        'textAlign':'center',
        'color':'black',
    }),
    html.Hr(style={
        'color':'black'
    }),

    dcc.Dropdown(
        id='input-dropdown-profissional',
        options=[
            {'label': profissional, 'value': profissional} for profissional in profissionais
        ],
        value=profissionais[0],  # Valor inicial do filtro (primeiro profissional da lista)
        clearable=False,
        placeholder='Selecione o profissional',
        style={
            'color': 'black',  # Define a cor da escrita como preto
            'text-align': 'center',
            'fontSize': '12px'  # Centraliza o texto dentro do componente
        }
    ),
    dcc.Dropdown(
        id='input-dropdown-legend',
        options=[{'label': 'Quantidade', 'value': 'Quantidade'},
                 {'label': 'Receita', 'value': 'Receita'}],
        value='Receita' ,
        clearable=False,
        placeholder='Selecione a legenda',
        style={
            'color': 'black',  # Define a cor da escrita como preto
            'text-align': 'center',
            'fontSize': '12px'  # Centraliza o texto dentro do componente
        }
    ),
    
    dcc.DatePickerRange(
        id='input-dropdown-date-range',
        start_date='2023-01-01',
        end_date=datetime.now().strftime('%Y-%m-%d')
    ),
])