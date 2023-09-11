import pandas as pd
from datetime import datetime

def ranking_clientes(df):
    df['Data Comanda'] = pd.to_datetime(df['Data Comanda'])

    today = datetime.today()
    df_recentes = df[df['Data Comanda'] <= today]

    # Encontrando o índice do registro mais recente para cada cliente
    idx_recentes = df_recentes.groupby('Cliente')['Data Comanda'].idxmax()

    # Criando um novo DataFrame com os registros mais recentes de cada cliente
    df_recentes = df_recentes.loc[idx_recentes]

    # Calculando o tempo desde a última visita de cada cliente
    df_recentes['Tempo Sem Visita (dias)'] = (today - df_recentes['Data Comanda']).dt.days

    # Criando um DataFrame com o ranking dos clientes pelo tempo sem visita
    ranking_clientes = df_recentes.sort_values(by='Tempo Sem Visita (dias)', ascending=False).reset_index(drop=True)
    ranking_clientes = ranking_clientes[['Profissional', 'Cliente', 'Tempo Sem Visita (dias)', 'Data Comanda']]

    def categorize_classe(tempo_sem_visita):
        if tempo_sem_visita <= 30:
            return 'c1'
        elif 30 < tempo_sem_visita <= 90:
            return 'c2'
        elif 90 < tempo_sem_visita <= 180:
            return 'c3'
        else:
            return 'c4'

    # Adicionando a coluna "classe" ao DataFrame ranking_clientes
    ranking_clientes['classe'] = ranking_clientes['Tempo Sem Visita (dias)'].apply(categorize_classe)
    return ranking_clientes

###
def filter_date(df, begin_date, end_date):
    df['Data Comanda'] = pd.to_datetime(df['Data Comanda'])
    df.set_index(['Data Comanda'], inplace=True)
    df = df.loc[begin_date:end_date]
    df.reset_index(inplace = True)
    return df

def classify(row):
    if 0 <= row['Ultima Compra'] <= 90 and 4 <= row['Visitas'] <= 12 and row['LTV'] >= 1100:
        return 'Campeões (High Profile)'
    elif 0 <= row['Ultima Compra'] <= 150 and 4 <= row['Visitas'] <= 12 and row['LTV'] >= 1100:
        return 'Clientes fiéis'
    elif 0 <= row['Ultima Compra'] <= 90 and 2 <= row['Visitas'] <= 3 and row['LTV'] >= 180:
        return 'FIéis em potencial'
    elif 0 <= row['Ultima Compra'] <= 90 and row['Visitas'] == 1 and 181 <= row['LTV'] <= 2250:
        return 'Novos clientes'
    elif 0 <= row['Ultima Compra'] <= 90 and row['Visitas'] == 1 and 0 <= row['LTV'] <= 180:
        return 'Promessas'
    elif 91 <= row['Ultima Compra'] <= 150 and (1 <= row['Visitas'] <= 12 or row['Visitas'] > 12) and (0 <= row['LTV'] <= 2250 or row['LTV'] > 2250):
        return 'Clientes precisando de atenção'
    elif 151 <= row['Ultima Compra'] <= 360 and (1 <= row['Visitas'] <= 12 or row['Visitas'] > 12) and row['LTV'] >= 650:
        return 'Em risco_High_LTV'
    elif 151 <= row['Ultima Compra'] <= 360 and (1 <= row['Visitas'] <= 12 or row['Visitas'] > 12) and (0 <= row['LTV'] <= 650):
        return 'Em risco_Low_LTV'
    elif 151 <= row['Ultima Compra'] <= 360 and (1 <= row['Visitas'] <= 3) and (0 <= row['LTV'] <= 650):
        return 'Hibernando'
    elif 181 <= row['Ultima Compra'] <= 360 and row['Visitas'] == 1 and (0 <= row['LTV'] <= 180):
        return 'Perdidos'
    else:
        return 'Outra classificação'