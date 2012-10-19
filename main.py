#!/usr/bin/python3

import socket
import argparse
import subprocess
import sys
import os
import fileinput

def start(args):
    print('Starting pupbot on host: {h}, port: {p}, ssl: {s}'.format(h=args.hostname, p=args.port, s=args.ssl))
    hostname = args.hostname
    port = args.port
    use_ssl = args.ssl
    
    if use_ssl:
        process = subprocess.Popen(['python3','bot.py', '-H', hostname, '-P', str(port), '-S'])
    else:
        process = subprocess.Popen(['python3','bot.py', '-H', hostname, '-P', str(port)]) 
    #add to running process
    f = open('logs/bots', 'a')
    f.write('{pid}\n'.format(pid=process.pid))
    f.close()
    sys.exit()
def stop(args):
    pid = args.pid
    hostname = socket.gethostname()
    
    sock_addr = '{pid}-{host}'.format(pid=pid, host=hostname)
    sock = socket.socket(socket.AF_UNIX)
    sock.setblocking(True)
    sock.connect('sockets/' + sock_addr)
    sock.send(b'stop')
    #remove from running processes
    f = open('logs/bots', 'r')
    data = f.read().split('\n')
    f.close()
    for d in data:
        if d == str(pid):
            data.remove(d)
    data = '\n'.join(data)
    f = open('logs/bots', 'w')
    f.write(data)
    f.close()
def listchan(args):
    pid = args.pid
    hostname = socket.gethostname()

    sock_addr = '{pid}-{host}'.format(pid=pid, host=hostname)
    sock = socket.socket(socket.AF_UNIX)
    sock.setblocking(True)
    sock.connect('sockets/' + sock_addr)
    sock.send(b'list')
def join(args):
    pid = args.pid
    channel = args.channel
    if channel.startswith('#')==False:
        channel = '#' + channel
    msg = 'join ' + channel
    hostname = socket.gethostname()

    sock_addr = '{pid}-{host}'.format(pid=pid, host=hostname)
    sock = socket.socket(socket.AF_UNIX)
    sock.setblocking(True)
    sock.connect('sockets/' + sock_addr)
    sock.send(msg.encode())
def part(args):
    pid = args.pid
    channel = args.channel
    if channel.startswith('#')==False:
        channel = '#' + channel
    msg = 'part ' + channel
    hostname = socket.gethostname()

    sock_addr = '{pid}-{host}'.format(pid=pid, host=hostname)
    sock = socket.socket(socket.AF_UNIX)
    sock.setblocking(True)
    sock.connect('sockets/' + sock_addr)
    sock.send(msg.encode())
def bots(args):
    f = open('logs/bots', 'r')
    data = f.read()
    f.close()
    print('Running process ids\n')
    print(data)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Connect to an irc server with PupBot')
    subparsers = parser.add_subparsers(title='Commands', description='Commands to send to the bot.')
    
    parser_start = subparsers.add_parser('start', help="Start a new bot.")
    parser_start.add_argument('-H', '--hostname', default='localhost', help="Set the hostname. Defaults to 'localhost'")
    parser_start.add_argument('-P', '--port', default=6667, type=int, help="Set the port. Defaults to '6667'")
    parser_start.add_argument('-S', '--ssl', default=False, action='store_true', help="Enable ssl connection.")
    parser_start.set_defaults(func=start)
    
    parser_stop = subparsers.add_parser('stop', help="Stop the specified bot.")
    parser_stop.add_argument('pid', type=int, help="Process ID of the bot.")
    parser_stop.set_defaults(func=stop)

    parser_list = subparsers.add_parser('list', help="List all channels on irc server.")
    parser_list.add_argument('pid', type=int, help="Process ID of the bot.")
    parser_list.set_defaults(func=listchan)

    parser_join = subparsers.add_parser('join', help="Join specified channel.")
    parser_join.add_argument('pid', type=int, help="Process ID of the bot.")
    parser_join.add_argument('channel', help="Channel name.")
    parser_join.set_defaults(func=join)

    parser_part = subparsers.add_parser('part', help="Part from specified channel.")
    parser_part.add_argument('pid', type=int, help="Process ID of the bot.")
    parser_part.add_argument('channel', help="Channel name.")
    parser_part.set_defaults(func=part)

    parser_bots = subparsers.add_parser('bots', help="List all running bots.")
    parser_bots.set_defaults(func=bots)
    
    args = parser.parse_args()
    args.func(args)

