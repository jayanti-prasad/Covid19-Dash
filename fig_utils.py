import numpy as np
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots

def plot_time_seris(df, mode, scale, title, style):
    fig = make_subplots(rows=2, cols=1,shared_xaxes=False,\
      horizontal_spacing=0.1, vertical_spacing=0.05,\
      subplot_titles=([title]))
    if mode == 'Active':
       df['removed'] = df['recovered'].add (df['deaths'],fill_value=0)
       df['active']  = df['confirmed'].subtract (df['removed'],fill_value=0)
       columns=['active','deaths']
       rows=[1,2]
       colors=['blue','red']
    else:
       columns=['confirmed','recovered','deaths']
       rows=[1,1,2]
       colors=['blue','green','red']
 
    count = 0 
    for column in columns:
       X = df[column] 
       if mode == 'Daily':
          X = X.diff(periods=1).iloc[1:]
       if scale == 'log':
          X = X.astype(float)
          X = np.log10(X)  
       fig1 = px.scatter(x=X.index, y=X.values)
       fig1['data'][0]['marker']['color']=colors[count]
       fig1['data'][0]['name']=columns[count]
       fig1['data'][0]['showlegend']=True
       fig1.data[0].update(mode=style)
       trace = fig1['data'][0]
       fig.add_trace(trace, row=rows[count], col=1)
       count +=1

    return fig 


def plot_bar_chart(df, name,scale, title):
    fig = make_subplots(rows=2, cols=1,shared_xaxes=False,\
      horizontal_spacing=0.1, vertical_spacing=0.05,\
      subplot_titles=([title]))
    columns=['confirmed','recovered','deaths']
    rows=[1,1,2]
    colors=['blue','green','red']
    df.index = df[name].to_list()
    count = 0
    for column in columns:
       X = df.iloc[:-1][column]
       if scale == 'log':
          X = X.astype(float)
          X = np.log10(X)
       fig1 = px.bar(x=X.index, y=X.values)
       fig1['data'][0]['marker']['color']=colors[count]
       fig1['data'][0]['name']=columns[count]
       fig1['data'][0]['showlegend']=True
       trace = fig1['data'][0]
       fig.add_trace(trace, row=rows[count], col=1)
       count +=1

    return fig


def plot_pi_plot(df,name,title):
   import plotly.graph_objects as go
   labels = df[name].to_list() 
   fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]],\
      x_title=title,subplot_titles=(['Confirmed','Deaths']))
   fig.add_trace(go.Pie(values=df['confirmed'].to_list(),labels=labels,domain=dict(x=[0, 0.5]),
       name="Confirmed"), row=1, col=1)

   fig.add_trace(go.Pie(values=df['deaths'].to_list(),labels=labels,
      domain=dict(x=[0.5, 1.0]), name="Deaths"), row=1, col=2)
   return fig 

def get_ts_plot(args, DL):
    if args.geography == 'World':
       if args.region is not None and args.region in DL.countries:
          df = DL.get_country_data(args.region)
          title = args.region
       else:
          df = DL.get_world_data()
          title = 'World'
          df['date'] = df.index 
    if args.geography == 'India':
       if args.region is not None and args.region in DL.states:
          if args.sub_region is not None and args.sub_region in DL.STATES[args.region] :
             title = args.sub_region + " [ " + args.region + " ] "
             df = DL.get_district_data (args.region, args.sub_region)
          else:
             df = DL.get_state_data (args.region)
             title = args.region 
       else:
          df = DL.get_country_data('India')
          title = 'India'

    mask = (df['date'] > args.start_date) & (df['date'] <= args.end_date)
    df = df.loc[mask]
 
    for col in ['confirmed','recovered','deaths']:
       if args.rolling_type == 'Median':
          df[col] = df[col].rolling(args.rolling_size).median()
       if args.rolling_type == 'Mean':
          df[col] =  df[col].rolling(args.rolling_size).mean()

    return plot_time_seris(df,args.tstype,args.scale,title, 'markers+lines')

def get_bar_plot(args, DL):
    if args.geography == 'World':
       df = DL.get_current_data('World','country',30)
       fig = plot_bar_chart(df,'country',args.scale, 'World')
       return fig 
    else:
       if args.region is not None and args.region in DL.states:
          df = DL.get_current_data(args.region,'district',30)
          fig = plot_bar_chart(df,'district',args.scale, args.region)
          return fig 
       else:
          df = DL.get_current_data('India','state',30) 
          fig = plot_bar_chart(df,'state',args.scale, 'India')
          return fig 

  
def get_pie_plot(args, DL):
    if args.geography == 'World':
       df = DL.get_current_data('World','country',30)
       fig = plot_pi_plot(df,'country','World') 
       return fig
    else:
       if args.region is not None and args.region in DL.states:
          df = DL.get_current_data(args.region,'district',30)
          fig = plot_pi_plot(df,'district',args.region) 
          return fig
       else:
          df = DL.get_current_data('India','state',30)
          fig = plot_pi_plot(df,'state','India') 
          return fig
 
