from __future__ import annotations
from threading import Thread as _T
import json, os, time, traceback as tb


__all__ = ["ViDB"]

def thread(name):
    def wrapper(func):
        def wrapper(*args, **kwargs):
            t = _T(target=func, args=args, kwargs=kwargs, name=name)
            t.daemon = True
            t.start()
            return t
        return wrapper
    return wrapper


class Item(dict):
    def __init__(self, table: TableClass, data: dict):
        self.table = table
        self.update(data)

    def __getitem__(self, key):
        return self.get(key)

    def update(self, data: dict):
        self.table.check(data)
        
        for key, value in data.items():
            self[key] = value
        
        self.table.update()
    
    def copy(self):
        return self.__class__(self.table, {**self})


class TableClass:
    def __init__(self, db: ViDB, name: str, types: dict[str, type]):
        self.do_check = True
        self.db = db
        self.name = name
        self.types = types
        self.columns = []
        self.columns.append(self.types)
        self.db.log(f"Created table {name}, types: {types}\n")
    
    def __getitem__(self, key):
        r = self.columns[1:][key].copy()
        r["id"] = key
        return r
    
    def __setitem__(self, key, value):
        value = {**value}
        del value["id"]
        self.columns[key] = value
    
    def __delitem__(self, key):
        del self.columns[key]
    
    def __len__(self):
        return len(self.columns)
    
    def __contains__(self, key):
        key = key.copy()
        del key["id"]
        return key in self.columns
    
    def check(self, data: dict):
        self.db.log("Checking data")
        self.db.log(f"Data: {data}")
        self.db.log(f"Types: {self.types}")
        for key, value in data.items():
            self.db.log(f"Checking {self.types[key]} = {type(value)}")
            if self.types[key] != type(value):
                raise TypeError(f"Type of {key} is {type(value)}, but should be {self.types[key]}")
    
    def insert(self, data: dict):
        log = self.db.log
        if self.do_check:
            log("Checking data enabled")
            self.check(data)
        log("Inserting data")
        self.columns.append(data)
        log("Updating")
        self.update()
        log("Done, new data: " + str(self.all()))
    
    def update(self):
        self.db.update()
    
    def all(self):
        r = []
        for n, item in enumerate(self.columns):
            item = item.copy()
            item["id"] = n
            r.append(item)
        return r
    
    def select(self, condition: callable):
        r = []
        for n, item in enumerate(self.columns[1:]):
            if condition(item):
                item = item.copy()
                item["id"] = n
                r.append(item)
        return r


class Table(dict):
    def __init__(self, db: ViDB, data: dict):
        self.db = db
        self.update(data)

    def create(self, name: str, types: dict[str, type]):
        self[name] = TableClass(self.db, name, types)
        self.db.update()
    
    def remove(self, name: str):
        del self[name]
        self.db.update()
    
    def list(self):
        print("Tables:")
        for name, table in self.items():
            print(f"  {name}")
            for key in table.types:
                print(f"    {key}", end="")
            print()
            for item in table.all():
                print(f"    {item['id']}:", end="")
                for key, value in item.items():
                    print(f" {key}={value}", end="")
                print()


class ViDB:
    def __init__(self, directory, log=lambda *a: None, cols=80):
        self.directory = directory
        self.log = log
        self.cols = cols
        self.block = False
        self.upload()
    
    def upload(self):
        self.block = True
        try:
            if not os.path.exists(self.directory):
                os.mkdir(self.directory)
            
            try:
                with open(self.directory + "/config.vidb", "rt") as f:
                    self.config = json.load(f)
                    exists = True
            except FileNotFoundError:
                if not exists:
                    print("\033[1;31mNo config.vidb found, replacing with default\033[0m")
                    self.config = {"pollDelay": 10}
                else:
                    print("\033[1;31mConfig.vidb found, but have not some necessary parameters, replacing with default\033[0m")
                    self.config["pollDelay"] = 10
                with open(self.directory + "/config.vidb", "wt") as f:
                    json.dump(self.config, f)
            
            try:
                with open(self.directory + "/db.json", "rt") as f:
                    db = json.load(f)
            except FileNotFoundError:
                print("No db.json found, replacing with empty")
                db = {}
                with open(self.directory + "/db.json", "wt") as f:
                    json.dump(db, f)
            
            self.table = Table(self, db)
            
            for table in db:
                types = {}
                # print(db[table][0].items())
                for key, value in db[table][0].items():
                    types[key] = eval(value)
                self.table[table] = TableClass(self, table, types)
                self.table[table].columns += db[table][1:]
                self.__setattr__(table, self.table[table])
        except Exception as e:
            excname = "Uploading error: " + e.__class__.__name__
            num = (self.cols-len(excname))//2
            print("\033[1;31m" + "─" * num + excname + "─" * num + "\033[0m")
            tb.print_exception(e)
            print("\r\033[1;31mEmulator catched uploading error\033[0m")
            fe = tb.format_exception(e)
            self.log("\n\n\nUploading error\n\n"+fe if type(fe) is str else ', '.join(fe)+"\n\n\n")
        
        self.block = False
    
    @thread("Poll")
    def poll(self):
        while True:
            while self.block: time.sleep(0.1)
            try:
                self.upload()
                time.sleep(self.config["pollDelay"])
            except Exception as e:
                excname = "Polling error: " + e.__class__.__name__
                num = (self.cols-len(excname))//2
                print("\033[1;31m" + "─" * num + excname + "─" * num + "\033[0m")
                tb.print_exception(e)
                print("\r\033[1;31mEmulator catched polling error\033[0m")
                fe = tb.format_exception(e)
                self.log("\n\n\nPolling error\n\n" + fe if type(fe) is str else ', '.join(fe) + "\n\n\n")
        
    def update(self):
        while self.block: time.sleep(0.1)
        self.block = True
        log = self.log
        log("Updating database")
        data = {}
        try:
            for table in self.table:
                log(f"Updating `{table}`")
                log(f"Raw table data: {self.table[table]}")
                datat = data[table] = [{**item} for item in self.table[table].all()[1:]]
                log(f"Table data: {datat}")
                types = {}
                for key, value in self.table[table].all()[0].items():
                    represented_type = repr(value).removeprefix('<class \'').removesuffix('\'>')
                    log(represented_type)
                    types[key] = represented_type
                log(f"Types: {types}")
                del types["id"]
                data[table] = [types] + datat
                log(f"Data: {data[table]}")
            
            with open(self.directory + "/db.json", "wt") as f:
                json.dump(data, f)
        except Exception as e:
            excname = "Updating error: " + e.__class__.__name__
            num = (self.cols-len(excname))//2
            print("\033[1;31m" + "─" * num + excname + "─" * num + "\033[0m")
            tb.print_exception(e)
            print("\r\033[1;31mEmulator catched updating error\033[0m")
            fe = tb.format_exception(e)
            self.log("\n\n\nUpdating error\n\n" + fe if type(fe) is str else ', '.join(fe) + "\n\n\n")
        self.block = False
