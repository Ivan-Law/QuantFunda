import pandas as pd
import numpy as np
import os
import sqlite3

cwd = os.getcwd()
myFolder = os.listdir(cwd)
conn = sqlite3.connect("myDB.db")                      ### SQLite Name
df = pd.read_sql_query("Select * from myDB", conn)     ### Table Name

def yoyPerf():
    newdf = []                                      ### New Dataframe for performance ratio
    newdf = pd.DataFrame(index=df.index)            ### Copy index & header to new Dataframe
    newdf = pd.DataFrame(columns=df.columns)      
    colNum = df.shape[1]
    
    for i in range(1, colNum - 2):                  ### Performance ratios of 2 years
        numerator = colNum - i - 1
        denominator = colNum - i - 2                              
        ratio = ((df.iloc[:,numerator]) / (df.iloc[:,denominator]) -1)
        ratio = ratio.replace(np.inf, 0)            ### Replace 0 if denominator is 0  
        ratio = ratio.fillna(0)
        ratio = ratio.apply(lambda x: f"{x:.2%}")   ### Display ratios as %              
        newdf[newdf.columns[-1 * i - 1]] = ratio
        newdf = newdf.fillna(0)
    
    newdf['index'] = df.iloc[:,0].values
    newdf['Ticker'] = df.iloc[:,-1].values
    return newdf

yoy = yoyPerf()
print(yoy)
yoy.to_csv('Fundamental_YoY_Analysis.csv')

def myFunc(numeratorName, denominatorName, FuncName, Func): ### Calculate 2 figures in the same year

    if Func == "DIV-DF":
        numerator = numeratorName.copy()
        denominator = denominatorName.copy()
        Func = "DIV"
    elif Func == "SUB-DF":
        numerator = numeratorName.copy()
        denominator = denominatorName.copy()
        Func = "SUB"
    else:
        numerator = df.groupby(['index']).get_group(numeratorName)
        denominator = df.groupby(['index']).get_group(denominatorName)
    tm = numerator.copy()

    numerator.set_index(['index','Ticker'], inplace=True)
    denominator.set_index(['index','Ticker'], inplace=True)

    if Func == "DIV":
        tmpdf = numerator.values / denominator.values
    if Func == "ADD":
        tmpdf = numerator.values + denominator.values
    if Func == "SUB":
        tmpdf = numerator.values - denominator.values
    tmpdf = pd.DataFrame(tmpdf)
    tmpdf = tmpdf.round(2)

    tmpdf['Ticker'] = tm.iloc[:,-1].values          ### Adding Ticker Column
    tmpdf.insert(0,'index',FuncName)                ### Adding Inex Column
    tmpdf.columns = tm.columns.values               ### Rename DF Column Header Name
    
    return tmpdf

mysubDF = myFunc('Total Current Assets','Total Liabilities', 'Curr Ass - Liab', 'SUB')      # Net Cur Asset = Curr Ass - Liab
myaddDF = myFunc('Total Other Income','Operating Income', 'Other Inc + Oper Income', 'ADD') # EBIT = Total Other Income + Operating Income
ROC = myFunc(myaddDF, mysubDF, 'EBIT / Cur Asset', 'DIV-DF')
TEV = df.groupby(['index']).get_group("Enterprise Value")
EBIT_on_TEV = myFunc(myaddDF, TEV, 'EBIT / TEV', 'DIV-DF')
GROSSPROFIT = df.groupby(['index']).get_group("Gross Profit")
TOTALASSET = df.groupby(['index']).get_group("Total Assets")
GPA = myFunc(GROSSPROFIT, TOTALASSET, 'Gr Profit / Tot Asset', 'DIV-DF')
CASH = df.groupby(['index']).get_group("Cash and Cash Equivalents")
CASH = CASH.drop_duplicates()
OA = myFunc(TOTALASSET, CASH, 'Total Asset - Cash', 'SUB-DF')

ST = df.groupby(['index']).get_group("Short Term Debt")
LT = df.groupby(['index']).get_group("Long Term Debt")
PS = df.groupby(['index']).get_group("Preferred Stock")
CS = df.groupby(['index']).get_group("Common Stock")
MI = df.groupby(['index']).get_group("Minority Interest")
MI = MI.drop_duplicates()

SNOA1 = myFunc(TOTALASSET, ST, 'Total Asset - Short Term Debt', 'SUB-DF')
SNOA2 = myFunc(SNOA1, LT, 'SNOA1 - Long Term Debt', 'SUB-DF')
SNOA3 = myFunc(SNOA2, PS, 'SNOA2 - Preferred Stock', 'SUB-DF')
SNOA4 = myFunc(SNOA3, CS, 'SNOA3 - Common Stock', 'SUB-DF')
OL    = myFunc(SNOA4, MI, 'SNOA4 - MI', 'SUB-DF')
SNOA_ = myFunc(OA, OL, 'OA - OL', 'SUB-DF')
SNOA  = myFunc(SNOA_, TOTALASSET, 'SNOA', 'DIV-DF')

#print(mydivDF)
#print("--- Net Cur Asset ---")      ### Net Cur Asset = Curr Ass - Liab
#print(mysubDF)  
#print("--- EBIT ---")               ### EBIT = Total Other Income + Operating Income
#print(myaddDF)  
print("--- ROC = EBIT / Cur Asset ---")                ### ROC = EBIT / Net Cur Asset
print(ROC)
print("--- EBIT / TEV ---")
print(EBIT_on_TEV)
print("--- GPA = Gross Profit / Total Asset ---")
print(GPA)
print("--- SNOA = (Tot Asset - ST & LT Debts - Min Int - Pref Stock - Bk Com St) / Tot Asset ---")
print(SNOA)

first = 0
comRatios = pd.DataFrame()
def combi(ratios):
    global first
    global comRatios
    global tickers
    
    if first == 0:
        comRatios = ratios.copy()
        ticker = ratios['Ticker']
        comRatios.drop(labels=['Ticker'], axis=1, inplace=True)
        comRatios.insert(0, 'Ticker', ticker)
        first = 1

    else:
        ratios_extract = ratios.iloc[:,:5]              ### Collect columns without ticker
        ratiosCol = pd.DataFrame(ratios_extract)
        comRatios = pd.concat([comRatios, ratiosCol], axis=1)    
    
    return comRatios

comList = [ROC, EBIT_on_TEV, GPA, SNOA]
for i in comList:
    combi(i)

print("--- Combined Ratios ---")
print(comRatios)

comRatios.to_csv('Fundamental_Ratios_Analysis.csv')
conn.close()