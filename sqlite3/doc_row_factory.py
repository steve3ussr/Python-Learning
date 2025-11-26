import sqlite3
from dataclasses import dataclass


@dataclass
class StuffWage:
    name: str
    wage: int
    all_info: dict


def stuff_wage_factory(c: sqlite3.Cursor, r: tuple):
    col = [_[0] for _ in c.description]
    return StuffWage(name=r[3], wage=r[2]+10*r[1], all_info=dict(zip(col, r)))

con = sqlite3.connect(":memory:")
con.row_factory = stuff_wage_factory
con.execute("CREATE TABLE t("
            "id INTEGER PRIMARY KEY,"
            "age INT,"
            "base_salary INT,"
            "name TEXT"
            ")")
data = [(24, 3000, 'ahh'),
        (69, 5000, 'hunhunh')]
con.executemany("INSERT INTO t(age, base_salary, name) VALUES(?, ?, ?)", data)
for _ in con.execute("SELECT * FROM t"):
    print(_)



