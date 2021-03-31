class RingBuffer:
    def __init__(self, length):
        self.buffer = [0] * length
        self.bufferLength = length
        self.readIndex = 0
        self.writeIndex = 0
        self.readable = 0
    
    def write(self, values: list):
        for index, val in enumerate(values):
            self.buffer[(index + self.writeIndex) % self.bufferLength] = val
            self.readable += 1
        self.writeIndex = (self.writeIndex + len(values)) % self.bufferLength
    
    def read(self, length = 0):
        if length == 0 or length > self.readable:
            length = self.readable
        output = [0] * length
        for index in range(length):
            output[index] = self.buffer[(index + self.readIndex) % self.bufferLength]
            self.readable -= 1
        self.readIndex = (self.readIndex + length) % self.bufferLength
        return output
    
    def debug(self):
        print(self.buffer)
        print("Length: {}, ReadIndex: {}, WriteIndex: {}, Readable: {}".format(self.bufferLength, self.readIndex, self.writeIndex, self.readable))
