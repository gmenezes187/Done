import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

from flask import Flask
from dash.dependencies import Input, Output

from dash import Dash, html, dcc
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from app import *
from components import sidebar, extratos, dashboards, dashboard_geral

content = html.Div(id="page-content")

app.layout = dbc.Container(children=[
    dbc.Row([
        dbc.Col([
            dcc.Location(id = 'url'),
            sidebar.layout 
        ], md = 2, style={
            'background-color': '#E8CAB1',
            'height':'1080px'}),
        dbc.Col([
            content 
        ], md = 10, style={
            'background-color': '#F7E8DA',
            'height':'1080px'}),
    ])


], fluid=True)

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def render_page(pathname):
    if pathname == '/' or pathname =='/dashboard_profissional': 
        return dashboards.layout
    elif  pathname =='/dashboard_geral': 
        return dashboard_geral.layout
    
    if pathname == '/extratos':
        return extratos.layout


if __name__ == '__main__':
    app.run_server(port = 8051, debug = True)