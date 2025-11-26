# TODO

- [ ] C
- [ ] R
- [ ] U
- [ ] D



# Intro

- SQLite是一个C库, 一个轻量级的本地磁盘数据库, 不需要额外的服务器; 使用非标准的SQL语句; 可以先用SQLite开发, 然后切换到更大的数据库上
- sqlite3是一个SQL driver

# Basic Tutorial

## Create Table

`sqlite3.connect(<db file>)`打开文件并且返回一个连接 (`sqlite3.Connection`), 如果文件不存在则会创建一个

>cursor是一个常用概念, 可以看成是iterator, 比如:
>
>- 数据库为1-10的整数
>- 通过SQL语句定义cursor为所有的奇数, 此时cursor将指向第一个结果
>- 通过一些操作, 可以移动cursor
>- 通过读取, 可以返回某一个奇数, 由其他语言继续处理

通过`connection.cursor()`可以创建一个database cursor, 通过这个cursor来执行语句, 例如: `cur.execute(<SQL>)`, 这个语句不返回什么. 执行后可以通过这个结果执行`fetchone, fetchall`等来获取结果

> 每个表 (还有其他的对象) 都含有一些 metadata (schema), 他们被储存在一个自带的默认的schema table里 (`sqlite_master`)

## Execute

cursor本身的地址不变, 所以应该执行一条SELCT语句, 然后就通过fetch查看; 如果连续执行多条SELECT语句, cursor会指向最后一个结果, 例如:

```python
res1 = cur.execute("SELECT title FROM movie")
print(res1.fetchall())
res2 = cur.execute("SELECT year FROM movie")
print(res2.fetchall())
```

> 正常情况下, execute后需要`connnection.commit()`来提交, 但默认情况下处于auto-commit模式. 
>
> 正常情况下, SQLite是transaction-based, 是原子的(可恢复的), 是串行化的 (并发结果和串行结果一样)
>
> 几乎所有SQL语句都在transaction中进行, 而且必须显示提交; 这很麻烦, 所以SQL driver可以将执行语句的过程自动wrap在事务中 (隐式的)
>
> 默认情况下, SQLite处于自动提交模式, sqlite3处于手动提交模式, 而sqlite3选择了implicitly wrap SQL in transaction

如果有很多要执行的语句, 一条一条执行很麻烦, 所以可以用`executemany()`来执行:

```python
data = [
    ("Monty Python Live at the Hollywood Bowl", 1982, 7.9),
    ("Monty Python's The Meaning of Life", 1983, 7.5),
    ("Monty Python's Life of Brian", 1979, 8.0),
]
cur.executemany("INSERT INTO movie VALUES(?, ?, ?)", data)

```

这里用了placeholder而非formatted-string, 这样可以防止SQL注入攻击

## Get Result

- `fetchone()`返回一个tuple, 包含了当前cursor指向的条目;
- `fetchall()`返回一个list, 包含所有条目; 
- `cursor`有`__next__(), _iter__()`, 所以可以用for循环来获取内容

## Quit

`con.close()`



# SQL Syntax (not only for SQLite)

## Create and Insert

下面是一个SQL的例子（不是SQLite）：

```sql
CREATE TABLE Employees (
    employee_id INT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    department_id INT,
    hire_date DATE DEFAULT CURRENT_DATE
);
```

创建一张表，括号里的每一行分别是：

1. 列名
2. 数据类型，例如整数，或者最大长度为50的字符串
3. 约束条件，例如非空，使用默认值，**设置为主键**

> 如果没有指定主键，不同的engine有不同的处理机制，如MySQL 的隐藏聚集键或 PostgreSQL 的 TID，但这是并非稳定、可引用的主键



使用`INSERT INTO`插入数据

```python
data = [(114, 24, 3000, 'ahh'),
        (514, 69, 5000, 'hunhunh')]
con.executemany("INSERT INTO t VALUES(?, ?, ?, ?)", data)
```

