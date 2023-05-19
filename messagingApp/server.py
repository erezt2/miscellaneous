import random
import socket, select, pickle, re, time

SERVER_PORT = 60101
SERVER_IP = "0.0.0.0"

# every repeated function from the client file
# is for verification in case client maliciously
# edited the html request

# help message from server
HELP = """normal commands:
/quit - terminate connection
/help - display this message
/setname [name] - change own username
/whisper [name] [message] - private message a user
/view-admin - sends the name of the admin (and server creator)
/view-managers - sends a list of all manager (active and inactive)
/view-users - sends a list of all active users

manager commands:
/promote [name] - promote user to manager
/demote [name] (only server creator) - demotes user 
/mute [name] - mute user
/unmute [name] - unmute user
/stop (only server creator) - closes server"""


class Message:  # message class for easy pickle dumping
    def __init__(self, msg, author):
        self.aut = author
        self.msg = msg
        self.tim = 0


class InverseFunc:  # two sided dictionary for convenience
    def __init__(self, class1, class2):
        self.class1 = class1
        self.class2 = class2
        self.one_to_two = {}
        self.two_to_one = {}

    def __contains__(self, item):
        if isinstance(item, self.class1):
            return item in self.one_to_two
        elif isinstance(item, self.class2):
            return item in self.two_to_one
        else:
            raise TypeError

    def __getitem__(self, item):
        if isinstance(item, self.class1):
            return self.one_to_two[item]
        elif isinstance(item, self.class2):
            return self.two_to_one[item]
        else:
            raise TypeError

    def __setitem__(self, key, value):
        if isinstance(key, self.class1):
            self.one_to_two[key] = value
            self.two_to_one[value] = key
        elif isinstance(key, self.class2):
            self.two_to_one[key] = value
            self.one_to_two[value] = key
        else:
            raise TypeError

    def __delitem__(self, key):
        if isinstance(key, self.class1):
            del self.two_to_one[self.one_to_two[key]]
            del self.one_to_two[key]
        elif isinstance(key, self.class2):
            del self.one_to_two[self.two_to_one[key]]
            del self.two_to_one[key]
        else:
            raise TypeError

    def get_two(self):
        return list(self.two_to_one.keys())

    def get_one(self):
        return list(self.one_to_two.keys())


def beautify_text(string):  # remove wrapping spaces or multiple next lines in a row
    string = string.strip("\n ")
    string = re.sub(r"\n{2,}", "\n\n", string)
    return string


