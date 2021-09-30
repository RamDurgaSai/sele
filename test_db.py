from time import localtime

from Data import DataBase
import json

data = DataBase(file="test.db")

with open("programs.json", mode="r", encoding="utf-8") as program:
    programs = json.load(program)

data.create_tables(*programs)


year, month, day, hour, minute, second, wd, yd, isd = localtime()
date = 10_000*year + 100*month + day
# for key,value in programs.items():
#
#     data.insert(table=key,date=date+10,
#         info =  str({f"tilte: {key}"}),
#         path =  f"Downloads/{key}.mp4",
#         pdisk = f"www.psidk.com/{key}",
#         )
for key,value in programs.items():
    info = "info"
    pdisk = "pdisk"
    path = "path"
    d = data.select("*",table=key,date = 202109030)
    print(d)
    if len(d) == 0:
        print("empty")
    else:
        print("not empty")

