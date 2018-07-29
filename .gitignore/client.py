# author	:	Sanket Khedekar sakh3719@colorado.edu
# name	    :	client.py
# purpose	:   Client file for receiving command from user and displaying output.
# date	    :	2017.9.24
# version	:	1.0

import socket
import sys
import os
import time
from cryptography.fernet import Fernet


class ClientSide:
    def __init__(self, server_name, server_port):
        self.serverName = server_name
        self.serverPort = server_port
        # Fernet key for encoding and decoding the data
        self.key = b'Yq0_0faWZEdP1ij8qm4Fy9alpCIYUUj6tothiIla1H8='

    def create_socket(self):
        # AF_INET for IPv4 | SOCK_DGRAM for UDP and SOCK_STREAM for TCP
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            print("Failed to create socket.")
            sys.exit()
        return client_socket

    # For set command
    def send_file(self, file_name, client_socket, server_address):
        data_size = 2048
        buffer = 4096
        if os.path.isfile(file_name):
            send_data = "FE"
            client_socket.sendto(send_data.encode(), server_address)
            file_handle = open(file_name, "rb")
            print("File opened.")
            send_data = True
            print("Sending data...")
            # key = Fernet.generate_key()
            # print("Key = ", key)
            # Key is used for encryption
            cipher_key = Fernet(self.key)
            # server_socket.sendto(cipher_key, client_address)
            while send_data:
                data = file_handle.read(data_size)
                data = data + str("###-###0").encode()
                send_data = cipher_key.encrypt(data)
                # print("Send data: ", send_data)
                client_socket.sendto(send_data, server_address)

                # Receive ack from the client
                ack_msg, server_address = client_socket.recvfrom(buffer)
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
                        print("Packet drop")
                        # print("Send data: ", send_data)
                        # If the packet drops, send another one
                        client_socket.sendto(send_data, server_address)
                        ack_msg, server_address = client_socket.recvfrom(buffer)
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
            client_socket.sendto(send_data.encode(), server_address)

        print(msg)

    # For get command
    def receive_file(self, filename, client_socket):
        buffer = 4096
        server_data, server_address = client_socket.recvfrom(buffer)
        if server_data.decode() == "FE":
            with open("received_" + filename, "wb") as file_handle:
                print("File opened.")
                print("Receiving data...")
                # key, server_address = client_socket.recvfrom(buffer)
                # print("Key = ", key)
                cipher_key = Fernet(self.key)
                while True:
                    # time.sleep(3)
                    encoded_server_data, server_address = client_socket.recvfrom(buffer)
                    # print("ACK encrypt data: ", encoded_server_data)
                    # For decrypting the data
                    server_data = cipher_key.decrypt(encoded_server_data)
                    data = server_data.split(b'###-###')[0]
                    # print("ACK: ", server_data.split(b'###-###')[1])
                    ack_count = (server_data.split(b'###-###')[1]).decode()
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
                    client_socket.sendto(ack_msg.encode(), server_address)

            file_handle.close()
            print("File Closed")

            # sendto is use to send package
            ack_msg = "ACK File transferred ###-###2"
            client_socket.sendto(ack_msg.encode(), server_address)
        else:
            print("File does not exists.")

    def txrx_cmd(self, cmd):
        buffer = 2048
        client_socket = ClientSide.create_socket(self)
        server_address = (self.serverName, self.serverPort)

        # print(ls != 0 and ls != 1)
        # print(ls != 1)
        # print(ls != 0)
        # print(cmd)
        if cmd != 0 and cmd != 1:
            send_data = ""
            for value in cmd:
                send_data += value + " "
            send_data = send_data[:-1]
            # Send
            client_socket.sendto(send_data.encode(), server_address)
            # Receive
            if cmd[0] == "get":
                file_name = str(cmd[1])
                ClientSide.receive_file(self, file_name, client_socket)
            elif cmd[0] == "put":
                file_name = str(cmd[1])
                ClientSide.send_file(self, file_name, client_socket, server_address)
            else:
                output, server_address = client_socket.recvfrom(buffer)
                print(output.decode())
                if str(output.decode()) == "Client and Server exit":
                    sys.exit()
        elif cmd == 1:
            print("Please provide one of the following commands.")
        else:
            print("Please provide arguments for that command.")

    def cmd_option(self, command):
        option = str(command.split(" ")[0]).lower()
        list_option = [option]
        try:
            if option == "get" or option == "put":
                file_name = str(command.split(" ")[1])
                list_option.append(file_name.lower())
            elif option == "rename":
                old_file_name = str(command.split(" ")[1])
                new_file_name = str(command.split(" ")[2])
                list_option.append(old_file_name.lower())
                list_option.append(new_file_name.lower())
            elif option == "list":
                list_option = [option]
            elif option == "exit":
                list_option = [option]
            else:
                list_option = 1
            # print(list_option)
            # This return will send command to the server from txrx_cmd
            return list_option
        except IndexError:
            return 0


if __name__ == '__main__':
    try:
        # Two command line arguments - IP Address and port No
        ip_address = str(sys.argv[1])
        port = int(sys.argv[2])
    except TypeError:
        print("Please enter IP address and  port no.")
        sys.exit()
    except IndexError:
        print("Please enter ip address and port no as arguments.")
        sys.exit()

    if port < 5001 or port > 65535:
        print("Please enter port no between 5001 and 65535 inclusive.")
        sys.exit()

    while True:
        c_option = input("\n ----- Please enter the command: -----"
                         "\n get [file_name] "
                         "\n put [file_name] "
                         "\n rename [old_file_name][new_file_name] "
                         "\n list "
                         "\n exit "
                         "\n >> : ")

        client = ClientSide(ip_address, port)
        cmd = client.cmd_option(c_option)
        client.txrx_cmd(cmd)


sys.exit()
