# ViDB - A database based on JSON made by Vi

## What is ViDB?

ViDB is a database based on JSON made by Vi. It is a simple and fast database that can be used to store and retrieve data in a JSON format. It is designed to be easy to use.

## How to use ViDB?

To create a database, you need to create a file named `db.json`.
You need to create a file named `config.vidb` in the same directory as `db.json`, it is JSON.
Next you can use ViDB Emulator to initialize the database.

## How to use ViDB Emulator?

ViDB Emulator is a command-line tool that can be used to initialize a ViDB database.
To use ViDB Emulator, you need to have Python installed on your system.

To install ViDB Emulator, you can use the following command:

```bash
git clone https://github.com/vivavy/vidb.git
```

Once ViDB Emulator is installed, you can use the following command to initialize a ViDB database:

```bash
vidb start .
```

This command will start ViDB Emulator in current directory (you can write custom directory name instead of `.`).

Now, you can create, delete and change data in the database using ViDB Emulator.

## What command can I use in ViDB Emulator?

### Create a new table

To create a new table, you can use the following command:

```python
db.table.create("tabe_name", {"field_name": field_type})
```

For example, to create a table named `users`, you can use the following command:

```python
db.table.create("users", {
    "name": string, 
    "age": int
})
```

Note: field `id` is automatically created by ViDB Server and it is autoincrementing primary key.

### Insert data into a table

To insert data into a table, you can use the following command:

```python
db.users.insert({
    "name": "John Doe",
    "age": 30
})
```

Also, you can use the following command to insert multiple rows at once:

```python
db.users.insert([  
    {
        "name": "John Doe",
        "age": 30
    },
    {
        "name": "Jane Doe",
        "age": 25
    }
])
```

### Update data in a table

To update data in a table, you can use the following command:

```python
db.users[0].update({
    "name": "John Smith"
})
```

### Delete data from a table

To delete data from a table, you can use the following command:

```python
del db.users[0]
```

## How to use ViDB in Python?

To use ViDB in Python, you need to install the `vidb` package using vipip3.

To install `vidb` package, you can use the following command:

```bash
vipip3 install vidb
```

Once `vidb` package is installed, you can use the following code to initialize a ViDB database:

```python
from vidb import ViDB

db = ViDB(".")
```

Now, you can use the `db` object to create, delete and change data in the database.

For example:

```python
from vidb import ViDB

db = ViDB(".")

# Create a new table named "users"
db.table.create("users", {
    "name": str,
    "age": int
})

# Insert data into the "users" table
db.users.insert({
    "name": "John Doe",
    "age": 30
})

# Update data in the "users" table
db.users[0].update({
    "name": "John Smith"
})

# Delete data from the "users" table
del db.users[0]
```

## Also, you can select entries from a table by some conditions

To select entries from a table by some conditions, you can use the following code:

```python
# Select all entries from the "users" table
adults = db.Table.users.select(lambda entry: entry["age"] > 18)

# this code will put all entries from the "users" table that have age greater than 18 into the "adults" variable

print(adults)
# >>> [{"id": 1, "name": "John Smith", "age": 30}, {"id": 2, "name": "Jane Doe", "age": 25}]
```

## Also, you can merge this method with any other Python modules, for example, re:

```python
import re

# Select all entries from the "users" table
adults = db.users.select(lambda entry: re.search(r".*S.*", entry["name"]))

print(adults)
# >>> [{"id": 1, "name": "John Smith", "age": 30}]
```

## Also, you can use the `.all()` method to get all entries from a table
```python
# Select all entries from the "users" table
all_users = db.Table.users.all()

print(all_users)
# >>> [{"id": 1, "name": "John Smith", "age": 30}, {"id": 2, "name": "Jane Doe", "age": 25}]
```

## After all, you can create vidbrc file in the same directory as `db.json` file, that will be executed every time you start ViDB Server or Emulator

For example:

```python
# vidbrc file
import re, math
# now you can use this modules in your requests
```

be careful, some modules or actions can be prohibited by ViDB Server for security reasons

for example, you can not use modules like `threading`, `os`, `sys` or `multiprocessing` in server.

BUT! you can use them in Emulator. It made for more flexible and easy initialization of ViDB Server.

Attention: ViDB Emulator can not be used while ViDB Server is running. Also, when you modify DB in your code, don't forget to make request to ViDB Server `db.upload()` to update DB on server.

For actual data in your code in used requests in parallel, you can call `db.poll()` to update DB in parallel.

That's all, enjoy ViDB!
