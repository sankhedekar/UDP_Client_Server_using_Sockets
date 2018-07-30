# UDP_Client_Server_using_Sockets
UDP Socket Programming.

---------------------------------------------------------------------------------------------------
Objective:
---------------------------------------------------------------------------------------------------
Appropriate understanding of Python language.
Learn about UDP Socket programming using Python.
Transferring content and messages between a Client and a Server using Sockets

---------------------------------------------------------------------------------------------------
Background:
---------------------------------------------------------------------------------------------------
1. Process:
   The Program assignment is done in Python. The purpose of the assignment is to 
   transfer files using UDP socket programming.
   Larger files with size more than 50MB (File size: 56MB) was successfully sent 
   within 30 secs with a transfer rate of 1.86MB/sec.
   The user is given options for selecting the command.
   When the command is send, the server sends the response and prints the message.
   
2. Splitting data in pieces:
   If the data is large, the data is broken into pieces before sending and each
   packet is send recursively.

3. Acknowledgement protocol:
   When the data is send, bit 0 is added to the bit.
   At the receiver, if the data is received with bit 0, acknowledgement is send
   with bit 1.
   If the bit 1 is not received, then again the same packet is send.
	
4. Encryption for security:
   Fernet from Cryptography is used for data encryption. Before sending a file, 
   the data which is broken into chunks of packets, are encrypted using the key 
   and send. The data is then decrypted at the other side using the same key.

---------------------------------------------------------------------------------------------------
Requirement:
---------------------------------------------------------------------------------------------------
Python v3.6.2

Inside root folder there should be two folders:
For Client: client
For Server: server

---------------------------------------------------------------------------------------------------
Folder Hierarchy:
---------------------------------------------------------------------------------------------------
Place the following files in client folder.
Foo1.txt
Foo2.jpg
Foo3.pdf
server.py

Place the following files in the server folder.
server.py

---------------------------------------------------------------------------------------------------
IDE for Development:
---------------------------------------------------------------------------------------------------
Pycharm
Terminal window inside pycharm for running program.

---------------------------------------------------------------------------------------------------
Instruction for running program:
---------------------------------------------------------------------------------------------------
Server 
server.py 7777

Client
client.py 127.0.0.1 7777

---------------------------------------------------------------------------------------------------
