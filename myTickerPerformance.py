import ffn
import pandas as pd
import io
import contextlib
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

Index = ['AAPL', 'MSFT', 'NVDA']
StartDate = '2020-01-01'

def StringToDataFrame(result):
    result2 = []                    ### Convert string into list of lists
    for line in result.split("\n"):
        lines = ' '.join(line.split())
        mylist = lines.split(' ')
        result2.append(mylist)
    
    content = result2[2:-1]         ### Collect content from line 3 to last 2
    header = result2[0]             ### Collect header row
    df = pd.DataFrame(content, columns=header)    
    return df

def myPerf(ticker):
    prices = ffn.get(ticker, start=StartDate)
    #prices = ffn.get(Index[0], start=StartDate)
    #total = prices.calc_total_return()     ### Total returns

    st = prices.calc_stats()
    f = io.StringIO()                   ### Convert Tabulate result into valuable
    with contextlib.redirect_stdout(f):
        st[0].display_monthly_returns()
    result = f.getvalue()               ### Simple variable to store standout output

    result2 = StringToDataFrame(result)
    result2.set_index('Year', inplace=True)     ### Monthly & YTD returns in DF
    print(f'--- {ticker} MoM & YTD ---')
    print(result2)                      ### YTD returns in DF
    result2.to_csv('Fundamental_' + ticker + '_MoM_YTD_Performance.csv')
    
    monthly = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    result2 = result2.drop(columns=monthly, axis=1)
 
    #print("=== Statistics ===")
    stats = st.stats                    ### Statistics
    stats2 = stats[3:13] * 100          ### Remove start & End dates
    stats2 = stats2.astype(float).round(2)
    result2.columns = stats2.columns.values     ### Set YTD column name to ticker

    combine = pd.DataFrame()
    combine = pd.concat([result2, stats2])
    combine = combine.T
    return combine

tickerPerformance = pd.DataFrame()
for i in Index:    
    t = myPerf(i)
    tickerPerformance = pd.concat([tickerPerformance, t])

print(tickerPerformance)
tickerPerformance.to_csv('Fundamental_Tickers_Group_Performance.csv')