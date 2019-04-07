import socket
import threading
import time
from queue import Queue
import pickle
import tkinter
from tkinter import messagebox, LEFT, RIGHT, NORMAL, END, DISABLED, GROOVE
import os
import sqlite3

tLock = threading.Lock()
LARGE_FONT = ("Helvetica", 14)

server_IP = '127.0.0.1'  # Set server IP here

db_filename = 'Chat-client.db'
db_is_new = not os.path.exists(db_filename)
db = sqlite3.connect(db_filename, check_same_thread=False)
new_messages = []
old_new_messages = {}


class Client(tkinter.Tk):
    # Create a socket object
    host = socket.gethostname()  # Get local machine name

    def __init__(self, val, *a, **ka):
        self.port = val
        tkinter.Tk.__init__(self, *a, **ka)
        self.title("CHAT APP")
        self.container = tkinter.Frame(self)
        self.container.pack()
        self.create_startpage(val)
        self.resizable(0, 0)

    def create_startpage(self, val):
        self.signin = StartPage(self.container, self)
        self.signin.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.s.connect((server_IP, self.port))
                break
            except Exception as e:
                print(e)
                time.sleep(5)

    def listener(self, s):
        try:
            while True:
                rec = s.recv(4000)
                arr = rec.split(b'.')
                for a in range(len(arr) - 1):
                    new = pickle.loads(arr[a] + b'.')
                    if new[0] == 1 and new[1][0].capitalize() in self.users:
                        self.q.put((1, new[1][0].capitalize(), new[1][1]))


                    elif new[0] == 2:
                        self.users = []
                        self.online_users = []
                        for str in new[1]:
                            self.online_users.append(str.capitalize())
                            try:
                                if self.blocked_users[str.capitalize()]:
                                    pass
                            except:
                                self.users.append(str.capitalize())
                                pass
                        self.users.remove(self.client.capitalize())

                        self.mainpage.update()
                        pass
                    elif new[0] == 3:
                        print("No such user " + new[1])
                    elif new[0] == 4:
                        self.users = []
                        self.online_users = []
                        for str in new[1][1]:
                            self.blocked_users[str[0].capitalize()] = 1
                            self.mainpage.unblock.add_command(label=str[0].capitalize(),
                                                              command=lambda str=str[0].capitalize(): self.unblock_it(
                                                                  str))
                        for str in new[1][0]:
                            self.online_users.append(str.capitalize())
                            try:
                                if self.blocked_users[str.capitalize()]:
                                    pass
                            except:
                                self.users.append(str.capitalize())
                                pass
                        self.users.remove(self.client.capitalize())
                        self.mainpage.update()

        except ConnectionResetError:
            messagebox.showerror("Error", "Server stopped")
            self.destroy()
        except ConnectionAbortedError as e:
            print(e)
            pass

    def log_in(self):
        try:
            s = self.s
            username = self.signin.entry_1.get()
            password = self.signin.entry_2.get()
            username = username.strip()
            password = password.strip()
            login_details = (username.lower(), password)
            new = pickle.dumps(login_details, -1)
            s.send(new)
            reply = s.recv(1024)
            ans = pickle.loads(reply)
            if ans == 0:
                print("Incorrect Password")
                messagebox.showerror('Incorrect Password')

            elif ans == -1:
                print("Username Doesn't Exist")
                messagebox.showerror("Username Doesn't Exist")
            elif ans == -2:
                print("Already logged in")
                messagebox.showerror("Already logged in")
            elif ans == 1:
                print("Connected")
                self.client = username.lower()
                self.users = []
                self.online_users = []
                self.blocked_users = {}
                self.to = None
                self.q = Queue()
                self.mainpage = MainPage(self.container, self)
                self.mainpage.grid(row=0, column=0, sticky='nsew')
                self.signin.destroy()
                self.tkraise(self.mainpage)
                lT = threading.Thread(target=self.listener, args=[s], name='Listener')
                lT.daemon = True
                lT.start()


        except ConnectionResetError:
            messagebox.showerror("Error", "Server stopped")
            self.destroy()

    def send_it(self):
        s = self.s
        string = self.mainpage.text.get(1.0, 'end-1c')
        string = string.strip()
        if string != '' and self.to is not None:
            self.q.put((2, 'You', string))
            arr = []
            b = 0
            for a in range(len(string)):
                if string[a] == '.':
                    arr.append(a)
            string = string.replace('.', '')
            message = (1, self.to.lower(), (arr, string))
            message = pickle.dumps(message, -1)
            s.send(message)


            new_messages.append((self.to, 2, string))

            self.mainpage.text.delete(1.0, tkinter.END)
        pass

    def block_it(self):
        s = self.s
        self.blocked_users[self.mainpage.menu_active] = 1
        self.mainpage.chats[self.mainpage.menu_active][0].destroy()
        self.mainpage.chats[self.mainpage.menu_active][1].destroy()
        self.mainpage.chats.pop(self.mainpage.menu_active)
        self.users.remove(self.mainpage.menu_active)
        self.mainpage.unblock.add_command(label=self.mainpage.menu_active,
                                          command=lambda str=self.mainpage.menu_active: self.unblock_it(str))
        self.mainpage.update()
        message = (2, self.mainpage.menu_active.lower())
        message = pickle.dumps(message, -1)
        s.send(message)

    def unblock_it(self, str):
        self.blocked_users.pop(str)
        index = self.mainpage.unblock.index(str)
        self.mainpage.unblock.delete(index, index)
        if str in self.online_users:
            self.users.append(str)
            self.mainpage.update()
        s = self.s
        message = (3, str.lower())
        message = pickle.dumps(message, -1)
        s.send(message)

    def log_out(self):
        for to, no, message in new_messages:
            db.execute('insert into {}_{} values(?,?)'.format(a.client, to), (no, message))
        try:
            self.s.close()
        except Exception as e:
            print(e)
        db.commit()
        new_messages.clear()
        self.mainpage.destroy()
        self.q.put((-1, 0, 0))
        self.mainpage.chats.clear()
        self.create_startpage(self.port)


