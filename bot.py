#!/usr/bin/python3

import os
import sys
import socket
import ssl
import argparse
import threading

def connect(servername, port, use_ssl):
    """Connect to the specified server.  Defaults are handled by the argument parser."""
    passwd = 'puppass'
    nick = 'PupBot'
    ident = 'PupBot'
    name = 'PupBot'
    owner = 'Daniel Wilson'

    comm_sock = socket.socket(family=socket.AF_UNIX)
    comm_sock.setblocking(True)

    hostname = socket.gethostname()
    sock_name = '{pid}-{host}'.format(pid=os.getpid(), host=hostname)
    
    print('Started pupbot on host: {h}, port: {p}, ssl: {s}, pid: {pid}'.format(h=hostname, p=port, s=use_ssl, pid=os.getpid()))
    
    comm_sock.bind('sockets/' + sock_name)
    comm_sock.listen(0)

    if use_ssl:
        sock = ssl.wrap_socket(socket.socket())
    else:
        sock = socket.socket()
    sock.connect((servername, port))
    sock.send(('PASS ' + passwd + '\r\n').encode())
    sock.send(('NICK ' + nick + '\r\n').encode())
    sock.send(('USER ' + ident + ' ' + hostname + ' ' + servername + ' :' + name + '\r\n').encode())

    sock.setblocking(False)
    #Thread off command watcher
    events = dict(stop=threading.Event(), \
                  list=threading.Event(), \
                  join=threading.Event(), \
                  part=threading.Event())
    data = dict()
    lock = threading.Lock()
    comm_thr = threading.Thread(target=accept_comm, args=(comm_sock, events, data, lock))
    comm_thr.daemon = True
    comm_thr.start()
    #enter event loop
    while 1:
        if events['stop'].is_set():
            #Send quit message to server, close sockets, return
            print('Stopping bot with pid: {pid}'.format(pid=os.getpid()))
            msg = 'QUIT :Someone told me to stop!\r\n'
            sock.send(msg.encode())
            comm_sock.shutdown(socket.SHUT_RDWR)
            comm_sock.close()
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            sys.exit()
        elif events['list'].is_set():
            events['list'].clear()
            print('Requesting channels for bot with pid: {pid}'.format(pid=os.getpid()))
            msg = 'LIST\r\n'
            sock.send(msg.encode())
        elif events['join'].is_set():
            events['join'].clear()
            with lock:
                chan_name = data['channel']
            print('Joining channel: {cn}'.format(cn=chan_name))
            msg = 'JOIN {cn}\r\n'.format(cn=chan_name)
            sock.send(msg.encode())
        elif events['part'].is_set():
            events['part'].clear()
            with lock:
                chan_name = data['channel']
            print('Parting channel: {cn}'.format(cn=chan_name))
            msg = 'PART {cn}\r\n'.format(cn=chan_name)
            sock.send(msg.encode())
        try:
            message = sock.recv(4096).decode()
            message_parts = message.split('\r\n')
            for i in range(len(message_parts)-1):
                message = message_parts[i]
                msgparts = message.split()
                parsemsg(sock, msgparts)
        except IOError:
            pass

def accept_comm(comm_sock, events, data, lock):
    while 1:
        (conn, addr) = comm_sock.accept()
        conn.setblocking(True)
        print('Connection made with:{a}'.format(a=addr))
        command = conn.recv(4096)
        command = command.decode()
        logcmd(command)
        command = command.split()
        if command[0] == 'stop':
            events['stop'].set()
            break
        elif command[0] == 'list':
            events['list'].set()
        elif command[0] == 'join':
            events['join'].set()
            channel = command[1]
            with lock:
                data['channel'] = channel
        elif command[0] == 'part':
            events['part'].set()
            channel = command[1]
            with lock:
                data['channel'] = channel
 
def logmsg(message):
    """Logs a message in logs/<pid>-messages"""
    f = open('logs/{pid}-messages'.format(pid=os.getpid()), 'a')
    f.write(message + '\n')
    f.close()

def logcmd(command):
    """Logs a command in logs/<pid>-commands"""
    f = open('logs/{pid}-commands'.format(pid=os.getpid()), 'a')
    f.write(command + '\n')
    f.close()

def parsemsg(sock, msgparts):
    """Parse a message and act on commands"""
    if msgparts[0] == 'PING':
        content = msgparts[1]
        sock.send(('PONG ' + content + '\r\n').encode())
    elif msgparts[1] == 'PRIVMSG':
        logmsg(' '.join(msgparts))
        message = bot_logic.Message(msgparts)
    elif msgparts[1] == '321':  #list start reply
        logmsg(' '.join(msgparts))
        server = msgparts[0][1:]
        f = open('channels/{pid}'.format(pid=os.getpid()),'w')
        f.write('Channels on server: {serv}\n'.format(serv = server))
        f.write('Channel:    Users:    Topic:\n')
        f.close()
    elif msgparts[1] == '322':  #list data reply
        logmsg(' '.join(msgparts))
        channel = msgparts[3] + '; ' +  msgparts[4] + '; ' + ' '.join(msgparts[5:])[1:] + '\n'
        f = open('channels/{pid}'.format(pid=os.getpid()),'a')
        f.write(channel)
        f.close()
    elif msgparts[1] == '323':  #list end reply
        logmsg(' '.join(msgparts))
        f = open('channels/{pid}'.format(pid=os.getpid()),'r')
        data = f.read()
        f.close()
        print(data)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Connect to an irc server with PupBot')
    parser.add_argument('-H', '--hostname', default='localhost', help="Set the hostname. Defaults to 'localhost'")
    parser.add_argument('-P', '--port', default=6667, type=int, help="Set the port. Defaults to '6667'")
    parser.add_argument('-S', '--ssl', default=False, action='store_true', help="Enable ssl connection.")
    args = parser.parse_args()

    connect(servername=args.hostname, port=args.port, use_ssl=args.ssl)
