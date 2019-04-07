import os
import sqlite3

db_data = 'chat_data.db'
if not os.path.exists(db_data):
    db = sqlite3.connect(db_data, timeout=10, check_same_thread=False)

conn = sqlite3.connect(db_data, timeout=10)
cur = conn.cursor()


def boss():
    sender = input('Chat between ---->  ')
    receiver = input('And ----->  ')
    try:
        with conn:
            cur.execute("""
            select * from monitoring_data  where 
            sender = '{tn}' and receiver = '{tb}' 
             or                       
             sender = '{tb}' and receiver = '{tn}'
            """.format(tb=sender.lower(), tn=receiver.lower()))
            data = cur.fetchall()

            cur.execute("""
            
                select * from userdetails where username = '{tr}' or username = '{tg}'            
            """.format(tr=sender, tg=receiver)
                        )
            details = cur.fetchall()
    except Exception as e:
        print('#---->  Please check the name spelling well  <----#')

    if data == []:
        print('#---->  Please check the name spelling well  <----#')

    if data:
        print(details)
        print('sender \t |        ', '(message)           \t |', 'receiver\t ')
        print('############################################################')
        for each in data:
            print(each[0], '\t', '(', each[2], ')', '\t', each[1], '\t')


boss()
