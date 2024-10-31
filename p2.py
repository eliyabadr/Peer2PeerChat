# p2.py
import socket
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import datetime

UDP_IP = "127.0.0.1"
UDP_PORT_SEND = 12001
UDP_PORT_RECEIVE = 12000
TCP_HOST = "localhost"
TCP_PORT = 5500
MAX_RETRIES = 5
ACK_TIMEOUT = 2  # seconds

def send_udp_message(message):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg = message.encode()
    retries = 0
    while retries < MAX_RETRIES:
        udp_socket.sendto(msg, (UDP_IP, UDP_PORT_SEND))
        try:
            udp_socket.settimeout(ACK_TIMEOUT)
            ack, _ = udp_socket.recvfrom(1024)
            if ack.decode() == "ACK":
                return True
        except socket.timeout:
            retries += 1
    return False

def udp_listener():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((UDP_IP, UDP_PORT_RECEIVE))
    while True:
        try:
            data, addr = udp_socket.recvfrom(1024)
            message = data.decode()
            timestamp = datetime.datetime.now().strftime('%H:%M:%S')
            chatbox.config(state='normal')
            chatbox.insert(tk.END, f"\n[{timestamp}] Peer: {message}", 'peer')
            chatbox.config(state='disabled')
            chatbox.see(tk.END)
            udp_socket.sendto("ACK".encode(), addr)
        except Exception as e:
            print(f"UDP Listener Error: {e}")

def send(event=None):
    rawmsg = message_entry.get()
    if rawmsg.strip() == '':
        return
    if os.path.isfile(rawmsg):
        send_file(rawmsg)
    else:
        success = send_udp_message(rawmsg)
        if success:
            timestamp = datetime.datetime.now().strftime('%H:%M:%S')
            chatbox.config(state='normal')
            chatbox.insert(tk.END, f"\n[{timestamp}] You: {rawmsg}", 'you')
            chatbox.config(state='disabled')
            chatbox.see(tk.END)
            message_entry.delete(0, tk.END)
        else:
            chatbox.config(state='normal')
            chatbox.insert(tk.END, "\n|Error: Message not sent after retries.", 'error')
            chatbox.config(state='disabled')
            chatbox.see(tk.END)

def send_file(file_path):
    try:
        with open(file_path, "rb") as file:
            name = os.path.basename(file_path)
            client_socket.send(name.encode())
            data = file.read()
            client_socket.sendall(data)
            client_socket.send(b"<DONE>")
            timestamp = datetime.datetime.now().strftime('%H:%M:%S')
            chatbox.config(state='normal')
            chatbox.insert(tk.END, f"\n[{timestamp}] You sent file: {name}", 'you')
            chatbox.config(state='disabled')
            chatbox.see(tk.END)
    except Exception as e:
        print(f"File Send Error: {e}")

def receive_file():
    save_path = os.getcwd()
    while True:
        try:
            file_name = client_socket.recv(1024).decode()
            if not file_name:
                break  # Connection closed
            file_name = "new_" + file_name
            timestamp = datetime.datetime.now().strftime('%H:%M:%S')
            chatbox.config(state='normal')
            chatbox.insert(tk.END, f"\n[{timestamp}] Received file: {file_name}", 'peer')
            chatbox.config(state='disabled')
            chatbox.see(tk.END)
            file_path = os.path.join(save_path, file_name)
            with open(file_path, "wb") as file:
                while True:
                    data = client_socket.recv(4096)
                    if data.endswith(b"<DONE>"):
                        file.write(data[:-6])
                        break
                    if not data:
                        break
                    file.write(data)
        except Exception as e:
            print(f"File Receive Error: {e}")
            break  # Exit the loop if there's an error

def toggle_theme():
    global current_theme
    if current_theme == "light":
        root.style.theme_use('dark')
        current_theme = "dark"
    else:
        root.style.theme_use('light')
        current_theme = "light"

def browse_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        send_file(file_path)

def open_emoji_panel():
    emoji_panel = tk.Toplevel(root)
    emoji_panel.title("Emoji Panel")
    emojis = ["😊", "😂", "😍", "😉", "😎", "😁", "😢", "😭", "😡", "👍", "🙏", "🔥", "❤️", "🥰", "😴"]
    for emoji in emojis:
        btn = ttk.Button(emoji_panel, text=emoji, command=lambda e=emoji: insert_emoji(e))
        btn.pack(side=tk.LEFT, padx=3, pady=3)

