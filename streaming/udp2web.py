#!/usr/bin/env python

# Suggestions for improvement
# 1. use only one socket for all UDP connections
# 2. print status messages inside each thread. Maybe the "logging" command could help
# The array "data" is shared among multiple threads. When it gets empty, e.g., the wave system is not streaming,
# the empty thread blocks the other. Suggestion: make one "data" array for each thread to avoid blocking.
# Alternatively, make a data packet of standard size concatenating DP coordinates and wave characteristics.
# If the data array is empty, fill the corresponding coordinates with zeros.
# When the packet arrives on the client, parse the coordinates and dismiss the empty coordinates.

import threading
from queue import Queue

# WS server that sends messages at random intervals
import asyncio
import random
import websockets

# socket_echo_server_dgram.py
import socket
import sys
import struct

# Queue instances
##queue_wave = Queue()
##queue_ship = Queue()
queue = Queue()
queue_setpoint = Queue()

# HBM related variables
hbm_log = []
wave_log = []
wave_list = []
# remember to set baseline to neutral probe reading
baseline = 0
threshold = 0.3

# Connection variables
portNumHBM  = 12000
portNumProp = 12001
portNumAz   = 12002
thisIP   = '192.168.1.128'
matlabIP = '192.168.1.113'
web_server_ip = "127.0.0.1"
web_server_port = 56780

def udp_server_az():
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind the socket to the respective port
    addrToBind = (thisIP, portNumAz)
    sock.bind(addrToBind)

    addrToSend = (matlabIP, portNumAz)

    # Sent setpoints to Dynamic Positioning module. Desired setpoint in format
    # [x, y, yaw]
    #setpoint = b'1.1, 1.2, 1.3'
    while True:
        setpoint = str.encode(queue_setpoint.get())
        sock.sendto(setpoint, addrToSend)

def udp_server_prop():
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port 12001
    udp_server_address = (thisIP, portNumProp)
    sock.bind(udp_server_address)
    #print('Starting UDP server on {} port {}\n'.format(*udp_server_address))

    while True:
        # expected buffer size
        data, address = sock.recvfrom(4096)
        # string with the following readings: st, pt, bow
        # counter, rpm az, az, bow, degrees alpha az, az, bow, vessel pos x, y, z
        # vessel rot x, y, z
        queue.put(data)

def udp_server_wave():
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the port
    udp_server_address = (thisIP, portNumHBM)
    print('Starting UDP server on {} port {}\n'.format(*udp_server_address))
    sock.bind(udp_server_address)

    while True:
        # expected buffer size of 64 bytes
        data, address = sock.recvfrom(64)

        # id, id, number of channels, counter, time, null, null,
        # wp1, wp2, wp3, wp4, time, null, null, trigger, null,
        # null, null
        format = 'cchIffffffffffffff'
        HBM = struct.unpack(format, data)
        no_channels = HBM[2]
        counter = HBM[3]
        time = HBM[4]
        wp1 = HBM[7]
        wp2 = HBM[8]
        wp3 = HBM[9]
        wp4 = HBM[10]
        time_reprise = HBM[11]
        trigger = HBM[14]
        parsedPackt = [time, wp2, counter]
        hbm_log.append(parsedPackt)

        elevation = wp2 - baseline
        wave_log_len = len(wave_log)

        if time != -1000000.0 and parsedPackt[0] != -1000000.0 and parsedPackt[1] != -1000000.0:
            if abs(elevation) > threshold:
                if not wave_log:
                    wave_log.append(parsedPackt)
                elif elevation > 0:
                    # chek if point is a peak candidate
                    if wave_log[-1][1] - baseline < 0:
                        wave_log.append(parsedPackt)
                    elif parsedPackt[1] > wave_log[-1][1]:
                        wave_log[-1] = parsedPackt
                else:
                    # check if point is a valley candidate
                    if wave_log[-1][1] - baseline > 0:
                        wave_log.append(parsedPackt)
                    elif parsedPackt[1] < wave_log[-1][1]:
                        wave_log[-1] = parsedPackt

        if len(wave_log) > wave_log_len:
            if len(wave_log) == 3:
                wave_height = abs(wave_log[-2][1] - wave_log[-3][1])
                wave_period = 2 * (wave_log[-2][0] - wave_log[-3][0])
                if wave_log[-3][1] - wave_log[-2][1] > 0:
                    # next is a crest
                    wave_phase = 0
                else:
                    # next is a valley
                    wave_phase = 180
                queue.put([wave_height, wave_period, wave_phase])
                wave_list.append([wave_height, wave_period, wave_phase])
            elif len(wave_log) > 3:
                test_wave_height = abs(wave_log[-2][1] - wave_log[-3][1])
                test_wave_period = 2 * (wave_log[-2][0] - wave_log[-3][0])
		# try to avoid misidentification of a new wave due to small reading errors
                if (test_wave_height - wave_height)/wave_height > 0.02 or (test_wave_period - wave_period)/wave_period > 0.02:
                    wave_height = test_wave_height
                    wave_period = test_wave_period
                    if wave_log[-3][1] - wave_log[-2][1] > 0:
                        # next is a crest
                        wave_phase = 0
                    else:
                        # next is a valley
                        wave_phase = 180
                    queue.put([wave_height, wave_period, wave_phase])
                    wave_list.append([wave_height, wave_period, wave_phase])
            wave_log_len = len(wave_log)

##        print('UDP server received {} bytes from {}'.format(
##            len(data), address))
##        print(HBM)

def web_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    async def sendReading(websocket, path):
        # this version of the command eventually halts the sending of packets
        #while not queue_wave.empty():
        while True:
##            wave_data = str(queue_wave.get())
##            print(wave_data)
##            ship_data = str(queue_ship.get())
##            # if wave ship
##            juntar os dois
##            # if wave
##            ship null
##            # 
            ## sprintf(
##            print(wave_data)
##            print(ship_data)
##            await websocket.send(wave_data)
##            await websocket.send(ship_data)
            data = str(queue.get())
            await websocket.send(data)
            await asyncio.sleep(0.005)
    async def rcvReading(websocket, path):
        while True:
            message = await websocket.recv()
            queue_setpoint.put(message)
    async def handler(websocket, path):
        # both send and receive need to be working
        rcv_Task = asyncio.ensure_future(rcvReading(websocket, path))
        send_Task = asyncio.ensure_future(sendReading(websocket, path))
        done, pending = await asyncio.wait(
            [rcv_Task, send_Task],return_when = asyncio.FIRST_COMPLETED,
            )
        #for task in pending:
        #    task.cancel()

    start_server = websockets.serve(handler, web_server_ip, web_server_port)

    loop.run_until_complete(start_server)
    loop.run_forever()

if __name__ == '__main__':
    # Initialize threads
    udp_az = threading.Thread(target=udp_server_az, name='UDP-thread-az')
    udp_prop = threading.Thread(target=udp_server_prop, name='UDP-thread-prop')
    udp_wave = threading.Thread(target=udp_server_wave, name='UDP-thread-wave')
    web = threading.Thread(target=web_server, name='Websocket-thread')

    # Start threads
    udp_az.start()
    udp_prop.start()
    udp_wave.start()
    web.start()