## Read by Select

## Update



## Delete

# Primary Key

SQLite会自动创建`ROWID`（一个**隐藏的、自动递增的、唯一的整数**，SQLite 内部用它来标识表中的每一行）。`SELECT ROWID FROM table`可以查看这个隐藏的主键。

如果想显式创建一个主键，可以用约束条件`INTEGER PRIMARY KEY`，这个列将变成`ROWID`的alias

如果不想用`ROWID`，可以用`WITHOUT ROWID`关闭它

# Datatypes

## SQLite Datatypes

大部分数据库是静态类型——但SQLite不是，这是个动态类型的engine。SQLite原生支持5种数据类型 (以及相应的Python类型)：

- NULL: None
- INTERGER: int
- REAL: float
- TEXT: str
- BLOB: bytes

> BLOB: Binary Large OBject

大多数数据库在创建表格时会指定每一列的数据类型，SQLite也可以指定，但这只是建议，而非强制。



## Custom Python types -> SQLite values

例如我想用数据库记录二维点坐标：

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

一种方法是为这个类编写一个`__conform__`函数:

```python
    def __conform__(self, protocol):
        if protocol is sqlite3.PrepareProtocol:
            return f"{self.x}-{self.y}"
```

另一种方法是注册一个adapter: 

```python
def adapt_point(obj):
    return f"{self.x}-{self.y}"

sqlite3.register_adapter(Point, adapt_point)
```

> 如何快速检验adapter的有效性？
>
> 1. 可以用`:memory:`作为数据库，而不是一个磁盘上的文件！
> 2. 可以不创建表，用`SELECT <constant>`来返回一个常量！

## SQLite values -> custom Python types

通过注册converter来转换：

```python
def convert_obj(s):
    x, y = map(float, s.split(b'-'))
    return Point(x, y)

sqlite3.register_converter("point", convert_obj)
```

> s总是一个bytes对象！

但是如何才能让sqlite3自动做转换呢？

**方法一：自定义数据类型**

在创建表时，可以用自定义的类型，如下所示；这个表的只有一个列，列中的值是`point`类型：

`CREATE TABLE t (p point)`

同时，在`connect`时需要传递一个参数：`detect_types=sqlite3.PARSE_DECLTYPES`，这样才会根据自定义的类型自动转化。

**方法二：使用列名称解析**

在`connect`时需要传递一个参数：`detect_types=sqlite3.PARSE_COLNAMES`，这样会根据列名来做解析。

如果想转化，就必须在SQL中这样写：`SELECT p AS "p [point]" FROM t`， 其中：

- query column name: must be wrapped by `double quote “”`
- type name: must be wrapped by `square bracket []`

> query column name指出现在结果集中的列名，如果SELECT不用AS，那original就是query；如果用了AS，那alias就是query

**方法三：组合使用！**

是的，connect函数可以传递`FLAG1 | FLAG2`，同时使用两种方法，不过 *根据列名解析* 的优先级更高

# Injection Attack

假设有一个用户数据库，使用明文密码，可以通过`SELECT * FROM t WHERE username=<username> AND password=<password>`来判断是否允许登录。

但如果直接用formatted string或者f-string：总之如果简单使用concatenate string，可能会遇到注入攻击，例如password为`123456 OR 1=1`，那么一定会登录成功。

sqlite3提供的解决方法是placeholder, 例如:

```python
execute("SELECT * FROM t WHERE name=? AND pwd=?", (arg1, arg2))
```

SQL语句会先发送给engine, 然后将其他的信息作为**arguments tuple**发送给engine。如果此时再尝试注入攻击，engine真的会搜索`123456 OR 1=1`，而不是执行语句。

有两种类型的placeholder，question mark style如之前所示，还有named style，例如:

```python
execute("SELECT * FROM t WHERE name=:name AND pwd=:pwd", 
       {'name': <name>, 
        'pwd': <pwd>})
```

# Reduce Cursor

