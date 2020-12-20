"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import json

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.key = generateKey()

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '.\n\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        if peer == 'lobby':
                            self.out_msg += 'Welcome to the public Tomato Lobby.\n'
                            self.out_msg += 'Start chatting to meet new friends.\n'
                            self.out_msg += "To exit type 'bye'\n"
                            self.out_msg += '-----------------------------------\n'
                        else:
                            self.out_msg += 'Connected to ' + peer + '. Chat away!\n\n'
                            self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"][1:].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p':
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"][1:].strip()
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'
                
                elif my_msg[0:6] == 'random':
                    self.out_msg += 'Searching for potential matches\n'
                    mysend(self.s, json.dumps({"action":"random","caller":'',"receiver":''}))
                    #caller and receiver are empty because this is not a new request
                    userAvailability = json.loads(myrecv(self.s))["results"]
                    if userAvailability == "n":
                        self.out_msg += 'Sorry no one is available at the moment, please try again later or visit our lobby!\n'
                
                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.peer = peer_msg["from"]
                    self.out_msg += "Connected to " + peer_msg["from"]
                    self.set_state(S_CHATTING)
                if peer_msg["action"] == "consent":
                    self.peer = peer_msg["from"]
                    self.out_msg += "A random user would like to connect with you, do you want to connect with them? ('y' or 'n')\n\n"
                    self.set_state(S_CONSENT)

#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                encrypted_msg = self.key.encrypt(my_msg.encode())
                mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":encrypted_msg.decode()}))
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                elif peer_msg["action"] == 'exchange':
                    #newString = self.key.decrypt(peer_msg["message"].encode())
                    self.out_msg += peer_msg["from"].replace("[", "").replace("]", ": ") + peer_msg["message"]
                    #self.out_msg += peer_msg["from"].replace("[", "").replace("]", ": ") + newString.decode()
                elif peer_msg["action"] == "connect":
                    self.out_msg += "Connected to " + peer_msg["from"]

            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
                
#==============================================================================
# Built for the random function
# This is event handling instate "S_CONSENT"
#==============================================================================
        elif self.state == S_CONSENT:
            if len(my_msg) > 0:
                #the counter below is to ensure that an indecisive user doesn't make the other wait
                self.get_myname()
                #due to complications with a while loop, we simply limited to one correct answer or not
                
                if my_msg=='y':
                    self.out_msg += 'Connecting you now...'
                    if self.connect_to(self.peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connected to a random user. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'
                    #for anon we simply do not display the name
                elif my_msg=='n':
                    #call random again, however must come from PEER not the person in consent
                    #we simply send the user's name
                    mysend(self.s, json.dumps({"action":"random", "caller":self.peer, "receiver":self.me}))
                    self.set_state(S_LOGGEDIN)
                
                else:
                    self.out_msg += "Sorry, we didn't quite get that, can you reply with 'y' or 'n' please?\n"
                   
                    
                    
                

#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
