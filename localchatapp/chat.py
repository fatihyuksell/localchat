from tkinter import *
from tkinter import scrolledtext, WORD, END, INSERT
from threading import Thread
from playsound import playsound
import socket, time, os

log_msg = ''
chat_history = ''
connected = False
class GUI:
    def __init__(self, ip='127.0.0.2'):
        self.base_ip = ip
        self.target_ip = ''
        self.chat_history = ''
        self.running = True
        self.udp_connected = False
        self.sound_opened = False
        self.build_server_thread = Thread(target=self.build_server)
        self.chat_gui_thread = Thread(target=self.create_chat_gui)
        self.sound_thread = Thread(target=self.create_sound_gui)


    def build_server(self):
        # TCP Listener (Server)
        if self.conn_type==1:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.base_ip, 80))
            sock.listen(5)

            self.client_socket, addr = sock.accept()
            while True:
                data = self.client_socket.recv(1024)
                if data:
                    if '#_Sound_#' in data.decode().split('$$$'):
                        sound_index = data.decode().split('$$$')[1]
                        self.play_sound(sound_index)
                    else:
                        self.chat_history += f'Partner: {data.decode()}'
                        self.update_chat_textbox()
                data = None

            self.client_socket.close()

        # UDP Listener (Server)
        if self.conn_type==2:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.base_ip, 80))

            while True:
                # accept connections from outside
                data, address = sock.recvfrom(4096)
                if data:
                    if data.decode() == 'waiting':
                        self.udp_connected = True
                    elif '#_Sound_#' in data.decode().split('$$$'):
                        sound_index = data.decode().split('$$$')[1]
                        self.play_sound(sound_index)
                    else:
                        self.chat_history += f'Partner: {data.decode()}'
                        self.update_chat_textbox()
                data = None

    def connect(self, ip, conn_type):
        if conn_type==1:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if conn_type==2:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if conn_type == 1:
            while self.running:
                try:
                    sock.connect((ip, 80))
                except Exception as e: 
                    pass
                else:
                    return sock
        if conn_type == 2:
            sock.connect((ip, 80))
            while not self.udp_connected:
                sent = sock.send(b'waiting')
            sent = sock.send(b'waiting')
            return sock

    def update_chat_textbox(self):
        self.chat_textbox.config(state='normal')
        self.chat_textbox.delete(1.0,END)
        self.chat_textbox.insert(INSERT, self.chat_history)

    def login_click_handler(self, e, r_vals, log_label):
        global log_msg, connected
        self.conn_type = r_vals
        ip = e.get()
        if ip==self.base_ip:
            log_label['text']   = 'This is your ip you cant use this ip'
            return            

        # Building own server
        self.build_server_thread.start()
        log_label['text']   = 'Waiting to Connection Partner'
        # Try to connect other computer
        self.sock =  self.connect(ip, r_vals)
        if self.sock:
            connected = True
            log_label['text'] = ''

            # Open the chat gui
            self.chat_gui_thread.start()

    def send_click_handler(self, e):
        global chat_history
        text = e.get('1.0', END)
        self.new_msg_textbox.delete(1.0,END)
        self.chat_history += f'You: {text}'
        self.update_chat_textbox()
        self.sock.send(str(text).encode())

    def sound_click_handler(self):
        if not self.sound_opened:
            self.sound_opened = False
            self.create_sound_gui()
            #self.sound_thread.start()

    def on_close(self):
        try:
            self.running = False
            try:
                self.client_socket.close()
                self.build_server_thread.join()
            except:pass
            self.chat_gui_thread.join()
        except : pass 
        self.login_window.destroy()

    def play_sound(self, index):
        try:
            playsound(f'sounds/{index}.wav')
            time.sleep(1)
        except:
            time.sleep(1)

    def sound_on_close(self):
        self.sound_window.destroy()
        self.sound_opened = False

    def create_sound_gui(self):
        def send_sound(index):
            self.sock.send(f'#_Sound_#$$${index}'.encode())

        self.sound_window = Tk()
        self.sound_window.protocol("WM_DELETE_WINDOW", self.sound_on_close)
        self.sound_window.geometry('480x100')
        self.sound_window.title("Select The Sound")
        self.sound_window.resizable(width=False, height=False)
       
        btn_1 = Button(self.sound_window,height=6, width=10, text="1", command=lambda:send_sound(1))
        btn_2 = Button(self.sound_window,height=6, width=10, text="2", command=lambda:send_sound(2))
        btn_3 = Button(self.sound_window,height=6, width=10, text="3", command=lambda:send_sound(3))
        btn_4 = Button(self.sound_window,height=6, width=10, text="4", command=lambda:send_sound(4))
        btn_5 = Button(self.sound_window,height=6, width=10, text="5", command=lambda:send_sound(5))
        btn_6 = Button(self.sound_window,height=6, width=10, text="6", command=lambda:send_sound(6))
            
        # Placing Gui Elements
        btn_1.grid(row=1, column=1)
        btn_2.grid(row=1, column=2)
        btn_3.grid(row=1, column=3)
        btn_4.grid(row=1, column=4)
        btn_5.grid(row=1, column=5)
        btn_6.grid(row=1, column=6)

        self.sound_window.mainloop()

    def create_login_gui(self):
        self.login_window = Tk()
        self.login_window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.login_window.geometry('500x200')
        self.login_window.title("Chat Client Login")
        selected = IntVar()

        # Creating Gui Elements
        main_label = Label(self.login_window, text='Chat Project', font=("Arial Bold", 22)) 
        ip_label = Label(self.login_window, text="Enter Destination IP:")
        pr_label = Label(self.login_window, text="Protochol:")
        ip_txt = Entry(self.login_window, width=25)
        ip_txt.insert(0, '127.0.0.1')
        rad1 = Radiobutton(self.login_window,text='TCP', value=1, variable=selected)
        rad2 = Radiobutton(self.login_window,text='UDP', value=2, variable=selected)
        log_label = Label(self.login_window, fg='red', text=log_msg)
        cnn_btn = Button(self.login_window, width=30, text="Start Connection =>", command=lambda: Thread(target=self.login_click_handler, args=(ip_txt, selected.get(), log_label)).start())
            

        # Placing Gui Elements
        main_label.place(relx=0.3, rely=0.2, anchor='sw')
        ip_label.place(relx=0.01, rely=0.4, anchor='sw')
        pr_label.place(relx=0.06, rely=0.53, anchor='sw')
        ip_txt.place(relx=0.3, rely=0.4, anchor='sw')
        rad1.place(relx=0.3, rely=0.55, anchor='sw')
        rad2.place(relx=0.5, rely=0.55, anchor='sw')
        cnn_btn.place(relx=0.25, rely=0.7, anchor='sw')
        log_label.place(relx=0.25, rely=0.8, anchor='sw')

        self.login_window.mainloop()

    def create_chat_gui(self):
        global chat_history
        self.chat_window = Tk()
        self.chat_window.geometry('550x500')
        self.chat_window.title("Chat Client")

        self.chat_textbox = scrolledtext.ScrolledText(self.chat_window, width=78,height=20)
        self.chat_textbox.insert(INSERT, chat_history)
        self.chat_textbox.config(state=DISABLED)
        self.new_msg_textbox = scrolledtext.ScrolledText(self.chat_window, wrap=WORD, width=40, height=8)
        self.btn_send = Button(self.chat_window, width=9, height=8, text="Send", 
            command=lambda: self.send_click_handler(self.new_msg_textbox))
        btn_music  = Button(self.chat_window, width=7, height=8, text="♪",
            command=lambda: self.sound_click_handler())
        btn_browse = Button(self.chat_window, width=9, height=8, text="Browse")

        self.chat_textbox.grid(column=0,row=0)
        self.new_msg_textbox.place(relx=0.01, rely=0.94, anchor='sw')
        self.btn_send.place(relx=0.6, rely=0.94, anchor='sw')
        btn_music.place(relx=0.74, rely=0.94, anchor='sw')
        btn_browse.place(relx=0.85, rely=0.94, anchor='sw')

        self.chat_window.mainloop()


g = GUI()

working = True
g.create_login_gui()
os._exit(1)
#Thread(target=g.create_login_gui).start()

