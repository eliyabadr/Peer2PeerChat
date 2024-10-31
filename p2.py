from socket import *
import threading
import tkinter as tk
from tkinter import messagebox, filedialog, Label, Toplevel, Button
import os

serverPort2 = 12000  
serverSocket2 = socket(AF_INET, SOCK_DGRAM)
serverSocket2.bind(("127.0.0.1", serverPort2))


def packeting(s):
    L = []
    sprime = s.split()
    seqnum = 0
    for k in sprime:
        L.append((k, seqnum))
        seqnum += 1

    return L


seqnum_received = 0  


def listen():
    print("Welcome to p2p-chat")
    print("Listening: ... ")
    L = []
    seqnumwanted = 0  
    while True:
        try:
            messagerec, clientAddress = serverSocket2.recvfrom(2048)
            msg = messagerec.decode()
            message = eval(msg) 
            global seqnum_received
            if type(message) == tuple:  
                seqnum_received = message[1]  
                if seqnum_received == seqnumwanted: 
                    
                    serverSocket2.sendto(str(seqnum_received + 1).encode(), ("127.0.0.1", 12001))
                    L.append(message[0])

                    seqnumwanted += 1 
                else:
                    
                    serverSocket2.sendto(str(seqnumwanted).encode(), ("127.0.0.1", 12001))  
            elif type(message) == bool and message == True:
                chatbox.insert(tk.END, "\n||Peer: " + " ".join(L)) 
                L = []
                seqnumwanted = 0
                seqnum_received = 0
            elif type(message) == int:
                seqnum_received = message

        except Exception as e:
            print(e)


def send():
    rawmsg = message_entry.get()
    if os.path.exists(rawmsg):    
        send_file(client_socket , rawmsg)
    else:
        packets = packeting(rawmsg)
        for packet in packets:
            while True:
                x = str(packet)
                serverSocket2.sendto(x.encode(), ("127.0.0.1", 12001))
                try:
                    if seqnum_received == packet[1] + 1:
                        break
                except Exception as e:
                    print(e)
        serverSocket2.sendto(str(True).encode(), ("127.0.0.1", 12001))
        chatbox.insert(tk.END , "\n|You: " + rawmsg)
        message_entry.delete(0, tk.END)


def send_file(path):
    file_path = path
    file = open(file_path, "rb")

    name = os.path.basename(file_path)

    client_socket.send(name.encode())

    data = file.read()
    client_socket.sendall(data)
    client_socket.send(b"<DONE>")
    file.close()


def receive_file():
    save_path = os.getcwd()
    while True:
        file_name = client_socket.recv(1024).decode()
        file_name = "new" + file_name
        chatbox.insert(tk.END, "\nReceived: " + file_name)
        file_name = os.path.join(save_path, file_name)
        file = open(file_name, "wb")
        print(file_name)
        data = b""
        ongoing = True
        while ongoing:
            info = client_socket.recv(1024)
            if info[-6:] == b"<DONE>":
                info = info[0:-6]
                ongoing = False
            data += info
        file.write(data)
        file.close()
          

def toggle_theme():
    global frame 
    current_theme = root.tk.call("ttk::style", "theme", "use")
    if current_theme == "clam":
        new_theme = "vista"
        root.configure(bg="#ADD8E6")
        frame.configure(bg="#ADD8E6")
    else:
        new_theme = "clam"
        root.configure(bg="#333A56")
        frame.configure(bg="#333A56")
    root.tk.call("ttk::style", "theme", "use", new_theme)

def main():
    host = "localhost"
    port = 5500
    global root
    global chatbox
    global message_entry
    global frame  
    global client_socket
    server_socket = socket(AF_INET, SOCK_STREAM)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen()
        print("Connecting...")
        
        client_socket, client_address = server_socket.accept()
        print("Connected.", client_address)
    except OSError:
        print("Connecting...")
        
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((host, port))
        print("Connected.")
        
    def browse_file():
        file_path = tk.filedialog.askopenfilename()
        if file_path:
            send_file(file_path)
    
    root = tk.Tk()
    root.title("p2p-chat")

    root.tk_setPalette(background="#ADD8E6") 
    root.configure(bg="#ADD8E6") 
    
    frame = tk.Frame(root, relief=tk.RIDGE, borderwidth=5)
    frame.pack(padx=10, pady=10)

    message_entry = tk.Entry(frame, width=50, font=("Helvetica", 12), fg="grey")
    message_entry.grid(row=0, column=1, padx=5, pady=5)

    message_entry.insert(0, "Type here...")
    message_entry.bind("<FocusIn>", lambda event: focus(event, message_entry))
    message_entry.bind("<FocusOut>", lambda event: focusout(event, message_entry))
    
    message_label = tk.Label(frame, text="Your Message:", font=("Georgia", 12))
    message_label.grid(row=0, column=0, sticky="w")

    send_button = tk.Button(frame, text="Send \u2708", command=send, font=("Helvetica", 12, "bold"))
    send_button.grid(row=0, column=2, padx=5, pady=5)

    file_button = tk.Button(frame, text="Send File 📁", command=browse_file, font=("Georgia", 12))
    file_button.grid(row=1, column=1, padx=5, pady=5)

    chatbox = tk.Text(frame, height=10, width=60, font=("Helvetica", 12))
    chatbox.grid(row=2, columnspan=3, padx=5, pady=5)
    
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    net_label = tk.Label(button_frame, text="🌐p2p-chat", font=("Georgia", 18), fg="blue")
    net_label.pack(side=tk.LEFT, padx=10)

    clear_button = tk.Button(button_frame, text="Clear \U0001F5D1", command=clear_chat, font=("Georgia", 12))
    clear_button.pack(side=tk.LEFT, padx=10)

    theme_button = tk.Button(button_frame, text="✩/☾", command=toggle_theme, font=("Georgia", 12, "bold"))
    theme_button.pack(side=tk.LEFT, padx=10)
    
    emoji_panel_button = tk.Button(button_frame, text="😎", command=open_emoji_panel, font=("Georgia", 12))
    emoji_panel_button.pack(side=tk.LEFT, padx=10)

    receiving = threading.Thread(target=listen)
    receiving.start()
    recfile = threading.Thread(target=receive_file)
    recfile.start()

    root.mainloop()

def open_emoji_panel():
    if message_entry.get() == "Type here...":
        message_entry.delete(0, tk.END)

    emoji_panel = Toplevel(root)
    emoji_panel.title("Emoji Panel")

    emojis = ["😊", "😎", "😍", "🤩", "😂", "😜", "😇", "🥳", "🎉"]
    for emoji in emojis:
        emoji_button = Button(emoji_panel, text=emoji, font=("Segoe UI Emoji", 12), command=lambda e=emoji: send_emoji(e))
        emoji_button.pack(side=tk.LEFT, padx=5, pady=5)

def send_emoji(emoji):
    if message_entry.get() == "Type here...":
        message_entry.delete(0, tk.END)
    message_entry.insert(tk.END, emoji)

def focus(event, entry):
    if entry.get() == "Type here...":
        entry.delete(0, "end")

def focusout(event, entry):
    if not entry.get():
        entry.insert(0, "Type here...")
        
def clear_chat():
    chatbox.delete(1.0, tk.END) 

if __name__ == "__main__":
    main()
