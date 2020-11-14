import os
import pandas as pd 
from datetime import datetime 
import platform

if platform.system() == 'Darwin':
   data_path='data/'
else:
   data_path="https://raw.githubusercontent.com/jayanti-prasad/Covid19-Dash/master/data/"
   

Months={'Jan':'01','Feb':'02','Mar':'03','Apr':'04',\
   'May':'05','Jun':'06','Jul':'07','Aug':'08',\
   'Sep':'09','Oct':'10','Nov':'11','Dec':'12'}


def date_formatting(date_string):
   parts = date_string.split('-')
   date_time_str = '2020-' + Months[parts[1]] + "-" + parts[0]
   return datetime.strptime(date_time_str, '%Y-%m-%d')


class DataLoader:
   def __init__(self,):
       self.df_global = pd.read_csv(data_path + os.sep + "covid-19-global.csv", parse_dates=['date'])
       self.df_state_wise = pd.read_csv(data_path + os.sep + "state_wise.csv")
       self.df_state_wise_daily = pd.read_csv(data_path + os.sep + "state_wise_daily.csv")
       self.df_districts = pd.read_csv(data_path + os.sep + "districts.csv",parse_dates=['Date'])
       self.countries = None 
       self.STATES = {}
       self.STATES_CODE = {}
       self.states = None 

       self.__get_countries()
       self.__get_states_code()
       self.__get_states_india()
       self.states_sorted = self.get_current_data('India', 'state',30)['state'].to_list()

   def __get_countries(self):
       dates = sorted (self.df_global['date'].to_list())
       last_date = dates.pop()
       df = self.df_global[self.df_global['date'] == last_date]
       df = df.sort_values(by='confirmed',ascending=False)
       self.countries = df['country'].to_list()
  
 
   def __get_states_india (self):
       states = self.df_districts['State'].to_list()
       districts = self.df_districts['District'].to_list()
       for i in range (0, len (districts)):
          if states [i] not in  self.STATES:
             self.STATES[states[i]] = ["Total"]
             self.STATES[states[i]].append (districts[i])
          else :
             if districts[i] not in self.STATES[states[i]]:
                self.STATES[states[i]].append (districts[i])
       self.states = list (set (self.STATES.keys()))
   
   def __get_states_code(self):
       states =  self.df_state_wise['State'].to_list()
       states_code = self.df_state_wise['State_code'].to_list()
       self.STATES_CODE = dict (zip (states,states_code))

   def get_world_data(self):
      df = self.df_global.groupby(['date']).sum()
      return df 
   
   def get_country_data(self, country):
       if country in self.countries:
          df = self.df_global[self.df_global['country']==country]
          df = df.sort_values(by=['date'])
          df.index = df['date'].to_list()
          return df   
       else:
          print("Country not found !: ",country)
          print(self.countries) 

   def get_state_data (self, state):
      
       Columns = ['Date','State','Confirmed', 'Recovered', 'Deceased']
       columns = [x.lower() for x in Columns]
       COLS = dict (zip (Columns, columns))
       columns = ['Date','State','Confirmed', 'Recovered', 'Deceased']
       if state not in self.states:
          print("State not found ! ", state)
          print("states:",states)
       else:
          state_code = self.STATES_CODE[state]   
          dF = self.df_state_wise_daily[['Date','Status',state_code]].copy()
          dF['Date'] = [date_formatting(d) for d in  dF['Date'].to_list()]
          df_state = pd.DataFrame()
          df_state['Date'] = sorted(list(set(dF['Date'].to_list() )))
          df_state['State'] = [state for i in range (0, len(df_state))]
          df_state.index = df_state['Date'].to_list()
          for column in ['Confirmed','Recovered','Deceased']:
             df = dF[dF['Status'] == column].drop(['Status'], axis=1)
             df = df.rename(columns={state_code: column}, errors="raise")
             df = df.sort_values(by='Date')
             df.index = df['Date'].to_list()
             df[column] = df[column].cumsum()
             X = df[column]
             df_state = pd.concat ([df_state, X],axis=1)
          df_state = df_state.rename(columns=COLS, errors="raise")
          df_state = df_state.rename (columns={'deceased':'deaths'})
          return df_state   

   def get_states_data (self,):
       Columns = ['Date','State','Confirmed', 'Recovered', 'Deceased']
       columns = [x.lower() for x in Columns]
       COLS = dict (zip (Columns, columns))
       dF = pd.DataFrame(columns=columns)
       for state in self.states:
          df = self.get_state_data(state)
          df['state'] = [state for i in range(0, len(df))]
          dF = pd.concat([dF, df], axis=0) 
       return dF  

   def get_districts_data(self,state):
       Columns = ['Date','District','Confirmed', 'Recovered', 'Deceased']
       columns = [x.lower() for x in Columns]
       dF = pd.DataFrame(columns=columns)
       for x in self.STATES[state]:
          df = self.get_district_data (state, x) 
          df['district'] = [x for i in range(0, len(df))] 
          dF = pd.concat([dF,df],axis=0)
       return dF 
 

   def get_district_data (self, state, district):
       if state not in  self.states:
          print("State not found:",state,self.states)
          return 
       else:
          if district not in self.STATES[state]:
             print("District not found:", district, state)
             return 
          else:
             dF = self.df_districts
             df1 = dF [dF['State'] == state].drop(['State'], axis=1)
             df1 = df1 [df1['District'] == district].drop(['District'], axis=1)
             df = df1 [['Date', 'Confirmed', 'Recovered', 'Deceased']].copy()
             df = df.rename(columns={'Date': 'date','Confirmed':'confirmed',\
                'Recovered':'recovered','Deceased':'deaths'}, errors="raise")
             df = df.sort_values(by='date')
             df.index = df['date'].to_list()
             return df   

   def get_current_data(self, region, sub_region,num_rows):
      name = sub_region  
      if name == 'country':
         dF  = self.df_global 
      if name == 'state':
         dF = self.get_states_data()
      if name == 'district':
         dF = self.get_districts_data (region)

      dates = dF['date'].to_list()
      last_date = list(pd.to_datetime(dates).sort_values()).pop()
      df = dF[dF['date'] == last_date]
      df = df.sort_values(by=['confirmed'],ascending=False) 
      df.index = df[name].to_list()
      df1 = df.iloc[:num_rows].reset_index()[[name,'confirmed','recovered','deaths']].copy()
      rest = df.iloc[num_rows:].sum()
      rest [name] = 'Others'
      last_index = len (df1)
      for col in df1.columns:
         if col in rest:
             df1.at[last_index, col] = rest[col]
      return df1

          
