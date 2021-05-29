import time
from BLEMidiTranslator.RingBuffer import RingBuffer
from enum import Enum

class EncoderMode(Enum):
    """
    Encoder mode specifies which mode allowed to use 
    in each ble-midi package
    There are 4 modes according to specification

    Full package include header, timestamp, and status 
    bytes in every message
    WithStatus package omit header byte if possible
    WithTimestamp package omit header, and status 
    byte if possible
    RunningStatus package omit header, timestamp, and 
    status bytes if possible

    RunningStatus is good for speed, it's most minimal
    package but some devices don't recognize them
    Full is good for compatibility but overhead could
    impact speed
    WithStatus works most of the time
    Choose wisely
    """
    Full = 0x01
    WithStatus = 0x02
    WithTimestamp = 0x03
    RunningStatus = 0x04

class Encoder:
    """
    Standart Midi to BLE Midi converter class
    """
    def __init__(self, mode: EncoderMode = EncoderMode.WithStatus, bufferLength: int = 1024) -> None:
        """
        Standart Midi to BLE Midi converter initializer

        :param mode: Encoder mode, look EncoderMode class
        for more information
        :param bufferLength: Length of encoder buffer.
        To use call writeToBuffer and encodeBuffer functions
        """
        self.mode = mode
        self.buffer = RingBuffer(bufferLength)
    
    def encode(self, message: list, mode = None) -> list:
        """
        Encode Midi message(s) to BLE Midi message(s)

        :param message: Should contain legal midi message(s)
        Multiple midi messages in one list accepted
        :param mode: Encoder mode. If not specified
        encoder will use mode specified in initializer
        """
        if mode == None:
            mode = self.mode
        if mode == EncoderMode.RunningStatus:
            return self.encodeRunningStatus(message)
        elif mode == EncoderMode.WithTimestamp:
            return self.encodeWithTimestamp(message)
        elif mode == EncoderMode.WithStatus:
            return self.encodeWithStatus(message)
        else:
            return self.encodeFull(message)
    
    def encodeFull(self, message: list) -> list:
        """
        Encode Midi message(s) to BLE Midi message(s)
        without omitting any header byte
        Look EncoderMode class for more information

        :param message: Should contain legal midi message(s)
        Multiple midi messages in one list accepted
        """
        buffer = []
        for val in message:
            currentTime = int(time.time() * 1000) % (0x1 << 13)
            header = 0x80 | ((currentTime >> 7) & 0x3F)
            timestamp = 0x80 | (currentTime & 0x7F)
            if val & 0x80:
                if val == 0xF7:
                    buffer.append(val)
                else:
                    buffer.append(header)
                    buffer.append(timestamp)
                    buffer.append(val)
            else:
                buffer.append(val)
        return buffer
    
    def encodeWithStatus(self, message: list) -> list:
        """
        Encode Midi message(s) to BLE Midi message(s)
        omitting header byte if possible
        Look EncoderMode class for more information

        :param message: Should contain legal midi message(s)
        Multiple midi messages in one list accepted
        """
        oldHeader = 0
        buffer = []
        for val in message:
            currentTime = int(time.time() * 1000) % (0x1 << 13)
            header = 0x80 | ((currentTime >> 7) & 0x3F)
            timestamp = 0x80 | (currentTime & 0x7F)
            if val & 0x80:
                if val == 0xF7:
                    buffer.append(val)
                else:
                    if oldHeader != header:
                        buffer.append(header)
                        buffer.append(timestamp)
                        buffer.append(val)
                        oldHeader = header
                    else:
                        buffer.append(timestamp)
                        buffer.append(val)
            else:
                buffer.append(val)
        return buffer
    
    def encodeWithTimestamp(self, message: list) -> list:
        """
        Encode Midi message(s) to BLE Midi message(s)
        omitting header and status byte if possible
        Look EncoderMode class for more information

        :param message: Should contain legal midi message(s)
        Multiple midi messages in one list accepted
        """
        oldHeader = 0
        lastStatus = 0
        buffer = []
        for val in message:
            currentTime = int(time.time() * 1000) % (0x1 << 13)
            header = 0x80 | ((currentTime >> 7) & 0x3F)
            timestamp = 0x80 | (currentTime & 0x7F)
            if val & 0x80:
                if val == 0xF7:
                    buffer.append(val)
                else:
                    if oldHeader != header:
                        buffer.append(header)
                        buffer.append(timestamp)
                        buffer.append(val)
                        oldHeader = header
                        lastStatus = val
                    elif lastStatus != val:
                        buffer.append(timestamp)
                        buffer.append(val)
                        lastStatus = val
                    else:
                        buffer.append(timestamp)
            else:
                buffer.append(val)
        return buffer
    
    def encodeRunningStatus(self, message: list) -> list:
        """
        Encode Midi message(s) to BLE Midi message(s)
        omitting header, timestamp, status byte if possible
        Look EncoderMode class for more information

        :param message: Should contain legal midi message(s)
        Multiple midi messages in one list accepted
        """
        oldHeader = 0
        lastStatus = 0
        buffer = []
        for val in message:
            currentTime = int(time.time() * 1000) % (0x1 << 13)
            header = 0x80 | ((currentTime >> 7) & 0x3F)
            timestamp = 0x80 | (currentTime & 0x7F)
            if val & 0x80:
                if val == 0xF7:
                    buffer.append(val)
                else:
                    if oldHeader != header:
                        buffer.append(header)
                        buffer.append(timestamp)
                        buffer.append(val)
                        oldHeader = header
                        lastStatus = val
                    elif lastStatus != val:
                        buffer.append(timestamp)
                        buffer.append(val)
                        lastStatus = val
                    else:
                        pass
            else:
                buffer.append(val)
        return buffer

    def writeToBuffer(self, message: list) -> None:
        """
        Write midi message(s) to buffer for encoding it
        later with larger group

        :param message: Should contain legal midi message(s)
        Multiple midi messages in one list accepted
        """
        self.buffer.write(message)
    
    def encodeBuffer(self, mode: EncoderMode = None) -> list:
        """
        Encode Midi message(s) in buffer to BLE Midi message(s)

        :param mode: Encoder mode. If not specified
        encoder will use mode specified in initializer
        """
        return self.encode(self.buffer.read(), mode)

