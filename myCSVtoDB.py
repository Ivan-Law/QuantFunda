import pandas as pd
import os
import sqlite3

cwd = os.getcwd()
myFolder = os.listdir(cwd)
conn = sqlite3.connect("myDB.db")                      ### SQLite Name

cursor = conn.cursor()
#cursor.execute("DROP TABLE myDB")

for i in myFolder:
    pp = cwd + "\\" + i
    if (os.path.isdir(pp)):             ### Collect all folder names

        myFiles = os.listdir(pp)
        df = []
        count = 0
        
        for file in myFiles:            ### For each folder 
            if file.endswith('.csv'):   ### Collect all csv file names
                dftmp = pd.read_csv(pp + "\\" + file, index_col=0)
                dftmp = dftmp.fillna(0)
                if count == 0:          ### First Dataframe as df; others concat
                    df = dftmp.copy()
                    count = 1
                else:
                    df = pd.concat([df, dftmp])
                    df['Ticker'] = i    ### Add new column as ticker name
        df.to_sql("myDB", conn, if_exists="append")        

dd = pd.read_sql_query("Select * from myDB", conn)
print(dd)

conn.close()