class StartPage(tkinter.Frame):
    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        label_1 = tkinter.Label(self, text='Username')
        label_2 = tkinter.Label(self, text='Password')
        self.entry_1 = tkinter.Entry(self)
        self.entry_2 = tkinter.Entry(self, show="*")
        self.entry_1.bind("<Return>", lambda e: controller.log_in())
        self.entry_2.bind("<Return>", lambda e: controller.log_in())
        label_1.grid(row=0)
        label_2.grid(row=1)
        self.entry_1.grid(row=0, column=1)
        self.entry_2.grid(row=1, column=1)
        button = tkinter.Button(self, bg ='#00A86B', text='Log In', command=controller.log_in)
        button.grid(row=2, columnspan=2)


class MainPage(tkinter.Frame, threading.Thread):
    def __init__(self, parent, controller):
        threading.Thread.__init__(self)
        tkinter.Frame.__init__(self, parent)
        self.controller = controller

        menu = tkinter.Menu(self, tearoff=0)
        menu.add_command(label=u'Block', command=lambda: self.controller.block_it())
        menu.add_command(label=u'Delete All Message', command=lambda: self.clear_messages())

        menubar = tkinter.Menu(self)
        self.unblock = tkinter.Menu(self, tearoff=0)
        menubar.add_cascade(label='Unblock', menu=self.unblock)
        self.controller.config(menu=menubar)

        self.sideframe = tkinter.Frame(self)
        self.listbox = tkinter.Listbox(self.sideframe)
        self.listbox.pack(fill=tkinter.BOTH, expand=True, side=tkinter.TOP, pady=5)
        self.listbox.bind("<1>", lambda e: self.rename_1(e))
        aqua = self.controller.call('tk', 'windowingsystem') == 'aqua'
        self.listbox.bind('<2>' if aqua else '<3>', lambda e: self.listbox_menu(e, menu))
        self.listbox.bind("<Key>", self.no_op)
        self.label = tkinter.Label(self.sideframe, text=self.controller.client.capitalize())
        self.logout = tkinter.Button(self.sideframe, text="Log Out", command=self.controller.log_out)
        self.logout.pack(side=RIGHT)
        self.label.pack(side=LEFT)
        self.sideframe.grid(row=0, rowspan=3, column=0, sticky='nswe', padx=5, pady=5)
        self.current = tkinter.Label(self)
        self.current.grid(row=0, column=1, pady=5, )
        self.chats = {}
        self.text = tkinter.Text(self, font=LARGE_FONT, height=2, width=50)
        self.text.grid(row=2, sticky='nswe', column=1, padx=5, pady=5)
        self.text.bind("<Return>", lambda e: self.controller.send_it())
        self.button = tkinter.Button(self, bg ='#00A86B', fg='white', font ='none 10 bold underline', text="Send", command=self.controller.send_it)
        self.button.grid(row=2, sticky='w', column=2)
        self.begin = 1
        self.daemon = True
        self.start()

    def clear_messages(self):
        self.chats[self.menu_active][0].config(state=NORMAL)
        self.chats[self.menu_active][0].delete('1.0', END)
        self.chats[self.menu_active][0].config(state=DISABLED)
        db.execute("DELETE FROM {}_{}".format(self.controller.client, self.menu_active))
        db.commit()
        arr = []
        for item in new_messages:
            if item[0] == self.menu_active:
                arr.append(item)
        for item in arr:
            new_messages.remove(item)

        pass

    def listbox_menu(self, event, menu):
        if self.listbox.size() == 0:
            return
        widget = event.widget
        index = widget.nearest(event.y)
        _, yoffset, _, height = widget.bbox(index)
        if event.y > height + yoffset + 5:  # XXX 5 is a niceness factor :)
            # Outside of widget.
            return
        item = widget.get(index)
        self.menu_active = item
        menu.post(event.x_root, event.y_root)

    def no_op(self, event):
        return "break"

    def run(self):

        while True:
            rec = self.controller.q.get()
            if rec[0] == 1:
                try:
                    self.chats[rec[1]]
                    main = self.chats[rec[1]][0]
                except:
                    s = tkinter.Scrollbar(self)
                    s.grid(row=1, column=3, sticky='ns')
                    main = tkinter.Text(self, height=10, width=50, font=LARGE_FONT)
                    main.grid(row=1, columnspan=2, column=1, sticky='nswe', padx=5, pady=5)
                    s.config(command=main.yview)
                    main.config(yscrollcommand=s.set)
                    main.lower()
                    s.lower()
                    main.configure(bg=self.cget('bg'), relief=GROOVE, state='disabled')
                    main.tag_config('other', foreground='red')
                    main.tag_config('me', foreground='green', justify=RIGHT, lmargin1=100)
                    main.tag_config('justify', lmargin2=100)
                    self.chats[rec[1]] = (main, s)
                    pass
                main.configure(state='normal')
                main.insert(END, rec[1], 'other')
                str = rec[2][1]
                if len(rec[2][0]) != 0:
                    str = rec[2][1][:rec[2][0][0]]
                    for a in range(len(rec[2][0])):
                        if a != len(rec[2][0]) - 1:
                            str = str + '.' + rec[2][1][rec[2][0][a] - a:rec[2][0][a + 1] - a - 1]
                        else:
                            str = str + '.' + rec[2][1][rec[2][0][a] - a:]
                new_messages.append((rec[1], 1, str))
                main.insert(END, ': ' + str + '\n')
                main.configure(state='disabled')
                main.see(END)
            elif rec[0] == 2:
                main = self.chats[self.controller.to][0]
                main.configure(state='normal')
                main.insert(END, rec[1], 'me')
                main.insert(END, ': ' + rec[2] + '\n', 'justify')
                main.configure(state='disabled')
                main.see(END)
            elif rec[0] == -1:
                break
        pass

    

    def old_messages(self, dat, user):

        main = self.chats[user][0]

        for sender, message in dat:
            if sender == 2:
                main.configure(state='normal')
                main.insert(END, 'You', 'me')
                main.insert(END, ': ' + message + '\n')
                main.configure(state='disabled')
            else:
                main.configure(state='normal')
                main.insert(END, user, 'other')
                main.insert(END, ': ' + message + '\n')
                main.configure(state='disabled')
                pass
        main.see(END)

        pass

    def rename_1(self, event):

        if self.listbox.size() == 0:
            return
        index = self.listbox.nearest(event.y)
        _, yoffset, _, height = self.listbox.bbox(index)
        if event.y > height + yoffset + 5:  # XXX 5 is a niceness factor :)
            return
        self.controller.to = self.listbox.get(index)
        self.current.config(text=self.controller.to)
        main = self.chats[self.controller.to][0]
        temp = self.chats[self.controller.to][1]
        main.grid(row=1, columnspan=2, column=1, sticky='nswe', padx=5, pady=5)
        temp.grid(row=1, column=3, sticky='ns')
        temp.lift()
        main.lift()

    def update(self):


        self.listbox.delete(0, END)

        for user in self.controller.users:
            try:
                self.chats[user]
                self.chats[user][0].grid(row=1, columnspan=2, column=1, sticky='nswe', padx=5, pady=5)
                self.chats[user][1].grid(row=1, column=3, sticky='ns')
                self.listbox.insert(END, user)

            except:
                s = tkinter.Scrollbar(self)
                temp = tkinter.Text(self, height=10, width=50, font=LARGE_FONT)
                temp.grid(row=1, columnspan=2, column=1, sticky='nswe', padx=5, pady=5)
                s.grid(row=1, column=3, sticky='ns')
                s.config(command=temp.yview)
                temp.config(yscrollcommand=s.set)
                temp.lower()
                s.lower()

                temp.configure(bg=self.cget('bg'), relief=GROOVE, state='disabled')
                temp.tag_config('other', foreground='blue')
                temp.tag_config('me', foreground='green', justify=RIGHT, lmargin1=100)
                temp.tag_config('justify', lmargin2=100, lmargin1=100)
                self.chats[user] = (temp, s)
                self.listbox.insert(END, user)
                try:
                    cur = db.cursor()
                    cur.execute("""select * from {}_{}""".format(self.controller.client, user))
                    dat = cur.fetchall()
                    self.old_messages(dat, user)


                    pass
                except:
                    db.execute(
                        'create table {}_{}( sender INT, message VARCHAR(4000))'.format(self.controller.client, user))
                    pass



        if len(self.controller.users) == 0:
            self.controller.to = None
            self.current.config(text='')
            self.button.configure(state='disabled')
            for a in list(self.chats.keys()):
                self.chats[a][0].grid_forget()
                self.chats[a][1].grid_forget()
            pass
        else:
            if self.controller.to not in self.controller.users:
                self.controller.to = self.listbox.get(0)
                self.current.config(text=self.controller.to)
                self.listbox.activate(0)
                self.chats[self.controller.to][0].grid(row=1, columnspan=2, column=1, sticky='nswe', padx=6, pady=6)
                self.chats[self.controller.to][1].grid(row=1, column=3, sticky='ns')
                self.chats[self.controller.to][0].lift()
                self.chats[self.controller.to][1].lift()
                self.button.configure(state='normal')
                pass
            else:
                pass



if __name__ == '__main__':

    a = Client(12345)
    a.mainloop()



    for to, no, message in new_messages:

        db.execute('insert into {}_{} values(?,?)'.format(a.client, to), (no, message))

    try:
        a.s.close()
    except Exception as e:
        print(e)
    db.commit()
    new_messages.clear()
    db.close()
