import sqlite3
import openpyxl
import pandas as pd

class DB():
    def __init__(self,dbname):
        self.conn = sqlite3.connect(f'./{dbname}')
        self.cursor = self.conn.cursor()
        print("Opened database successfully")

    def get_table(self):
        self.cursor.execute("select name from sqlite_master where type='table'")
        self.conn.commit()
        result = self.cursor.fetchall()
        return result

    def read(self,tablename):
        try:
            self.cursor.execute("SELECT comment from " + tablename)
            self.conn.commit()
            description = self.cursor.description
            datas = []
            for row in self.cursor.fetchall():
                datas.append(row)
            # print(datas)
            return datas

        except Exception as e:
            print(str(e))
            print("数据读取错误")


aa = DB("comment1.db")
table_list = aa.get_table()
print(table_list)
with open("./data.txt","w", encoding='utf-8') as f:
    for i in range(len(table_list)):
        if table_list[i][0] == 'sqlite_sequence':
            continue
        title = table_list[i][0]

        value = aa.read(title)

        
        for row in value:
            print(row[0])
            f.writelines(row[0])
            f.writelines('\n')
