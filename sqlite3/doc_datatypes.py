import sqlite3


class Info:
    def __init__(self, n: int, value: float, desc: str):
        self.n = n
        self.value = value
        self.desc = desc.replace('-', '.')

    def __conform__(self, proto):
        if proto is sqlite3.PrepareProtocol:
            return f"{self.n}-{self.value}-{self.desc}"
        else:
            raise SyntaxError(f"Cannot adapt <Info object> to protocol: {proto}")

    def __repr__(self):
        return f"<number: {self.n}, value: {self.value}, description: {self.desc}>"

    __str__ = __repr__

def adapt_info(info_obj: Info):
    return f"{info_obj.n}-{info_obj.value}-{info_obj.desc}"

def convert_info(b):
    print(type(b), b)
    bytes_list = b.split(b'-')
    return Info(n=int(bytes_list[0]),
                value=float(bytes_list[1]),
                desc=bytes_list[2].decode())


inst1 = Info(114, 114.514, 'huh, huh')
inst2 = Info(514, 18.19810, 'Ahhhh!')

sqlite3.register_adapter(Info, adapt_info)
sqlite3.register_converter('info', convert_info)

con = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
con.execute("CREATE TABLE t("
            "info_id INT PRIMARY KEY, "
            "content info"
            ")")
con.execute("INSERT INTO t(content) VALUES(?)", (inst1, ))

_tmp_cur = con.execute("SELECT * FROM t")
print(con.fetchone())
con.close()