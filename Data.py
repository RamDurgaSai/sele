from sqlite3 import connect
from time import localtime
from typing import Union

class DataBase:
    def __init__(self,file:str):
        self.file_path = file
        self.connection = connect(self.file_path)

    def create_tables(self,*args,**kwargs):
        for table_name in args:
            self.connection.execute(f"""
            create table if not exists "{table_name}"(
            date integer primary key autoincrement,
            info text, path text , pdisk text, telegram int);
            """)
    def update(self,type:str,table:str,date:int,data)-> None:
        if not date:
            year, month, day, hour, minute, second, wd, yd, isd = localtime()
            date = 10_000*year + 100*month + day
        if isinstance(data,bool):
            data = int(data)
        sql = f"""
        update "{table}" set "{type}" = "{data}" where date = "{date}" ;
        """
        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.connection.commit()

    def select(self,*args,table:str,date:int = None):
        if not date:
            year, month, day, hour, minute, second, wd, yd, isd = localtime()
            date = 10_000 * year + 100 * month + day

        command = f"""
        select {" , ".join([str(arg) for arg in args])} from  "{table}" where date = {date} ;
        """
        cursor = self.connection.execute(command)
        return cursor.fetchall()

    def insert(self,table:str,**kwargs):
        command = f"""
        
        insert into "{table}" ({" , ".join(kwargs.keys())}) values ({" , ".join(['"'+str(value)+'"' for value  in kwargs.values()])}) ;
        """
        cursor = self.connection.cursor()
        cursor.execute(command)
        self.connection.commit()






