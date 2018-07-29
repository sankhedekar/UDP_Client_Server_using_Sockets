# author	:	Sanket Khedekar sakh3719@colorado.edu
# name	    :	server.py
# purpose	:   Server file for transfer of data by taking the commands from the client.
# date	    :	2017.9.24
# version	:	1.0

import socket
import sys
import os
import time
from cryptography.fernet import Fernet


class ServerSide:
    def __init__(self, server_port):
        self.serverPort = server_port
        # Fernet key for encoding and decoding the data
        self.key = b'Yq0_0faWZEdP1ij8qm4Fy9alpCIYUUj6tothiIla1H8='

    def create_socket(self):
        # AF_INET for IPv4 | SOCK_DGRAM for UDP and SOCK_STREAM for TCP
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            print("Failed to create socket.")
            sys.exit()
        return server_socket

    # For get command
    def send_file(self, file_name, server_socket, client_address):
        data_size = 2048
        buffer = 4096
        if os.path.isfile(file_name):
            send_data = "FE"
            server_socket.sendto(send_data.encode(), client_address)
            file_handle = open(file_name, "rb")
            print("File opened.")
            send_data = True
            print("Sending data...")
            # key = Fernet.generate_key()
            # print("Key = ", key)
            # Key is used for encryption
            cipher_key = Fernet(self.key)
            # server_socket.sendto(key, client_address)
            while send_data:
                data = file_handle.read(data_size)
                data = data + str("###-###0").encode()
                send_data = cipher_key.encrypt(data)
                # print("Send data: ", send_data)
                server_socket.sendto(send_data, client_address)

                # Receive ack from the client
                ack_msg, server_address = server_socket.recvfrom(buffer)
                ack_data = str(ack_msg.decode())
                message = ack_data.split("###-###")[0]
                # print("ACK message: ", message)
                ack_count = ack_data.split("###-###")[1]
                # print("ACK count: ", ack_count)

                if ack_count == "2":
                    print(message)
                    break
                elif ack_count == "1":
                    print("ACK received.")
                elif ack_count == "0":
                    # time.sleep(3)
                    while ack_count == "0":
                        # If the packet drops, send another one
                        print("Packet drop")
                        # print("Send data: ", send_data)
                        server_socket.sendto(send_data, client_address)
                        ack_msg, server_address = server_socket.recvfrom(buffer)
                        ack_data = str(ack_msg.decode())
                        # print("ACK Message: " + ack_data)
                        ack_count = ack_data.split("###-###")[1]
                        if ack_count == "1":
                            break

            file_handle.close()
            print("File closed.")
            msg = "File received."

        else:
            # If the file is not present
            msg = "File does not exists."
            send_data = "FNE"
            server_socket.sendto(send_data.encode(), client_address)

        print(msg)

    # For put command
    def receive_file(self, filename, server_socket):
        buffer = 4096
        client_data, server_address = server_socket.recvfrom(buffer)
        if client_data.decode() == "FE":
            with open("send_" + filename, "wb") as file_handle:
                print("File opened.")
                print("Receiving data...")
                # key, server_address = client_socket.recvfrom(buffer)
                # print("Key = ", key)
                cipher_key = Fernet(self.key)
                while True:
                    # time.sleep(3)
                    encoded_client_data, client_address = server_socket.recvfrom(buffer)
                    # print("ACK encrypt data: ", encoded_client_data)
                    # For decrypting the data
                    client_data = cipher_key.decrypt(encoded_client_data)
                    data = client_data.split(b'###-###')[0]
                    # print("ACK: ", client_data.split(b'###-###')[1])
                    ack_count = (client_data.split(b'###-###')[1]).decode()
                    # print("ACK data: ", data)
                    # print("ACK count: ", ack_count)
                    if not data:
                        print("End of file")
                        break
                    if ack_count == "0":
                        # write data to a file
                        file_handle.write(data)
                        ack_msg = "ACK Packet received.###-###1"
                    else:
                        ack_msg = "ACK Packet received.###-###0"

                    # print(ack_msg)
                    server_socket.sendto(ack_msg.encode(), client_address)

            file_handle.close()
            print("File Closed")

            # sendto is use to send package
            ack_msg = "ACK File transferred ###-###2"
            server_socket.sendto(ack_msg.encode(), client_address)
        else:
            print("File does not exists.")

    def fn_get_file(self, filename, server_socket, client_address):
        # print("get")
        ServerSide.send_file(self, filename, server_socket, client_address)

    def fn_put_file(self, filename, server_socket):
        # print("put")
        ServerSide.receive_file(self, filename, server_socket)

    def fn_rename_file(self, client_address, old, new):
        # print("rename")
        try:
            old_file = str(old.split(".")[1])
            new_file = str(new.split(".")[1])
            if not os.path.isfile(old):
                data = "File doesn't exists."
            elif os.path.isfile(new):
                data = "File name already exist. Please give another name."
            elif old_file != new_file:
                data = "Please provide file name with same extension."
            elif os.path.isfile(old):
                os.rename(old, new)
                data = "File renamed."
            else:
                data = "File not renamed."
        except IndexError:
            data = "Please provide file with extension."
        # Send
        ServerSide.tx_cmd(self, client_address, data)

    def fn_list(self, client_address):
        # print("list")
        current_dir = os.curdir
        file_list = os.listdir(current_dir)
        data = "Files in the server directory are: \n"
        for file in file_list:
            data += file + "\n"
        data = data[:-1]
        # Send
        ServerSide.tx_cmd(self, client_address, data)

    def fn_exit(self, client_address):
        # print("exit")
        data = "Client and Server exit"
        # Send
        ServerSide.tx_cmd(self, client_address, data)
        print("Command executed: 'exit'")
        sys.exit()

    def tx_cmd(self, client_address, data):
        # Send
        server_socket = ServerSide.create_socket(self)
        server_socket.sendto(data.encode(), client_address)

    def rx_cmd(self):
        buffer = 2048
        server_socket = ServerSide.create_socket(self)
        server_socket.bind(('', self.serverPort))
        print("The server is ready. Port No is " + str(self.serverPort))

        while True:
            # Receive
            rx_data_encode, client_address = server_socket.recvfrom(buffer)
            rx_data = rx_data_encode.decode()

            cmd = str(rx_data.split(" ")[0]).lower()

            # print(rx_data)
            # print(cmd)

            if cmd == "get":
                file_name = str(rx_data.split(" ")[1]).lower()
                ServerSide.fn_get_file(self, file_name, server_socket, client_address)
                # print(cmd)
                # print(file_name)

            elif cmd == "put":
                file_name = str(rx_data.split(" ")[1]).lower()
                ServerSide.fn_put_file(self, file_name, server_socket)
                # print(cmd)
                # print(file_name)

            elif cmd == "rename":
                old_file_name = str(rx_data.split(" ")[1]).lower()
                new_file_name = str(rx_data.split(" ")[2]).lower()
                ServerSide.fn_rename_file(self, client_address, old_file_name, new_file_name)
                # print(cmd)
                # print(old_file_name)
                # print(new_file_name)

            elif cmd == "list":
                ServerSide.fn_list(self, client_address)
                # print(cmd)

            elif cmd == "exit":
                ServerSide.fn_exit(self, client_address)
                # print(cmd)

            print("Command executed: '" + cmd + "'")


if __name__ == '__main__':
    try:
        # One command line argument - Port No
        port = int(sys.argv[1])
    except TypeError:
        print("Port no should be in integer.")
        sys.exit()
    except IndexError:
        print("Please enter Port no as argument.")
        sys.exit()

    if port < 5001 or port > 65535:
        print("Please enter port no between 5001 and 65535 inclusive")
        sys.exit()

    server = ServerSide(port)
    server.rx_cmd()
