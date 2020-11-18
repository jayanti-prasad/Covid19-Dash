import os
import time
import numpy 
import numpy as np
import dash
import argparse 
import platform
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import date, datetime
from data_utils import DataLoader
from fig_utils import get_ts_plot, get_bar_plot,get_pie_plot

"""
This is the main dashboard program and it uses 'data_utils' for
fetching the data and 'fig_utils' to fetch plotply express figues.
"""

numpy.seterr(divide = 'ignore') 
os.environ["TZ"] = "Asia/Kolkata"
time.tzset()

DL = DataLoader()

start_date = datetime.strptime('2020-01-01', '%Y-%m-%d')
end_date = date.today()

external_stylesheets = ['bWLwgP.css']
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.title = 'Jayanti Prasad\'s Covid-19 Dashboard'

my_js_url=['display.js']
app.scripts.append_script({
"external_url": my_js_url
})


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
              labelStyle={'display': 'inline-block'})),

        html.Td(
           dcc.DatePickerRange(
              id='date-picker-range',
              start_date_placeholder_text="Start Date",
              end_date_placeholder_text="End Date",
              start_date=start_date,
              end_date=end_date)),
        html.Td(),
        html.Td(),
      ]),
      html.Tr([
        html.Td(
           dcc.Dropdown(
              id='region',
              )),
         html.Td(
            dcc.RadioItems(
              id='mode',
              options=[{'label': i, 'value': i} for i in ['Bar','Pie','TimeSeries']],
              value='TimeSeries',
              labelStyle={'display': 'inline-block'}),),
        html.Td(
           dcc.Dropdown(
             id='tstype',
             value='Total',
        ),), 
        html.Td(
           dcc.RadioItems(
             id='scale',
             options=[{'label': i, 'value': i} for i in ['linear','log']],
             value='linear',
             labelStyle={'display': 'inline-block'}),
            ),
      ]),
    html.Tr([
        html.Td(
          dcc.Dropdown(
             id='sub_region',
             )),
        html.Td(
          dcc.Dropdown(
             id='rolling_type',
             options=[{'label': "Rolling " + i, 'value': i} for i in ['Mean','Median']],
             value='Mean',),
        ),
        html.Td(
           dcc.Dropdown(
             id='rolling_size',
             options=[{'label': str(i) + " Days", 'value': i} for i in [1,2,5,7,10,15]],
             value=1,),
        ),
     html.Td(),
    ]),
    html.Tr([
       html.Td("Data Source",style={'width': '100%', 'display': 'inline-block'}),
       html.Td("https://github.com/CSSEGISandData/COVID-19"),
       html.Td("https://api.covid19india.org/"),
       html.Td(),
    ]),
    ],style={'border': '4px solid black','background-color':'#FFFFE0'},
    ),

    html.Div([
    html.Div([ html.Div(id='output-container-date-picker'),]),
    html.Hr(),
    dcc.Graph(id='indicator-graphic'),
   ]),
  html.H3(children= '(c) Jayanti Prasad 2020', style={'text-align': 'center'}),
])



@app.callback(
    dash.dependencies.Output('tstype', 'options'),
    [dash.dependencies.Input('mode', 'value')]
)
def update_dropdown_ts(name):
    if name == 'TimeSeries':
       return [{'label': i, 'value': i} for i in ['Total','Daily','Active']]
    else:
       return [{'label': i, 'value': i} for i in []]

@app.callback(
    dash.dependencies.Output('sub_region', 'options'),
    [dash.dependencies.Input('region', 'value')]
)
def update_dropdown_sub_region(name):
    if name in DL.states:
       return [{'label': i, 'value': i} for i in DL.STATES[name]]
    else:
       return [{'label': i, 'value': i} for i in []]
         


@app.callback(
    dash.dependencies.Output('region', 'options'),
    [dash.dependencies.Input('geography', 'value')]
)
def update_dropdown_region(name):
    if name == 'World':
         return [{'label': i, 'value': i} for i in DL.countries]
    else:
         return [{'label': i, 'value': i} for i in DL.states_sorted]


@app.callback(Output('indicator-graphic', 'figure'),
    [Input('geography', 'value'),
    Input('region', 'value'),
    Input('sub_region', 'value'),
    Input('mode', 'value'),
    Input('tstype', 'value'),
    Input('scale', 'value'),
    Input('rolling_type', 'value'),
    Input('rolling_size', 'value'),
    Input(component_id='date-picker-range', component_property='start_date'),
    Input(component_id='date-picker-range', component_property='end_date'),])

def update_graph(geography,region,sub_region,mode,tstype,scale,rolling_type,rolling_size,start_date,end_date):
    parser = argparse.ArgumentParser()
    parser.add_argument('-g','--geography',default=geography)
    parser.add_argument('-r','--region',default=region)
    parser.add_argument('-s','--sub-region',default=sub_region)
    parser.add_argument('-t','--tstype',default=tstype)
    parser.add_argument('-m','--mode',default=mode)
    parser.add_argument('-l','--scale',default=scale)
    parser.add_argument('-a','--rolling-type',default=rolling_type)
    parser.add_argument('-w','--rolling-size',type=int,default=rolling_size)
    parser.add_argument('-b','--start-date',default=start_date)
    parser.add_argument('-e','--end_date',default=end_date)
    args = parser.parse_args()

    if args.mode == 'TimeSeries':
       fig = get_ts_plot(args, DL)
    if args.mode == 'Bar':
       fig = get_bar_plot(args, DL)
    if args.mode == 'Pie' and platform.system() == 'Darwin':
       fig = get_pie_plot(args, DL)

    fig.update_layout({'legend_orientation':'h'})
    fig.update_layout(height=800,width=1200,margin=dict(l=10, r=10, t=40, b=20))

    return fig


if __name__ == '__main__':

    app.run_server(debug=True,dev_tools_silence_routes_logging=False)
