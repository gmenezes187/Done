import pandas as pd
from datetime import datetime

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