class Chatroom:  # chatroom class
    def __init__(self, creator_name, server_id, password):
        self.legacy_creator = creator_name
        self.chat_code = server_id
        self.chat_pass = password
        self.creator = creator_name
        self.name_socket = InverseFunc(socket.socket, str)
        self.managers = {creator_name}
        self.muted = set()
        self.assigned_sockets = []
        # self.client_status = {}

    def close_client(self, client, client_sockets, clients_chatroom):
        name = ""
        if client in self.name_socket:
            name = self.name_socket[client]
            del self.name_socket[client]
        if name in self.muted:
            self.muted.remove(name)
        if name in self.managers:
            self.managers.remove(name)
        self.assigned_sockets.remove(client)
        # del self.client_status[client]
        client_sockets.remove(client)
        del clients_chatroom[client]
        client.close()

    def run_client(self, cl_socket, messages_to_send):
        temp = cl_socket.recv(1024)
        data = temp.decode()

        if not data:
            return "closed"

        data = beautify_text(data)

        if data.startswith("/"):  # handle commands
            val = self.handle_commands(data, cl_socket, messages_to_send)
            if val is not None:
                return val
        elif cl_socket in self.name_socket and self.name_socket[cl_socket] in self.muted:  # muted user response
            messages_to_send.append((Message("You are muted!", "&server"), {cl_socket}))
            return "ensnared"
        else:
            if cl_socket in self.name_socket:
                aut = self.name_socket[cl_socket]  # message handler (add @ in front of managers' names)
                if self.name_socket[cl_socket] in self.managers:
                    aut = "@" + aut
                messages_to_send.append((Message(data, aut), set(self.assigned_sockets)))
            else:
                messages_to_send.append(
                    (Message("something went wrong. use /setname", "&server"), {cl_socket}))
        return "stalling"  # return value is cosmetic, doesnt do anything as long as client/ chatroom isn't closing

    def handle_commands(self, data, cl_socket, messages_to_send):
        args = data.split(" ")  # command handler, self explanatory for every command
        if args[0] == "/quit":
            return "closed"

        elif args[0] == "/setname":
            name = args[1]
            match = re.match(r"^[a-zA-Z0-9]+$", name)

            if not match or 3 > len(name) or len(name) > 16:
                messages_to_send.append((Message(
                    "invalid name.\n\nuse only english alphabet and numbers", "&server"), {cl_socket}))
                return "ensnared"
            # elif cl_socket not in self.name_socket:
            #     if name in self.name_socket:
            #         messages_to_send.append((Message(
            #             "name already exists. randomly assigning username.\nuse /setname to change your username",
            #             "&server"), {cl_socket}))
            #         name = gen_name()
            #     self.name_socket[name] = cl_socket
            org_name = self.name_socket[name]
            if name in self.name_socket:
                messages_to_send.append((Message(
                    "name already exists. change to another username", "&server"),
                                         {cl_socket}))
            else:
                del self.name_socket[org_name]
                self.name_socket[name] = cl_socket
                if org_name in self.muted:
                    self.muted.remove(org_name)
                    self.muted.add(name)
                if org_name in self.managers:
                    self.managers.remove(org_name)
                    self.managers.add(name)
                if org_name == self.creator:
                    self.creator = name
                messages_to_send.append((Message(
                    "name changed to: " + name, "&server"), {cl_socket}))

        elif args[0] == "/help":
            messages_to_send.append((Message(HELP, "&server"), {cl_socket}))

        elif args[0] == "/whisper":
            name = args[1]
            message = " ".join(args[2:])

            if name not in self.name_socket:
                messages_to_send.append((Message(
                    f"User {name} does not exist!", f"&server"),
                                         {cl_socket}))
                return "ensnared"

            messages_to_send.append((Message(
                message, f"!{self.name_socket[cl_socket]} to {name}"),
                                     {self.name_socket[name], cl_socket}))

        elif args[0] == "/view-admin":
            if self.creator == self.legacy_creator:
                messages_to_send.append((Message(
                    "The server admin/ creator is: " + self.creator, f"&server"),
                                         {cl_socket}))
            else:
                messages_to_send.append((Message(
                    f"The server admin is: {self.creator}, but the server creator is {self.legacy_creator}\n"
                    f"(notice that other users can join with the same username as said creator)", f"&server"),
                                         {cl_socket}))

        elif args[0] == "/view-managers":
            messages_to_send.append((Message(
                "Managers: " + ", ".join(self.managers), f"&server"),
                                     {cl_socket}))

        elif args[0] == "/view-users":
            messages_to_send.append((Message(
                "Users: " + ", ".join(self.name_socket.get_two()), f"&server"),
                                     {cl_socket}))

        elif self.name_socket[cl_socket] in self.managers:

            if args[0] == "/close":
                if self.name_socket[cl_socket] != self.creator:
                    messages_to_send.append((Message(
                        f"Only the server admin can do this action!", f"&server"),
                                             {cl_socket}))
                    return "ensnared"
                messages_to_send.append(
                    (Message("STOP SERVER", "&server"), set(self.assigned_sockets)))
                return "destroyed"

            if args[0] == "/promote":
                name = args[1]
                if name in self.managers:
                    messages_to_send.append((Message(
                        f"User {name} is already a manager!", f"&server"),
                                             {cl_socket}))
                    return "ensnared"
                self.managers.add(name)
                messages_to_send.append(
                    (Message(name + " got promoted to a manager.", "&server"), set(self.assigned_sockets)))

            elif args[0] == "/demote":
                name = args[1]
                if name not in self.managers:
                    messages_to_send.append((Message(
                        f"User {name} is not a manager!", f"&server"),
                                             {cl_socket}))
                    return "ensnared"
                if name == self.creator:
                    messages_to_send.append((Message(
                        f"User {name} can't be demoted!", f"&server"),
                                             {cl_socket}))
                    return "ensnared"
                self.managers.remove(name)
                messages_to_send.append(
                    (Message(name + " got demoted from a manager.", "&server"), set(self.assigned_sockets)))

            elif args[0] == "/mute":
                name = args[1]

                if name not in self.name_socket:
                    messages_to_send.append((Message(
                        f"User {name} does not exist!", f"&server"),
                                             {cl_socket}))
                    return "ensnared"

                if name in self.muted:
                    messages_to_send.append((Message(
                        f"User {name} is already muted!", f"&server"),
                                             {cl_socket}))
                    return "ensnared"

                self.muted.add(name)
                messages_to_send.append((Message(
                    f"User {name} has been muted!", "&server"),
                                         set(self.assigned_sockets)))

                messages_to_send.append((Message(
                    f"You have been muted!", "&server"),
                                         {self.name_socket[name]}))

            elif args[0] == "/unmute":
                name = args[1]

                if name not in self.name_socket:
                    messages_to_send.append((Message(
                        f"User {name} does not exist!", f"&server"),
                                             {cl_socket}))
                    return "ensnared"

                if name not in self.muted:
                    messages_to_send.append((Message(
                        f"User {name} is not muted!", f"&server"),
                                             {cl_socket}))
                    return "ensnared"

                self.muted.remove(name)

                messages_to_send.append((Message(
                    f"User {name} has been unmuted!", "&server"),
                                         set(self.assigned_sockets)))

                messages_to_send.append((Message(
                    f"You have been unmuted!", "&server"),
                                         {self.name_socket[name]}))

            else:
                messages_to_send.append(
                    (Message("unknown command. use /help", "&server"), {cl_socket}))

        else:
            messages_to_send.append(
                (Message("unknown command. use /help", "&server"), {cl_socket}))


