import sqlite3
import os


os.remove("./tutorial.db")
con = sqlite3.connect("tutorial.db")
cur = con.cursor()
print(dir(cur))
cur.execute("CREATE TABLE movie(title, year, score)")
cur.execute("""INSERT INTO movie VALUES
                ('Monty Python and the Holy Grail', 1975, 8.2),
                ('Whatever', 1975, 1.1),
                ('And Now for Something Completely Different', 1971, 7.5)
                """)

res1 = cur.execute("SELECT * FROM movie WHERE year = 1971"); print(res1.fetchall())

quit(0)