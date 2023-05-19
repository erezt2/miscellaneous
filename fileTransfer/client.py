import subprocess
import time
from tkinter.filedialog import askopenfilename
import os
import socket
import tkinter as tk
from tkinter import messagebox

window = tk.Tk()
window.title('Erez Cloud')
window.geometry("750x600")
window.configure(bg='LightBlue')
window.resizable(False, False)

if not os.path.exists("C:\\PythonClientFile"):
    os.makedirs("C:\\PythonClientFile")


def upload_file():
    file_path = askopenfilename()
    if file_path is not None and file_path != '':
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.connect(("127.0.0.1", 4000))

        my_socket.send(("UPLOAD " + os.path.basename(file_path)).encode())
        f = open(file_path, 'rb')
        content = f.read()
        f.close()
        my_socket.sendall(content)
        my_socket.close()
        messagebox.showinfo('file upload', 'File uploaded successfully')
    else:
        messagebox.showwarning('file upload', 'nothing chosen')


def download_file():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect(("127.0.0.1", 4000))

    my_socket.send("DOWNLOAD".encode())
    data = my_socket.recv(1024).decode()

    files = ''
    while data:
        files += data
        if '/' in data:
            break
        data = my_socket.recv(1024).decode()

    cancel = tk.Button(window, text="cancel", height=2, width=16, font=('ariel', 11), command=lambda: select(""))
    cancel.pack(side="bottom", anchor="sw")

    def select(selected):
        if selected:
            print(1234)
            my_socket.send(selected.encode())

            file_path = "C:\\PythonClientFile\\" + selected
            ending = "." + file_path.split(".")[-1]
            file_path = ".".join(file_path.split(".")[:-1])
            c = 1

            if os.path.exists(file_path + ending):
                c += 1

            while os.path.exists(file_path + str(c) + ending):
                c += 1

            if c != 1:
                f = open(file_path + str(c) + ending, 'wb')
            else:
                f = open(file_path + ending, 'wb')

            data = my_socket.recv(1024)

            while data:
                f.write(data)
                data = my_socket.recv(1024)

            f.close()
        my_socket.close()
        for widget in frame2.winfo_children():
            widget.destroy()
        cancel.destroy()
        frame2.update()
        receive['state'] = 'normal'
        send['state'] = 'normal'
        openf['state'] = 'normal'
        canvas_container.yview_moveto(0.0)
        canvas_container.configure(scrollregion=f"0 0 0 {frame2.winfo_height()}")
        frame2.update()
        if selected:
            messagebox.showinfo('file upload', 'File uploaded successfully')

    for file in files.split("|")[:-1]:
        tk.Button(frame2, text=file, height=1, width=66, font=('ariel', 11), command=lambda: select(file)).pack(side="top")
    frame2.update()
    receive['state'] = 'disabled'
    send['state'] = 'disabled'
    openf['state'] = 'disabled'
    canvas_container.configure(yscrollcommand=scroll.set, scrollregion=f"0 0 0 {frame2.winfo_height()}")
    frame2.update()
    # messagebox.showinfo('file download', 'File downloaded successfully')


def exitt():
    window.destroy()


def select_file(filename, cancel):
    if filename != "":
        os.startfile(os.path.join("C:\\PythonClientFile", filename))
    cancel.destroy()
    for widget in frame2.winfo_children():
        widget.destroy()
    frame2.update()
    receive['state'] = 'normal'
    send['state'] = 'normal'
    openf['state'] = 'normal'
    canvas_container.yview_moveto(0.0)
    canvas_container.configure(scrollregion=f"0 0 0 {frame2.winfo_height()}")
    frame2.update()


def open_file():
    cancel = tk.Button(window, text="cancel", height=2, width=16, font=('ariel', 11), command=lambda: select_file("", cancel))
    cancel.pack(side="bottom", anchor="sw")
    for filename in os.listdir("C:\\PythonClientFile"):
        tk.Button(frame2, text=filename, height=1, width=66, font=('ariel', 11), command=lambda: select_file(filename, cancel)).pack(side="top")
    receive['state'] = 'disabled'
    send['state'] = 'disabled'
    openf['state'] = 'disabled'
    frame2.update()
    canvas_container.configure(yscrollcommand=scroll.set, scrollregion=f"0 0 0 {frame2.winfo_height()}")


def pass1():
    pass


tk.Button(window, text='Erez Cloud', command=pass1, height=3, width=10, border=0, bg="LightBlue", font=('Baskerville Old Face', 40)).place(x=235, y=-30)
send = tk.Button(window, height=2, width=18, text='Send', font=('Baskerville Old Face', 20), border=3, bg="LightBlue", command=upload_file)
send.place(x=250, y=150)
receive = tk.Button(window, height=2, width=18, text='Receive', font=('Baskerville Old Face', 20), border=3, bg="LightBlue", command=download_file)
receive.place(x=250, y=250)
openf = tk.Button(window, height=2, width=18, text='Open', font=('Baskerville Old Face', 20), border=3, bg="LightBlue", command=open_file)
openf.place(x=250, y=350)

frame = tk.Frame(window, width=600, height=120, background="LightBlue", border=3)
canvas_container = tk.Canvas(frame, width=574, height=120)
frame2 = tk.Frame(canvas_container)
scroll = tk.Scrollbar(frame, orient="vertical", command=canvas_container.yview)  # will be visible if the frame2 is to to big for the canvas
canvas_container.create_window((0, 0), window=frame2, anchor='nw')

frame2.update()
canvas_container.configure(yscrollcommand=scroll.set, scrollregion=f"0 0 0 {frame2.winfo_height()}")


canvas_container.pack(side="left")
scroll.pack(side="right", fill="y")

frame.place(x=80, y=450)
frame.pack_propagate(0)

window.mainloop()
