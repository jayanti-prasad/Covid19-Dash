import sys
import os
import pandas as pd
from datetime import datetime 
import numpy as np
import argparse 
import matplotlib.pyplot as plt
import platform

if platform.system() == 'Darwin':
   data_path="data/"
else:
   data_path="/home/covid19db/Covid19-Dash/data/"
    

Months={'Jan':'01','Feb':'02','Mar':'03','Apr':'04',\
   'May':'05','Jun':'06','Jul':'07','Aug':'08',\
   'Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

# This is for  global data 

def date_formatting(date_string):
   parts = date_string.split('-')
   date_time_str = '2020-' + Months[parts[1]] + "-" + parts[0]
   return datetime.strptime(date_time_str, '%Y-%m-%d')


def get_states_data (df1, df2):
   states =  df1['State'].to_list()
   states_code = df1['State_code'].to_list()
   STATES = dict (zip (states_code, states))
   columns = ['Date','State','Confirmed', 'Recovered', 'Deceased']
   dF_out = pd.DataFrame(columns=columns)

   df2['Date'] = [date_formatting(d) for d in  df2['Date'].to_list()]
   for state in df2.columns[3:]:
       if state in STATES:
          dF = df2[['Date','Status',state]].copy()
          df_state = pd.DataFrame()
          df_state['Date'] = sorted (list ( set (df2['Date'].to_list() )))
          df_state['State'] = [STATES[state] for i in range (0, len(df_state))] 
          df_state['State_Code'] = [state for i in range (0, len(df_state))] 
          df_state.index = df_state['Date'].to_list()
          for column in ['Confirmed','Recovered','Deceased']:
             df = dF[dF['Status'] == column].drop(['Status'], axis=1)
             df = df.rename(columns={state: column}, errors="raise")
             df = df.sort_values(by='Date')
             df.index = df['Date'].to_list()
             df[column] = df[column].cumsum()
             X = df[column]
             df_state = pd.concat ([df_state, X],axis=1)
          dF_out = pd.concat ([dF_out, df_state],axis=0)
          #print(STATES[state], df_state.shape, dF_out.shape)

   dF_out = dF_out.rename(columns={'Date': 'date','Confirmed':'confirmed',\
     'Recovered':'recovered','Deceased':'deaths'}, errors="raise")

   return dF_out, STATES 


def get_districts (df3):
    states = df3['State'].to_list() 
    districts = df3['District'].to_list()
    S = {}
    for i in range (0, len (districts)):
       if states [i] not in  S:
          S[states[i]] = ["Total"]
          S[states[i]].append (districts[i]) 
       else :
          if districts[i] not in S[states[i]]:
             S[states[i]].append (districts[i]) 
 
    return S 

def get_district_data (dF, state, district):

    if district !='Total':
       df = dF [dF['State'] == state].drop(['State'], axis=1)
       df = df [df['District'] == district].drop(['District'], axis=1)
    else:
       df = dF[dF['State'] == state]
       df = df.groupby('Date').sum()
       df['Date'] = df.index

    df = df [['Date', 'Confirmed', 'Recovered', 'Deceased']].copy()
    df = df.rename(columns={'Date': 'date','Confirmed':'confirmed',\
     'Recovered':'recovered','Deceased':'deaths'}, errors="raise")
    df = df.sort_values(by='date')
    df.index = df['date'].to_list()
    return df


def get_data_world ():
    dF = pd.read_csv(data_path + os.sep + "covid-19-global.csv", parse_dates=['date'])
    dates = sorted (dF['date'].to_list())
    last_date = dates.pop()
    df = dF[dF['date'] == last_date]
    df = df[df['deaths'] > 0]
    df = df.sort_values(by='confirmed',ascending=False)
    return dF, df['country'].to_list()


def get_data_india():

   df1 = pd.read_csv(data_path + os.sep + "state_wise.csv")
   df2 = pd.read_csv(data_path + os.sep + "state_wise_daily.csv")
   df3 = pd.read_csv(data_path + os.sep + "districts.csv",parse_dates=['Date'])

   dF, STATES = get_states_data (df1, df2)

   # get a dictionary of states sorted by the number of cases 
   DICT = get_districts (df3)
   dates = sorted (list (set (dF['date'].to_list())))
   last_date = dates.pop()
   df_last = dF[dF['date'] == last_date]
   df_last = df_last.sort_values(by='confirmed',ascending=False)
   states = df_last['State'].to_list()
   STATES_NEW = {'Total':[]}
   for s in states:
      if s in DICT:
         STATES_NEW[s] = DICT[s]
   return dF, df3, STATES_NEW

def collapsed_data (dF, name, num_rows):
    dates = dF['date'].to_list()
    last_date = list(pd.to_datetime(dates).sort_values()).pop()
    df = dF[dF['date'] == last_date]
    df = df.sort_values(by=['confirmed'],ascending=False)
    df1 = df.iloc[:num_rows].reset_index()[[name,'confirmed','recovered','deaths']].copy()
   
    rest = df.iloc[num_rows:].sum()
    rest [name] = 'Others'
    last_index = len (df1)
    for col in df1.columns:
       if col in rest:
         df1.at[last_index, col] = rest[col] 
    return df1  



if __name__ == "__main__":

   parser = argparse.ArgumentParser()
   parser.add_argument('-i','--input-dir',help='Input data dir',default='data')
   parser.add_argument('-s','--state-code',help='State Code',default='MH')
   parser.add_argument('-d','--district',help='District',default='Pune')

   args = parser.parse_args()

   df1 = pd.read_csv(args.input_dir + os.sep + "state_wise.csv")
   df2 = pd.read_csv(args.input_dir + os.sep + "state_wise_daily.csv")
   df3 = pd.read_csv(args.input_dir + os.sep + "districts.csv",parse_dates=['Date'])

   dF, STATES = get_states_data (df1, df2)
   STATE_DICT = get_districts (df3)
   

   print(dF.shape, dF.columns)
   print("States:",STATES)
   print("States:",STATE_DICT)   

   if args.district:
      df = get_district_data (df3,STATES[args.state_code],args.district)
      title = args.district + "[ "+ STATES[args.state_code] + " ]"
   else:
      df = dF[dF['State_Code'] == args.state_code]
      title = STATES[args.state_code] 


   df = df.sort_values(by='date')
   df.index = df['date'].to_list()

   fig, ax = plt.subplots(3, 1, sharex=True)
   fig.set_figheight(18)
   fig.set_figwidth(18)
   plt.subplots_adjust(hspace=.0)

   ax[0].set_title(title)
   ax[0].set_ylabel('Confirmed')
   ax[1].set_ylabel('Recovered')
   ax[2].set_ylabel('Deaths')

   ax[0].plot(df['confirmed'],'ob')
   ax[1].plot(df['recovered'],'og')
   ax[2].plot(df['deaths'],'or')
   for i in range(0, 3):
      ax[i].grid()

   plt.show()

