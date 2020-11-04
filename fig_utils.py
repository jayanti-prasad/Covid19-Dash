import plotly.express as px
from plotly.subplots import make_subplots
from data_utils import get_district_data,get_data_world,get_data_india
from datetime import datetime,date 
import numpy as np

def update_dropdown(name):
    if name == 'World':
         return [{'label': i, 'value': i} for i in countries]
    else:
         return [{'label': i, 'value': i} for i in states]

def transform (X, plot_style, rolling_type, rolling_size):
    X = X.astype(float)
    if plot_style == 'Log10':
       X =  np.log10(X)
    if rolling_type == 'Median':
       X = X.rolling(rolling_size).median()
    if rolling_type == 'Mean':
       X =  X.rolling(rolling_size).mean()

    return X


def get_figure (df, region, title, mode, plot_style, rolling_type, rolling_size):

    df['removed'] = df['Recovered'].add (df['Deaths'],fill_value=0)
    df['Active']  = df['Confirmed'].subtract (df['removed'],fill_value=0)

    X = df['Confirmed']
    Y = df['Recovered']
    Z = df['Deaths']
    title = region + " (Total)"
    x, y, z = X, Y, Z

    if mode == 'Daily':
       x = X.diff(periods=1).iloc[1:]
       y = Y.diff(periods=1).iloc[1:]
       z = Z.diff(periods=1).iloc[1:]
       title = region + " (Daily)"

    elif mode == 'Active':
       x = df['Active']
       y = df['Active']
       z = Z
       title = region + " (Active)"
    else:
       x, y, z = X, Y, Z
       title = region + " (Cumulative)"

    x = transform (x, plot_style, rolling_type, rolling_size)
    y = transform (y, plot_style, rolling_type, rolling_size)
    z = transform (z, plot_style, rolling_type, rolling_size)

    fig1 = px.scatter(x)
    fig2 = px.scatter(y)
    fig3 = px.scatter(z)

    trace1 = fig1['data'][0]
    trace2 = fig2['data'][0]
    trace3 = fig3['data'][0]

    fig = make_subplots(rows=2, cols=1,shared_xaxes=False,\
      horizontal_spacing=0.1, vertical_spacing=0.05,\
     y_title=region,subplot_titles=([title]))

    fig.add_trace(trace1, row=1, col=1)
    fig.add_trace(trace2, row=1, col=1)
    fig.add_trace(trace3, row=2, col=1)
 
    fig.data[0].update(mode='markers+lines')
    fig.data[1].update(mode='markers+lines')
    fig.data[2].update(mode='markers+lines')

    fig['data'][0]['marker']['color']="blue"
    fig['data'][1]['marker']['color']="green"
    fig['data'][2]['marker']['color']="red"

    return fig


if __name__ == "__main__":

    dF1, countries = get_data_world()
    dF2, df3, STATES  = get_data_india()

    countries = ["Total"] + countries
    states = STATES.keys()

    start_date = datetime.strptime('2020-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    end_date = date.today()

    for geography in ['World','India']:
       regions =  update_dropdown(geography)
 
       for region in regions:
           if geography == 'World':
              df = dF1[dF1['country'] == region['value']]
              print(geography, region, df.shape, df.columns)
           else :
              for state in states:
                  for district in STATES[state]:
                      df = get_district_data (df3,state,district)                  
                      print(geography, region['value'], state, district, df.shape, df.columns)
 
