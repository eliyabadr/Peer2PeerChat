p2p-chat Application

This is a peer-to-peer chat application built using Python and Tkinter. It enables two users on the same network to send messages, emojis, and files, with a simple and intuitive UI.

--- Features

- Real-Time Messaging: Send text messages over UDP with retry and acknowledgment.
- File Sharing: Transfer files over a TCP connection.
- Emoji Panel: Select emojis from a panel to insert into your messages.
- Theme Toggle: Switch between light and dark themes.
- Auto-Retry Connections: Automatically reconnects if initial connection fails.

--- Installation

1. Install Python (version 3.6 or above).
2. Run `pip install tk` to ensure Tkinter is available.
3. Clone or download this repository.
4. Run `p1.py` and `p2.py` in separate terminal windows.

--- Usage

1. Starting the Chat:
   - Run `p1.py` and `p2.py` in any order. They will automatically connect to each other.
2. Sending Messages:
   - Type a message in the input box and press "Enter" or click "Send" to send.
3. Sending Files:
   - Click "Send File 📁" and select a file to send.
4. Toggle Theme:
   - Click "Toggle Theme ✨" to switch between light and dark themes.
5. Clear Chat:
   - Click "Clear Chat 🗑" to erase chat history.
6. About:
   - Click "About ℹ" for information about the app.

--- Testing

See `totest.txt` for details on testing with network conditions.