def main():
    #  create server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket = server_socket
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()

    # client list
    client_sockets = []
    messages_to_send = []
    chatroom_names = InverseFunc(str, Chatroom)
    clients_chatroom = {}

    run = True
    while run:
        rlist, wlist, xlist = select.select([server_socket] + client_sockets, client_sockets, [])  # get read/ write ready clients
        # assigns current time format
        tm = time.time()
        tm = time.localtime(tm)
        tm = f"{str(tm.tm_hour).zfill(2)}:{str(tm.tm_min).zfill(2)}:{str(tm.tm_sec).zfill(2)}"

        for current_socket in wlist:  # send messages to clients who are write ready
            sending = [message for message in messages_to_send if
                       current_socket in message[1] and not message[1].remove(current_socket)]

            if sending:
                messages = []  # in case a couple messages are sent at once
                for message in sending:
                    msg, pending = message
                    msg.tim = tm
                    messages.append(msg)
                current_socket.send(pickle.dumps(tuple(messages)))

        # filters out already messages that are already sent to all clients
        messages_to_send = list(filter(lambda x: len(set(x[1]).intersection(set(client_sockets))), messages_to_send))

        for current_socket in rlist:  # iterate over
            if current_socket is server_socket:
                connection, client_address = current_socket.accept()
                client_sockets.append(connection)
            else:
                if current_socket in clients_chatroom:
                    chatroom = clients_chatroom[current_socket]
                    # chatroom.set_status(current_socket, "ready")  # allows chatroom to handle client
                    ret = chatroom.run_client(current_socket, messages_to_send)  # client handle
                    if ret == "destroyed":  # admin closed the server
                        for client in chatroom.assigned_sockets:
                            chatroom.close_client(client, client_sockets, clients_chatroom)
                    if ret == "closed":  # user disconnected
                        name = ""
                        if current_socket in chatroom.name_socket:
                            name = chatroom.name_socket[current_socket]
                        messages_to_send.append(
                            (Message(f"user {name} disconnected", "&server"), set(chatroom.assigned_sockets)))
                        if chatroom.creator == name:  # if user is the admin, assign new admin (also ensures there is always 1 manager)
                            temp_list = list(chatroom.managers)
                            if len(temp_list) == 1:
                                if len(chatroom.assigned_sockets) > 1:
                                    temp_list = list(chatroom.name_socket.get_two())
                                    chatroom.creator = temp_list[0] if temp_list[0] != chatroom.creator else temp_list[1]
                                    chatroom.managers.add(chatroom.creator)
                            else:
                                chatroom.creator = temp_list[0] if temp_list[0] != chatroom.creator else temp_list[1]

                            messages_to_send.append((Message(
                                f"Main admin {name} disconnected, {chatroom.creator} assigned as new admin.", "&server"),
                                                     set(chatroom.assigned_sockets)))
                        chatroom.close_client(current_socket, client_sockets, clients_chatroom)  # close client
                    if len(chatroom.assigned_sockets) == 0:  # close server if its empty
                        del chatroom_names[chatroom]
                else:  # if client is not in a group chat, they must be new in this server.
                    temp = current_socket.recv(1024)
                    data = temp.decode().split("|")
                    if len(data) != 4:
                        current_socket.close()
                        client_sockets.remove(current_socket)
                        continue

                    # verify values
                    name = data[1]  # making sure client didn't edit their http request to include forbidden values
                    if data[0] == "create":
                        if name:
                            current_socket.close()
                            client_sockets.remove(current_socket)
                            continue
                    else:
                        match = re.match(r"^[0-9]+$", name)
                        if not match or 4 > len(name) or len(name) > 5:
                            current_socket.close()
                            client_sockets.remove(current_socket)
                            continue

                    name = data[2]
                    match = re.match(r"^[a-zA-Z0-9!-*]+$", name)
                    if not match or 5 > len(name) or len(name) > 16:
                        current_socket.close()
                        client_sockets.remove(current_socket)
                        continue

                    name = data[3]
                    match = re.match(r"^[a-zA-Z0-9]+$", name)
                    if not match or 3 > len(name) or len(name) > 16:
                        current_socket.close()
                        client_sockets.remove(current_socket)
                        continue

                    if data[0] == "create":
                        # assign random ID to server
                        r = random.randint(1000, 99999)
                        while str(r) in chatroom_names.get_one():
                            r = random.randint(1000, 99999)
                        chatroom = Chatroom(data[3], str(r), data[2])
                        chatroom_names[chatroom] = str(r)
                    else:
                        # verify ID, password, and unique username
                        if data[1] in chatroom_names:
                            chatroom = chatroom_names[data[1]]
                        else:
                            current_socket.send("ERROR: Non existing chat ID inserted.".encode())
                            current_socket.close()
                            client_sockets.remove(current_socket)
                            continue
                        if data[2] != chatroom.chat_pass:
                            current_socket.send("ERROR: Incorrect password.".encode())
                            current_socket.close()
                            client_sockets.remove(current_socket)
                            continue
                        if data[3] in chatroom.name_socket.get_two():
                            current_socket.send("ERROR: user with the same name already exists.".encode())
                            current_socket.close()
                            client_sockets.remove(current_socket)
                            continue

                    clients_chatroom[current_socket] = chatroom  # add to client lists
                    chatroom.name_socket[data[3]] = current_socket
                    chatroom.assigned_sockets.append(current_socket)
                    # chatroom.client_status[current_socket] = "stalling"

                    current_socket.send("SUCCESS".encode())  # handshake over
                    messages_to_send.append(  # broadcast message in chat
                        (Message(f"user {name} connected", "&server"), set(chatroom.assigned_sockets)))
                    messages_to_send.append((Message(f"Hello! use /help to get a list of commands.\nThe server ID is {chatroom.chat_code}",
                                                     "&server"), {current_socket}))

    server_socket.close()  # bye bye!


if __name__ == "__main__":
    main()


