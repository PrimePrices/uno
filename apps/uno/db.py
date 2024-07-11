from get_db import get_db, requires_db



class DBClass:
    table="default"
    def __init__(self):self.id=None # This stops the self.id from causing errors when the code is parsed
    def _update_db(self, attribute:str, value:str|list):
        conn= get_db()
        print(f"updating {attribute} to {value}")
        if type(value)==list:
            value=",".join(value)
        conn.execute(f"UPDATE {self.table} SET {attribute}='{value}' WHERE id={self.id}")
        conn.commit()
        conn.close()
    def _get_db_attribute(self, attribute:str):
        conn= get_db()
        value=conn.execute(f"SELECT {attribute} FROM {self.table} WHERE id={self.id}").fetchone()[0]
        conn.close()
        return value
    @staticmethod
    def _database_property(attribute:str) -> property:
        def getter(self) -> str:
            value= self._get_db_attribute(attribute)
            return value
        def setter(self, value:str|list):
            if type(value)==list:
                value=",".join(value)
            self._update_db(attribute, value)
        return property(getter, setter)
    @staticmethod
    def _database_list(attribute:str, data_type=None) -> property:
        def getter(self) -> CSVList:
            return CSVList(table=self.table, entry_uid=self.id, column=attribute, data_type=data_type)
        def setter(self, iterable:list) -> None:
            CSVList(iterable=iterable, table=self.table, entry_uid=self.id, column=attribute, data_type=data_type)
        return property(getter, setter)
class CSVList(list):
    __slots__=["data", "table", "entry_uid", "column", "data_type"]
    def __init__(self, iterable=None, table=None, entry_uid=None, column=None, data_type=None):
        self.table=table
        self.entry_uid=entry_uid
        self.column=column
        self.data_type=data_type
        if iterable!=None:
            self.set_list(iterable)
    def __contains__(self, value):
        return value in self.get_list()
    def cast_list(self, data):
        if self.data_type==None:
            return data
        a=[]
        if not(data):
            print(f"trying to cast {data=}, appently null")
            return []
        for i in data:
            try:
                a.append(self.data_type(i))
            except:
                raise TypeError(f"Expected value that could be cast into {self.data_type}. Instead got {i} of type={type(i)}")
        return a
    def __getitem__(self, index):#
        return self.get_list()[index]
    def get_list(self) -> list:
        conn=get_db() 
        data:str=conn.execute(f"SELECT {self.column} FROM {self.table} WHERE id={self.entry_uid}").fetchone()[0]
        conn.close()
        if not data:
            #print(f"{data=}")
            return []
        list_data: list[str]=data.split(",")
        list_data=self.cast_list(list_data)
        #if self.column!="draw":
            #print(f"FROM get_list SELECT {self.column} FROM {self.table} WHERE id={self.entry_uid} RETRUNS" , data)
            #print(f"LIST_DATA = {list_data}, {type(list_data)=}")
            #print("\n".join([str(i.code_context) for i in stack()]))
        return list_data
    def set_list(self, l:list) -> None:
        if self.data_type!=None:
            l=[str(i) for i in l]
        string=",".join(l)
        conn=get_db()
        conn.execute(f"UPDATE {self.table} SET {self.column}='{string}' WHERE id={self.entry_uid}")
        conn.commit()
        conn.close()
    def append(self, value):
        data=self.get_list()
        data.append(value)
        self.set_list(data)
    def pop(self, index):
        data=self.get_list()
        r=data.pop(index)
        self.set_list(data)
        return r
    def reverse(self):
        list = self.get_list()
        list.reverse()
        self.set_list(list)
    def __setitem__(self, index, item):
        if type(item)==str and "," in item:
            raise TypeError("Text cannot contain a comma")
        try:
            item=str(item)
        except:
            raise TypeError(f"Item {item} of type {type(item)} couldn't be converted to a string")
        data=self.get_list()
        data[index]=item
        self.set_list(data)
    def __str__(self):
        return str(self.get_list())
    def __len__(self):
        return len(self.get_list())
    def __iter__(self):
        return iter(self.get_list())
    def __list__(self):
        return list(self.get_list())