- Connection对象也有`execute`系列方法, 不必使用Cursor对象
- `execute`系列方法会返回一个Cursor对象
- Cursor对象实现了 iterator protocol，所以可以直接用for循环

# Non UTF-8 Text

如果要处理的字符并非UTF-8，可以用str函数来转换：

```python
con.text_factory = lambda s: str(s, encoding='gbk')
```

> str函数还有errors参数， `errors="surrogateescape"`

# Row Factory

默认返回的列是一个tuple，有时候这不太方便，我们可能希望有一个dict，namedtuple，dataclass之类的对象

通过 `con.row_factory = sqlite3.Row` 可以设置返回的row的类型

## sqlite3.Row

这个类有以下特点：

1. 像list一样可迭代，可用下标访问（ `__iter__`, `__getitem__`）
2. 类似于dict，可以用 `keys()` 获取 query column name，进而可以用key来访问元素
3. **case-insensitive!**

## other (dict as an example)

```python
con.row_factory = a_factory_func
def a_factory_func(cursor, row):
    field =[col[0] for col cursor.desciption]
    return dict((field, row))
```

> `Cursor.description` 是一个property，返回一个tuple of 7-tuple，每个7-tuple按照DB API，元素包括 name, type_code等；对于SQLite，通常7-tuple中只有第一个元素有用（列名），其他的都是None

# SQLite URI

可以用URI形式打开数据库，例如`file:<filename>?key1=value1&key2=value2`

有几个常用的key：

1. mode
   1. ro: read only
   2. rw: read, write
   3. rwc: read, write, create if not exist
   4. memory: in memory, not disk
2. cache
   1. shared
   2. private

> SQLite 的 **Shared-Cache Mode**（共享缓存模式）是一种特殊的操作模式，旨在让**同一个进程内的多个数据库连接**能够共享对同一个数据库文件的**数据缓存 (Page Cache)** 和**模式信息 (Schema Cache)**。
>
> **核心作用和优势 (Core Function and Benefits)**
>
> 1. 内存和 I/O 减少 (Memory & I/O Reduction)
>
> - **减少内存消耗：** 在默认模式下，每个独立的数据库连接都会维护自己的数据页缓存。如果一个应用开启了 10 个连接来访问同一个数据库文件，它会维护 10 份独立的缓存。启用共享缓存后，这 10 个连接共享**同一份**缓存，显著减少了所需的总内存量。
> - **减少磁盘 I/O：** 当一个连接从磁盘读取一个数据页到共享缓存后，其他连接可以直接从内存中访问该数据页，而不需要再次从磁盘读取，从而减少了磁盘 I/O 操作。
>
> 2. 模式共享和一致性 (Schema Sharing)
>
> - **共享模式：** 所有连接共享同一份模式信息（表结构、索引定义等）。
> - **一致性：** 确保所有连接在同一时间看到的是数据库最新的、一致的结构定义。
>
> 3. 跨连接事务行为（更细粒度的锁定）
>
> 共享缓存模式下，SQLite 可以实现更细粒度的锁定，有助于在多个并发读取和写入操作之间进行协调，从而在某些情况下提高并发性。
>
> **⚠️ 特别适用场景 (Specific Use Case)**
>
> 共享缓存模式在以下场景中特别有用：
>
> - **嵌入式服务器/多线程应用：** 在资源受限的设备（如早期的手机操作系统、嵌入式系统）或需要同时处理多个数据库连接的服务器应用程序中，共享缓存可以大幅节省内存。
> - **内存数据库共享：** 如果您希望在应用程序的**多个连接之间共享一个 `:memory:`（内存）数据库**，则**必须**启用共享缓存模式（使用 `file::memory:?cache=shared`）。这是唯一能让多个连接访问同一个内存数据库的方法。
>
> **📢 重要提示：WAL 模式的出现**
>
> 虽然共享缓存模式有其优势，但 SQLite 官方在后来的版本中更推荐使用 **WAL Mode (Write-Ahead Logging)** 来解决并发读写和性能问题。
>
> - **历史背景：** 共享缓存模式（Shared-Cache Mode）最初是为了解决 SymbianOS 等旧平台上的内存限制而设计的。
> - **现代推荐：** 许多 SQLite 专家和文档现在**不鼓励**使用默认的共享缓存模式，而推荐使用 **WAL 模式**。WAL 模式在不牺牲并发性的情况下，提供了更好的性能和更稳定的读写隔离。
>
> **总结:**
>
> **SQLite Shared-Cache Mode 的主要作用**是允许同一个进程内的**多个连接共享同一个数据库的内存缓存**，以此达到**节省内存和减少 I/O**的目的，并实现多连接访问**内存数据库**。

