import os
import pandas as pd
import matplotlib.pyplot as plt
import glob 
import argparse 
from datetime import datetime 
from subprocess import Popen, PIPE
import urllib.request

def update_repo (git_dir):
   proc = Popen(["git","-C",git_dir,"pull"], stdout=PIPE,
        stderr=PIPE, universal_newlines=True)
   output, stderr = proc.communicate()
   if stderr :
      print(stderr)
   else:
      print(output)


def update_india (args):
    print("Updating data for India")
    SOURCE="https://api.covid19india.org/csv/latest/"
    files=["state_wise","state_wise_daily","district_wise","districts","tested_numbers_icmr_data"]
    for f in files:
       urllib.request.urlretrieve(SOURCE+f+".csv", args.output_dir + os.sep + f+'.csv')
       print("downloaded", args.output_dir + os.sep + f+".csv")


def get_data (input_dir):
    filenames = glob.glob(input_dir + os.sep \
      + "csse_covid_19_data/csse_covid_19_daily_reports/*.csv")
    count = 0
    dF = pd.DataFrame(columns=['Country_Region', 'Confirmed', 'Deaths', 'Recovered', 'date'])
    for filename in sorted(filenames):
       date_time_str = os.path.basename(filename).replace(".csv","")
       date = datetime.strptime(date_time_str, '%m-%d-%Y')
       df = pd.read_csv(filename)
       if 'Country/Region'  in df.columns:
          df = df.rename(columns={"Country/Region": "Country_Region"}, errors="raise")
       df = df.groupby(['Country_Region']).sum()
       df['date'] = [date for i in range (0, df.shape[0])]
       df = df.reset_index()
       print(date, df.shape)       
       dF = pd.concat ([dF,df])
    dF = dF.reset_index()
    dF = dF.rename(columns={"Country_Region":"country",\
       "Confirmed":"confirmed","Recovered":"recovered",\
       "Deaths":"deaths"}, errors="raise")
      
    dF = dF[['date','country','confirmed', 'recovered','deaths']].copy()
    return dF 
 

if __name__ == "__main__":

   parser = argparse.ArgumentParser()
   parser.add_argument('-i','--input-dir',help='Input dir',\
      default='/Users/jayanti/Data/COVID-19/COVID-19/')
   parser.add_argument('-o','--output-dir',help='Output  dir',default='data')
   parser.add_argument('-c','--country',help='Country')

   args = parser.parse_args()
   os.makedirs(args.output_dir,exist_ok=True)

   update_india (args)
   update_repo (args.input_dir)

   dF = get_data (args.input_dir)
   print(dF.shape, dF.columns)
   dF.to_csv(args.output_dir + os.sep + "covid-19-global.csv")
 
