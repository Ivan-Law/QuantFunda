from financetoolkit import Toolkit
from datetime import datetime
import os
import shutil
import re
from os import listdir
from os.path import isfile, join

myNow = datetime.now().strftime('%Y-%m-%d')
TickName = ['AAPL', 'MSFT', 'NVDA']

def moveFiles(TT):
    cwd = os.getcwd()
    input_folder = cwd
    files = [f for f in listdir(input_folder) if isfile(join(input_folder, f))]
    
    for file in files:
        if file.endswith(".csv"):               
               fn = os.path.splitext(file)[0]
               myFolder = re.search('-(.*)-2023', fn)           ### Require to update when necessary
               myF = myFolder.group(1)              
               target_dir = cwd + "\\" + myF               
               shutil.move(os.path.join(cwd, file), target_dir)              
             
    file = ""
    fn = ""
    files = []      
    target_dir = ""

def myAnnualFunda(TT):
    companies = Toolkit(
        tickers=[TT],
        api_key="<Your_Key>",         ### Register a free API Key from financetoolkit:
        start_date='2020-12-31')      ### https://github.com/JerBouma/FinanceToolkit

    # a Financial Statement example
    myFin_BS = companies.get_balance_sheet_statement()
    myFin_IS = companies.get_income_statement()
    myFin_CF = companies.get_cash_flow_statement()

    #pp.pprint(myFin_BS)
    myFin_BS.to_csv('myFunda_BS-' + TT + '-' + myNow + '.csv')
    myFin_IS.to_csv('myFunda_IS-' + TT + '-' + myNow + '.csv')
    myFin_CF.to_csv('myFunda_CF-' + TT + '-' + myNow + '.csv')

    # Ratios example,  Enterprise Value Breakdown,  dupont_analysis
    myFin_ratios = companies.ratios.collect_profitability_ratios()
    myFin_models = companies.models.get_enterprise_value_breakdown()
    myFin_analysis = companies.models.get_extended_dupont_analysis()

    myFin_ratios.to_csv('myFunda_ratios-' + TT + '-'  + myNow + '.csv')
    myFin_models.to_csv('myFunda_models-' + TT + '-'  + myNow + '.csv')
    myFin_analysis.to_csv('myFunda_analysis-' + TT + '-'  + myNow + '.csv')
    
    CHECK_FOLDER = os.path.isdir(TT)
    if not CHECK_FOLDER:
        os.makedirs(TT)
    
    moveFiles(TT)


for i in TickName:
    try:
        myAnnualFunda(i)
    except:
        pass
    

TickName = ''