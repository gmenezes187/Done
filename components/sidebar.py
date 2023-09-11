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

from components import dashboards

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
                id='filtro-classe-cliente',
                options=[
                    {'label': 'C1', 'value': 'c1'},
                    {'label': 'C2', 'value': 'c2'},
                    {'label': 'C3', 'value': 'c3'},
                    {'label': 'C4', 'value': 'c4'}
                ],
                value='c1',  # Valor inicial do filtro
                clearable=False,
                placeholder='Selecione a classe',
                style={
                    'color': 'black',  # Define a cor da escrita como preto
                    'text-align': 'center',
                    'fontSize':'12px'  # Centraliza o texto dentro do componente
                }  # Impede que o filtro seja desmarcado
                        )
], )