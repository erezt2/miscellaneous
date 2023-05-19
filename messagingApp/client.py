import time
import tkinter as tk, socket, select, pickle, re
from tkinter import messagebox

IP = "127.0.0.1"
PORT = 60101
BG_COLOR = "#171B20"
TEXT_COLOR = "#b1b9c4"
FONT = "Consolas"
INPUT_COLOR = "#25272e"
frames = {}
offline_test = False


class Globals:  # i know this is lazy programming. sue me
    message = ""
    name = ""
    socket_reference = None
    text_box = None


class Message:
    pass


def beautify_text(string):  # remove wrapping spaces or multiple next lines in a row
    string = string.strip("\n ")
    string = re.sub(r"\n{2,}", "\n\n", string)
    return string


def login(*args):  # socket handshake client
    args = list(map(lambda x: x if isinstance(x, str) else x.get(), args))

    # login/ chat group creation parameters
    name = args[1]
    if args[0] == "create":
        if name:
            messagebox.showerror("name error", "chat ID should be empty when creating chat")
            return
    else:
        match = re.match(r"^[0-9]+$", name)
        if not match or 4 > len(name) or len(name) > 5:
            messagebox.showerror("name error", "invalid chat ID\n(4-5 digits)")
            return

    name = args[2]
    match = re.match(r"^[a-zA-Z0-9!-*]+$", name)
    if not match or 5 > len(name) or len(name) > 16:
        messagebox.showerror("name error", "invalid chat password\n5-16 characters\nonly english numbers or shift+[0-8] characters")
        return

    name = args[3]
    match = re.match(r"^[a-zA-Z0-9]+$", name)
    if not match or 3 > len(name) or len(name) > 16:
        messagebox.showerror("name error", "invalid username:\n3-5 characters\nonly english or numbers")
        return

    if not offline_test:
        try:
            #  connect to server
            skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            skt.connect((IP, PORT))
            skt.send("|".join(args).encode())
            temp = skt.recv(3072)  # receive handshake response (error or success)
            data = temp.decode()
            if data.startswith("ERROR"):  # on error display to user.
                skt.close()
                messagebox.showerror("server error", data)
                return

            # if no error, show chat room page
            show_page("chat")
            Globals.socket_reference = skt
            root.after(10, lambda: socket_handle(skt))
        except ConnectionRefusedError:
            messagebox.showerror("server error", "couldn't connect to the server")
            return
    else:
        show_page("chat")


def socket_handle(skt):
    closed = False
    try:
        rlist, wlist, xlist = \
            select.select([skt], [skt], [])

        if rlist:
            read_socket = rlist[0]
            temp = read_socket.recv(3072)  # read from socket
            if not temp:  # raise error if connection closed
                closed = True
                show_page("login")
                messagebox.showinfo("exited server", "Connection closed or interrupted")
                raise EOFError
            data = pickle.loads(temp)  # decode msg object

            Globals.text_box.configure(state='normal')

            for msg in data:  # add message(s) to client textbook
                Globals.text_box.insert("end", f" {msg.aut} ({msg.tim}):\n", "bold")
                msg = msg.msg.replace("\n", "\n  ")
                Globals.text_box.insert("end", f'  {msg}\n')

            Globals.text_box.configure(state='disabled')

        if wlist and Globals.message:
            if len(Globals.message) > 1000:
                Globals.text_box.configure(state='normal')
                Globals.text_box.insert("end", "WARNING: Message cannot exceed 1000 characters\n", "bold")
            else:
                wlist[0].sendall(Globals.message.encode())  # send message
            Globals.message = ""
    except EOFError:  # server closed/ crashed response
        if not closed:
            show_page("login")
            messagebox.showerror("server error", "Server crashed or closed")
        skt.close()
        Globals.text_box.configure(state='normal')
        Globals.text_box.delete('1.0', tk.END)
        Globals.text_box.configure(state='disabled')
        Globals.socket_reference = None
        return

    root.after(10, lambda: socket_handle(skt))  # recursively call function with timeout