## Context Manager

connection对象实现了上下文管理器协议 (`__enter__, __exit__`)，可以自动提交，也可以自动回滚+抛出异常，例如：

```python
with con:
    con.execute('......')
```

# Transaction Control

有两种控制方式：autocommit, isolation_level, 推荐使用前者

建议将 *autocommit* 设为 `False`，表示使用兼容 [**PEP 249**](https://peps.python.org/pep-0249/) 的事务控制。 这意味着：

- `sqlite3` 会确保事务始终处于开启状态，因此 [`connect()`](https://docs.python.org/zh-cn/3.12/library/sqlite3.html#sqlite3.connect) 、[`Connection.commit()`](https://docs.python.org/zh-cn/3.12/library/sqlite3.html#sqlite3.Connection.commit) 和 [`Connection.rollback()`](https://docs.python.org/zh-cn/3.12/library/sqlite3.html#sqlite3.Connection.rollback) 将隐式地开启一个新事务（对于后两者，在关闭待处理事务后会立即执行）。 开启事务时 `sqlite3` 会使用 `BEGIN DEFERRED` 语句。
- 事务应当显式地使用 `commit()` 执行提交。
- 事务应当显式地使用 `rollback()` 执行回滚。
- 如果数据库执行 [`close()`](https://docs.python.org/zh-cn/3.12/library/sqlite3.html#sqlite3.Connection.close) 时有待处理的更改则会隐式地执行回滚。

将 *autocommit* 设为 `True` 以启用 SQLite 的 [autocommit mode](https://www.sqlite.org/lang_transaction.html#implicit_versus_explicit_transactions)。 在此模式下，[`Connection.commit()`](https://docs.python.org/zh-cn/3.12/library/sqlite3.html#sqlite3.Connection.commit) 和 [`Connection.rollback()`](https://docs.python.org/zh-cn/3.12/library/sqlite3.html#sqlite3.Connection.rollback) 将没有任何作用。 请注意 SQLite 的自动提交模式与兼容 [**PEP 249**](https://peps.python.org/pep-0249/) 的 [`Connection.autocommit`](https://docs.python.org/zh-cn/3.12/library/sqlite3.html#sqlite3.Connection.autocommit) 属性不同；请使用 [`Connection.in_transaction`](https://docs.python.org/zh-cn/3.12/library/sqlite3.html#sqlite3.Connection.in_transaction) 查询底层的 SQLite 自动提交模式。

将 *autocommit* 设为 [`LEGACY_TRANSACTION_CONTROL`](https://docs.python.org/zh-cn/3.12/library/sqlite3.html#sqlite3.LEGACY_TRANSACTION_CONTROL) 以将事务控制行为保留给 [`Connection.isolation_level`](https://docs.python.org/zh-cn/3.12/library/sqlite3.html#sqlite3.Connection.isolation_level) 属性。 更多信息参见 [通过 isolation_level 属性进行事务控制](https://docs.python.org/zh-cn/3.12/library/sqlite3.html#sqlite3-transaction-control-isolation-level)。

> **总结：**
>
> 虽然 SQLite 默认是 `autocommit`，但最好的实践是**在需要保证多个操作是不可分割的逻辑单元或需要提升写入性能时，始终使用 `BEGIN` 和 `COMMIT` 来显式控制事务**。
>
> **原因：**
>
> 1. **数据完整性 (Data Integrity):** 如果一个操作序列（比如转账：A 账户减钱，B 账户加钱）中途失败，显式事务确保所有操作要么**全部成功 (COMMIT)**，要么**全部失败 (ROLLBACK)**，从而保持数据的一致性。
> 2. **性能提升 (Performance Improvement):** SQLite 写入磁盘是一个昂贵的操作。在 `autocommit` 模式下，每条 `INSERT`/`UPDATE`/`DELETE` 都会触发一次单独的磁盘写入。通过将多个操作包含在一个 `BEGIN/COMMIT` 块中，SQLite 可以将多次写入操作合并为**一次**高效的磁盘操作。对于批量插入尤其关键。
> 3. **原子性保证 (Atomicity):** 显式事务保证了操作的原子性。

# Notable Reference

## Module

### sqlite3.**threadsafety**

> [ref](https://docs.python.org/zh-cn/3.12/library/sqlite3.html#sqlite3.threadsafety)

整数常量，指明 `sqlite3` 模块支持的线程安全级别。 SQLite 的线程模式有:

- **Single-thread**: 在此模式下，所有的互斥都被禁用, 并且 SQLite 同时在多个线程中使用将是不安全的。
- **Multi-thread**: 在此模式下，只要单个数据库连接没有被同时用于两个或多个线程之中 SQLite 就可以安全地被多个线程所使用。
- **Serialized**: 在序列化模式下，SQLite 可以安全地被多个线程所使用而没有额外的限制。



## Connection

### cursor

这个函数可以接收一个factory，如果我想从Cursor继承一个更好的cursor，可以改变factory

### blobopen

用于blob，后续描述

### iterdump

可以用于将数据库转储为SQL源代码

```python
con = sqlite3.connect('example.db')
with open('dump.sql', 'w') as f:
    for line in con.iterdump():
        f.write('%s\n' % line)
con.close()
```

### backup

创建 SQLite 数据库的备份。

```python
src = sqlite3.connect('example.db')
dst = sqlite3.connect(':memory:')
src.backup(dst)
dst.close()
src.close()
```

### serialize, deserialize

将一个数据库序列化为 [`bytes`](https://docs.python.org/zh-cn/3.12/library/stdtypes.html#bytes) 对象。 对于普通的磁盘数据库文件，序列化就是磁盘文件的一个副本。 对于内存数据库或“临时”数据库，序列化就是当数据库备份到磁盘时要写入到磁盘的相同字节序列。

### autocommit

用于事务控制

## Cursor

### fetch, fetchmany, fetchall

获取内容

### arraysize

控制fetchmany的行数

### description

可用于获取query column name

### lastrowid

提供上一次插入的行的行 ID

### rowcount

提供 `INSERT`, `UPDATE`, `DELETE` 和 `REPLACE` 语句所修改行数的只读属性

### row_factory

改变row的类型

## Blob

file-like object，用于读写二进制

使用方法：

```python
con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE test(blob_col blob)")
con.execute("INSERT INTO test(blob_col) VALUES(zeroblob(13))")

# 写入到我们的 blob，使用两次 write 操作：
with con.blobopen("test", "blob_col", 1) as blob:
    blob.write(b"hello, ")
    blob.write(b"world.")
    # 修改我们的 blob 的开头和末尾字节
    blob[0] = ord("H")
    blob[-1] = ord("!")

# 读取我们的 blob 的内容
with con.blobopen("test", "blob_col", 1) as blob:
    greeting = blob.read()

print(greeting)  # 输出 "b'Hello, world!'"
con.close()
```

因为是file-like，所以可以用`len`, `read/write`，`seek`, `tell`, `close`, `__getitem__`等函数

## Exception

`sqlite3.Error`是所有异常的基类







