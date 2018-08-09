#!/usr/bin/env python3

import serial
import time


#serialPort = serial.Serial("/dev/pts/15", 9600, rtscts=True, dsrdtr=True)
serialPort = serial.Serial("/dev/ttyAMA0", 9600, rtscts=True, dsrdtr=True)

class Card:

    def __init__(self):
        self.prev_id = None
        self.current_id = None
        self.repeat = False

    def read(self, idle=False):
        if serialPort.in_waiting < 13:
            return False
        buffer = b''
        while serialPort.in_waiting:
            char = serialPort.read()
            if char == b'\x03':
                break
            buffer += char
        if char == b'\x03' and len(buffer) == 13 and buffer[0] == 2:
            card_header = int(buffer[1:3].decode(), 16)
            checksum =  card_header
            card_number_hex = buffer[3:11].decode()
            for i in (0, 2, 4, 6):
                checksum ^= int(card_number_hex[i:i + 2], 16)
            if (checksum != int(buffer[11:13].decode(), 16)):
                return False
            id = str(int(card_number_hex, 16))
            self.prev_id = self.current_id
            if self.prev_id:
                self.repeat = True if self.prev_id == id else False
            self.current_id = id
            if idle or not self.repeat:
                return True
        return False


if __name__ == "__main__":
    card = Card()

    while True:
        if card.read():
            print(card.current_id, card.repeat)
        time.sleep(.1)

#    print(buffer)