def send_message(txt):
    string = txt.get(1.0, tk.END).strip("\n ")

    if not string:
        return

    Globals.message = beautify_text(string)
    txt.delete(1.0, tk.END)


def page_frame(function):  # page wrapper (preset settings such as color)
    def wrapper(_root):
        frame = tk.Frame(_root)
        frame.configure(bg=BG_COLOR)

        frame = function(frame)

        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        return frame
    return wrapper


def get_root():  # root
    temp = tk.Tk()
    temp.title("Erez Chat")
    temp.geometry("800x450")
    temp.configure(bg=BG_COLOR)
    temp.grid_rowconfigure(0, weight=1)
    temp.grid_columnconfigure(0, weight=1)
    temp.resizable(False, False)
    return temp


def show_page(page):
    page = frames[page]
    page.tkraise()


@page_frame
def get_login(frame):  # login page design
    temp = tk.Frame(frame)
    temp.configure(bg=BG_COLOR)

    label1 = tk.Label(temp, text="Insert chat ID:\n(leave empty when creating chatroom)", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT)
    label1.grid(row=0, column=0, pady=2)
    txt1 = tk.Entry(temp, bg=INPUT_COLOR, fg=TEXT_COLOR, font=FONT, width=30)
    txt1.grid(row=1, column=0, pady=2)

    label2 = tk.Label(temp, text="Insert chat password:", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT)
    label2.grid(row=2, column=0, pady=2)
    txt2 = tk.Entry(temp, bg=INPUT_COLOR, fg=TEXT_COLOR, font=FONT, width=30)
    txt2.grid(row=3, column=0, pady=2)

    label3 = tk.Label(temp, text="Choose username:", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT)
    label3.grid(row=4, column=0)
    txt3 = tk.Entry(temp, bg=INPUT_COLOR, fg=TEXT_COLOR, font=FONT, width=30)
    txt3.grid(row=5, column=0, pady=2)

    button1 = tk.Button(temp, text="CREATE CHAT", command=lambda: login("create", txt1, txt2, txt3))
    button1.grid(row=6, column=0, pady=8)
    button2 = tk.Button(temp, text="JOIN CHAT", command=lambda: login("join", txt1, txt2, txt3))
    button2.grid(row=7, column=0)

    temp.grid(row=0, column=0)

    return frame


@page_frame
def get_chatroom(frame):  # chatroom page design
    temp = tk.Frame(frame)
    temp.configure(bg=BG_COLOR)

    label = tk.Label(temp, text="send message:", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT)
    label.grid(row=0, column=0, sticky="w")
    txt = tk.Text(temp, bg=INPUT_COLOR, fg=TEXT_COLOR, font=FONT, width=75, height=3)
    txt.grid(row=1, column=0)
    button = tk.Button(temp, width=14, height=3, text="send", command=lambda: send_message(txt))
    button.grid(row=1, column=1, sticky="ws", padx=4, pady=2)

    temp.grid(row=1, column=0, sticky="w", padx=7, pady=6)

    text_box = tk.Text(frame, height=24, width=100, font="Helvetica 12", bg=BG_COLOR, fg=TEXT_COLOR)
    text_box.grid(row=0, column=0, sticky="sw")
    scroll = tk.Scrollbar(frame, orient="vertical", command=text_box.yview)
    scroll.grid(row=0, column=1, sticky="nse")

    text_box['yscrollcommand'] = scroll.set
    text_box.tag_configure("bold", font="Helvetica 12 bold")
    text_box.config(state="disabled")
    Globals.text_box = text_box

    return frame


def on_close():  # close socket when closing client
    if Globals.socket_reference is not None:
        Globals.socket_reference.close()
    root.destroy()


root = get_root()
frames["login"] = get_login(root)
frames["chat"] = get_chatroom(root)
show_page("login")
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
quit()