class Decoder:
    """
    BLE Midi to Standart Midi converter class
    """
    def __init__(self, bufferLength: int = 1024):
        """
        BLE Midi to Standart Midi converter initializer

        :param bufferLength: Length of decoder buffer.
        To use call writeToBuffer and decodeBuffer functions
        """
        self.buffer = RingBuffer(bufferLength)
    
#    def decode(self, message: list) -> list[tuple[int, list[int]]]: # not much compatible
    def decode(self, message: list):
        """
        Decode BLE Midi message(s) to Midi message(s)

        :param message: Should contain legal ble midi message(s)
        Multiple ble midi messages in one list accepted
        """
        header = 0
        timestamp = 0
        status = 0
        headerPointer = 0
        dataPointer = 0
        startPointer = 0
        output = []
        returnAfterData = False
        while True:
            # start pointer points start of header bytes
            # header pointer points end of header, start of data bytes
            # data pointer points end of data bytes
            startPointer = dataPointer
            headerPointer = dataPointer
            # we read every message which MSb is 1
            # eg. header, timestamp, status messages
            while message[headerPointer] >= 0x80 and headerPointer < len(message) - 1:
                headerPointer += 1
            # if there is no remaining data
            if headerPointer == len(message) - 1:
                # check if last byte is zero-data byte system message
                status = message[headerPointer]
                if status == 0xF6 or status == 0xF8 or status == 0xFA or \
                   status == 0xFB or status == 0xFC or status == 0xFE or status == 0xFF:
                   messageTime = ((header & 0x3F) << 7) | (timestamp & 0x7F)
                   output.append((messageTime, [message[headerPointer]]))
                return output
            # process header
            if headerPointer - startPointer == 3:
                header = message[headerPointer - 3]
                timestamp = message[headerPointer - 2]
                status = message[headerPointer - 1]
            elif headerPointer - startPointer == 2:
                timestamp = message[headerPointer - 2]
                status = message[headerPointer - 1]
            else:
                timestamp = message[headerPointer - 1]
            # point start of data bytes
            dataPointer = headerPointer
            # calculate message time
            messageTime = ((header & 0x3F) << 7) | (timestamp & 0x7F)
            # pass through every data byte
            while message[dataPointer] < 0x80 and dataPointer < len(message) - 1:
                dataPointer += 1
            if dataPointer == len(message) - 1:
                dataPointer += 1
                returnAfterData = True
            # process data
            # if system exclusive
            if status == 0xF0:
                dataPointer += 1 # we read 1 non-data byte from message
                output.append(((messageTime), [status] + message[headerPointer:headerPointer + (dataPointer - headerPointer)]))
            # if there is no data byte
            elif dataPointer - headerPointer == 0:
                output.append((messageTime, [status]))
            # if only one byte present in data
            elif dataPointer - headerPointer == 1:
                output.append((messageTime, [status] + [message[headerPointer]]))
            # it two byte present in data
            elif dataPointer - headerPointer == 2:
                output.append((messageTime, [status] + message[headerPointer:headerPointer + 2]))
            # if more than two byte present in data it should running status
            else:
                cmd = status & 0x80
                # these are two byte midi messages
                if cmd == 0x80 or cmd == 0x90 or cmd == 0xA0 or cmd == 0xB0 or cmd == 0xE0:
                    for i in range(headerPointer, dataPointer, 2):
                        output.append((messageTime, [status] + message[i:i + 2]))
                # these are one byte midi messages
                if cmd == 0xC0 or cmd == 0xD0:
                    for i in range(headerPointer, dataPointer, 1):
                        output.append((messageTime, [status] + [message[i]]))
            if returnAfterData:
                return output

    def writeToBuffer(self, message: list) -> None:
        """
        Write ble midi message(s) to buffer for encoding it
        later with larger group

        :param message: Should contain legal ble midi message(s)
        Multiple ble midi messages in one list accepted
        """
        self.buffer.write(message)
    
    def decodeBuffer(self) -> list:
        """
        Decode Midi message(s) in buffer to BLE Midi message(s)
        """
        return self.decode(self.buffer.read())