import os
import time
import numpy 
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import date, datetime
from data_utils import collapsed_data
from data_utils import get_district_data,get_data_world,get_data_india,rename_columns
from fig_utils import get_figure, get_bar_chart,get_pie

numpy.seterr(divide = 'ignore') 

os.environ["TZ"] = "Asia/Kolkata"
time.tzset()

dF1, countries = get_data_world()
dF2, df3, STATES  = get_data_india()

countries = ["Total"] + countries
states = STATES.keys()

start_date = datetime.strptime('2020-01-01', '%Y-%m-%d')
end_date = date.today()

external_stylesheets = ['bWLwgP.css']
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.title = 'Jayanti Prasad\'s Covid-19 Dashboard'

app.layout = html.Div([
    html.H1(children='Covid-19',style={'text-align': 'left'}),
    html.Table(
    [
      html.Tr([
      html.Td(
         dcc.RadioItems(
            id='geography',
            options=[{'label': i, 'value': i} for i in ['World','India']],
            value='India',
            labelStyle={'display': 'inline-block'}),
             style={'width': '100%', 'display': 'inline-block'}
      ),

      html.Td(
         dcc.DatePickerRange(
                id='date-picker-range',
                start_date_placeholder_text="Start Date",
                end_date_placeholder_text="End Date",
                start_date=start_date,
                end_date=end_date,
       style={'width': '100%', 'display': 'inline-block'})),

       html.Td(),

      ],style={'background-color':'#008B8B'}),
      html.Tr([
          html.Td(
             dcc.Dropdown(
             id='regions',value='Total'
             ),style={'width': '100%', 'display': 'inline-block'}),

          html.Td(
            dcc.RadioItems(
                id='mode',
                options=[{'label': i, 'value': i} for i in ['Cumulative','Daily','Active','Bar','Pie']],
                value='Cumulative',
                labelStyle={'display': 'inline-block'}),
          ),
          html.Td(
             dcc.RadioItems(
                id='plot-style',
                options=[{'label': i, 'value': i} for i in ['Linear','Log10']],
                value='Linear',
                labelStyle={'display': 'inline-block'}),
          ),

      ],style={'background-color':'#BDB76B'}),

    html.Tr([
        html.Td(
          dcc.Dropdown(
             id='districts',value='Total',
             ),style={'width': '100%', 'display': 'inline-block'}


        ),
        html.Td(
          dcc.Dropdown(
             id='rolling_type',
             options=[{'label': "Rolling " + i, 'value': i} for i in ['Mean','Median']],
             value='Mean',
          ),
        ),
        html.Td(
           dcc.Dropdown(
             id='rolling_size',
             options=[{'label': str(i) + " Days", 'value': i} for i in [1,2,5,7,10,15]],
             value=1,
          ),
        ),

    ],style={'background-color':'#FFDEAD'}),
    html.Tr([
       html.Td("Data Source",style={'width': '100%', 'display': 'inline-block'}),
       html.Td("https://github.com/CSSEGISandData/COVID-19"),
       html.Td("https://api.covid19india.org/"),
    ],style={'background-color':'#F8C471'}),

    ],style={'width':'100%','float':'center'}
    ),

    html.Div([

    html.Div([ html.Div(id='output-container-date-picker'),]),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Hr(),
    dcc.Graph(id='indicator-graphic'),
   ]),
   html.H5(children='(c) Jayanti Prasad 2020 ',style={'text-align': 'center'})

])

@app.callback(
    dash.dependencies.Output('districts', 'options'),
    [dash.dependencies.Input('regions', 'value')]
)
def update_dropdown_distrct(name):
    if name in STATES.keys():
       return [{'label': i, 'value': i} for i in STATES[name]]
    else:
       return [{'label': "Default", 'value': 'TT'}]


@app.callback(
    dash.dependencies.Output('regions', 'options'),
    [dash.dependencies.Input('geography', 'value')]
)
def update_dropdown(name):
    if name == 'World':
         return [{'label': i, 'value': i} for i in countries]
    else:
         return [{'label': i, 'value': i} for i in states]


@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('geography', 'value'),
    Input('regions', 'value'),
    Input('districts', 'value'),
    Input('rolling_type', 'value'),
    Input('rolling_size', 'value'),
    Input(component_id='date-picker-range', component_property='start_date'),
    Input(component_id='date-picker-range', component_property='end_date'),
    Input('mode', 'value'),Input('plot-style', 'value')])

def update_graph(geography,region,district,rolling_type,rolling_size,start_date,end_date,mode,plot_style):


    rolling_size = int(rolling_size)

    title = geography

    if geography == 'World':
       if region in countries[1:]:
          df = dF1[dF1['country'] == region]
          df.index = df['date'].to_list()
          title =  region
       else:
          df = dF1.groupby(['date']).sum()
          title = 'World'
          if 'date' not in df.columns:
             df['date'] =  df.index
       df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    else :
       if region in states and  district in STATES[region]:
          df = get_district_data (df3,region,district)
          if  district != 'Total':
              title = district + "[ " + region + " ]"
          else :
              title = region
       else:
          df = dF1[dF1['country'] == 'India']
          title = 'India'

    columns = ['confirmed','recovered','deaths']
    TAG ={'World':'country','India':'State'}
    DAT ={'World':dF1,'India':dF2}
   
    if mode == 'Bar':
       if geography == 'World':
          df = collapsed_data (dF1,'country',30)[:-1]
          title = 'World'
       if geography == 'India':
          if region in states and district in STATES[region]:
              df = rename_columns(df3)
              df = df[df['State'] == region]
              df = collapsed_data (df, 'District', 30)
              df = df[df['District'] != 'Others']
              TAG[geography] = 'District' 
              title = region 
          else: 
              df = collapsed_data (dF2, 'State', 30)[:-1]
              title = 'India'
          df[columns] = df[columns].astype(float)
       if plot_style == 'Log10':
           df[columns] = np.log10(df[columns])

       fig =  get_bar_chart (df, TAG[geography],title)

    elif mode == 'Pie':
       df = collapsed_data (DAT[geography],TAG[geography],30)
       df = df[df[TAG[geography]] !='Total']
       fig = get_pie(df, geography)
 
    else:
       df.index = df['date'].to_list()
       mask = (df['date'] > start_date) & (df['date'] <= end_date)
       df = df.loc[mask]

       df = df.rename(columns={'confirmed': 'Confirmed',\
         'recovered':'Recovered','deaths':'Deaths'}, errors="raise")
       fig= get_figure(df, region, title, mode, plot_style, rolling_type, rolling_size)

    fig.update_layout({'legend_orientation':'h'})
    fig.update_layout(width=1200,height=800,margin=dict(l=10, r=10, t=40, b=20))

    return fig


if __name__ == '__main__':

    app.run_server(debug=True,dev_tools_silence_routes_logging=False)