def insert_emoji(emoji):
    message_entry.insert(tk.END, emoji)
    message_entry.focus_set()

def clear_chat():
    chatbox.config(state='normal')
    chatbox.delete(1.0, tk.END)
    chatbox.config(state='disabled')

def about():
    messagebox.showinfo("About", "p2p-chat Application\nVersion 2.0\nEnhanced with emojis and better UI!")

def main():
    global root, chatbox, message_entry, client_socket, current_theme
    current_theme = "light"
    connected = False

    # Only one side should bind and listen, the other should connect
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((TCP_HOST, TCP_PORT))
        connected = True
        print("Connected as client.")
    except Exception as e:
        print("Trying to start as server...")
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((TCP_HOST, TCP_PORT))
            server_socket.listen(1)
            print("Waiting for connection...")
            client_socket, _ = server_socket.accept()
            connected = True
            print("Connected as server.")
        except Exception as e:
            print(f"Connection Error: {e}")

    if not connected:
        print("Unable to establish TCP connection.")
        return

    root = tk.Tk()
    root.title("p2p-chat")
    root.geometry("600x500")

    root.style = ttk.Style()
    root.style.theme_create('light', settings={
        '.': {'configure': {'background': '#ffffff', 'foreground': '#000000'}},
        'TLabel': {'configure': {'background': '#ffffff', 'foreground': '#000000'}},
        'TButton': {'configure': {'background': '#e0e0e0'}},
        'TEntry': {'configure': {'fieldbackground': '#ffffff', 'foreground': '#000000'}},
        'TText': {'configure': {'background': '#ffffff', 'foreground': '#000000'}}
    })
    root.style.theme_create('dark', settings={
        '.': {'configure': {'background': '#2b2b2b', 'foreground': '#ffffff'}},
        'TLabel': {'configure': {'background': '#2b2b2b', 'foreground': '#ffffff'}},
        'TButton': {'configure': {'background': '#3c3f41', 'foreground': '#ffffff'}},
        'TEntry': {'configure': {'fieldbackground': '#3c3f41', 'foreground': '#ffffff'}},
        'TText': {'configure': {'background': '#2b2b2b', 'foreground': '#ffffff'}}
    })
    root.style.theme_use('light')

    frame = ttk.Frame(root)
    frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    message_label = ttk.Label(frame, text="Your Message:")
    message_label.pack(anchor='w')

    message_entry = ttk.Entry(frame)
    message_entry.pack(fill=tk.X, pady=5)
    message_entry.bind('<Return>', send)  # Bind 'Enter' key to send

    send_button = ttk.Button(frame, text="Send ✈", command=send)
    send_button.pack(pady=5)

    chatbox = tk.Text(frame, height=15, wrap='word')
    chatbox.pack(fill=tk.BOTH, expand=True, pady=5)
    chatbox.tag_config('peer', foreground='blue')
    chatbox.tag_config('you', foreground='green')
    chatbox.tag_config('error', foreground='red')
    chatbox.config(state='disabled')  # Make chatbox read-only

    button_frame = ttk.Frame(root)
    button_frame.pack(fill=tk.X, padx=10, pady=5)

    file_button = ttk.Button(button_frame, text="Send File 📁", command=browse_file)
    file_button.pack(side=tk.LEFT, padx=5)

    emoji_button = ttk.Button(button_frame, text="Emojis 😊", command=open_emoji_panel)
    emoji_button.pack(side=tk.LEFT, padx=5)

    clear_button = ttk.Button(button_frame, text="Clear Chat 🗑", command=clear_chat)
    clear_button.pack(side=tk.LEFT, padx=5)

    theme_button = ttk.Button(button_frame, text="Toggle Theme ✨", command=toggle_theme)
    theme_button.pack(side=tk.LEFT, padx=5)

    about_button = ttk.Button(button_frame, text="About ℹ", command=about)
    about_button.pack(side=tk.RIGHT, padx=5)

    threading.Thread(target=udp_listener, daemon=True).start()
    threading.Thread(target=receive_file, daemon=True).start()

    root.mainloop()

    client_socket.close()  # Close the socket when GUI is closed

if __name__ == "__main__":
    main()
