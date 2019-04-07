import os
import sqlite3
from Admin import monitor

db_data = 'chat_data.db'
user_db = 'Chat-server.db'
if not os.path.exists(db_data):
    db = sqlite3.connect(db_data, timeout=10, check_same_thread=False)

conn = sqlite3.connect(db_data, timeout=10)
db = sqlite3.connect(user_db, timeout=10)
cur = conn.cursor()
user_cur = db.cursor()
wordfrq = []

with db:
    user_cur.execute('select username from credentials')
    usernames = user_cur.fetchall()

with conn:
    for n in range(len(usernames)):
        for x in range(n + 1, len(usernames)):
            cur.execute("""
            select * from monitoring_data  where 
            sender = '{tn}' and receiver = '{tb}' 
             or                       
             sender = '{tb}' and receiver = '{tn}'
            """.format(tb=usernames[n][0], tn=usernames[x][0]))
            data = cur.fetchall()
            newdat = []
            dataList = []
            if data:
                currentdata = usernames[n][0] + ' and ' + usernames[x][0]
                for each in data:
                    for x in each[2].split():
                        dataList.append(x.lower())

                    newdat.append(each[2])

                dataSet = set(newdat)

#                monitor(dataList, currentdata)
                # print(dataSet)
