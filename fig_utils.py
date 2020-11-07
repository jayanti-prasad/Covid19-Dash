import plotly
import plotly.express as px
from plotly.subplots import make_subplots
#import plotly.graph_objects as go
from datetime import datetime,date
from plotly.offline import plot
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

    date = df['date'].to_list()
    X = df['Confirmed']
    Y = df['Recovered']
    Z = df['Deaths']
    x, y, z = X,Y, Z

    L1,L2,L3='Confirmed','Recovered','Deaths'

    if mode == 'Daily':
       x = X.diff(periods=1).iloc[1:]
       y = Y.diff(periods=1).iloc[1:]
       z = Z.diff(periods=1).iloc[1:]
       title = title + " (Daily)"

    elif mode == 'Active':
       x = df['Active']
       y = df['Active']
       z = Z
       title = title + " (Active)"
       L1,L2='','Active'
    else:
       x, y, z = X, Y, Z
       title = title + " (Cumulative)"

    x = transform (x, plot_style, rolling_type, rolling_size)
    y = transform (y, plot_style, rolling_type, rolling_size)
    z = transform (z, plot_style, rolling_type, rolling_size)

    fig1 = px.scatter(x=x.index, y=x.values)
    fig2 = px.scatter(x=y.index, y=y.values)
    fig3 = px.scatter(x=z.index, y=z.values)

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

    fig['data'][0]['showlegend']=True
    fig['data'][1]['showlegend']=True
    fig['data'][2]['showlegend']=True

    fig['data'][0]['name']=L1
    fig['data'][1]['name']=L2
    fig['data'][2]['name']=L3


    return fig

def get_bar_chart (df, name):
    df = df[df[name] !='Total']
    x = df[name].to_list()
    L1,L2,L3='Confirmed','Recovered','Deaths'

    fig1 = px.bar(x=x, y=df['confirmed'])
    fig2 = px.bar(x=x, y=df['recovered'])
    fig3 = px.bar(x=x, y=df['deaths'])

    trace1 = fig1['data'][0]
    trace2 = fig2['data'][0]
    trace3 = fig3['data'][0]
  
    if name == 'country':
       title = 'World'
    else:
       title = 'India'
  

    fig = make_subplots(rows=2, cols=1,shared_xaxes=False,\
      horizontal_spacing=0.1, vertical_spacing=0.05,y_title='Covid-19',subplot_titles=([title]))

    fig.add_trace(trace1, row=1, col=1)
    fig.add_trace(trace2, row=1, col=1)
    fig.add_trace(trace3, row=2, col=1)

    fig['data'][0]['marker']['color']="blue"
    fig['data'][1]['marker']['color']="green"
    fig['data'][2]['marker']['color']="red"

    fig['data'][0]['showlegend']=True
    fig['data'][1]['showlegend']=True
    fig['data'][2]['showlegend']=True

    fig['data'][0]['name']=L1
    fig['data'][1]['name']=L2
    fig['data'][2]['name']=L3

    return fig

def  get_pie(df, name):

    if name == 'World':
       title = 'World [Covid-19]'
    else:
       title = 'India [Covid-19]' 

    TAG = {'World':'country','India':'State'}

    """
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]],\
       x_title=title,subplot_titles=(['Confirmed','Deaths'])) 

   
    fig.add_trace(go.Pie(values=df['confirmed'].to_list(),labels=df[TAG[name]].to_list(),domain=dict(x=[0, 0.5]),
       name="Confirmed"), row=1, col=1)

    fig.add_trace(go.Pie(values=df['deaths'].to_list(),labels=df[TAG[name]].to_list(),
       domain=dict(x=[0.5, 1.0]), name="Deaths"), row=1, col=2)
    """
    fig = px.pie(df, values='confirmed', names=TAG[name], title=title)

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

