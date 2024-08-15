from src.arqs.fin import fin_receiver, fin_sender
from src.arqs.selective_repeat import SelectiveRepeatReceiver, SelectiveRepeatSender
from src.messages.data import Data
from src.messages.header import *
from queue import *
from time import time
from math import ceil

from src.tools.constants import *
        
class StopNWaitSender:
    def __init__(self, chunks, config, socket, socket_lock, queue):
        self.chunks = chunks
        self.config = config
        self.socket = socket
        self.socket_lock = socket_lock
        self.queue = queue
        self.seq = 0
        self.timeout = INITIAL_TIMEOUT
        self.sent_timestamp = 0
        self.config.logger.bar(len(self.chunks))

    def update_timeout(self, rtt):
      self.timeout = rtt * 2
      if self.timeout > 1:
        self.timeout = 1
      if self.timeout < 0.001:
        self.timeout = 0.001
        
    def send(self):
        with self.socket_lock:
            self.socket.sendto(encode(Data(self.seq, self.chunks[self.seq])),
                               (self.config.host, self.config.port))
            self.sent_timestamp = time()
        self.config.logger.log(f">>  DATA {self.seq}")

    def run(self):
        while self.seq < len(self.chunks): 
            self.send()

            try:
                response = self.queue.get(timeout=self.timeout)
                if response.type == 'ack':
                    self.config.logger.log(f"<<  ACK {response.seq}")
                    if response.seq == self.seq:
                        self.update_timeout(time() - self.sent_timestamp)
                        self.seq += 1
                        self.config.logger.bar_update(self.seq)


            except:
                pass                
       
        self.config.logger.bar_finish()
        fin_sender(self.socket, self.socket_lock, self.config, self.queue, self.timeout) 
        self.config.logger.log('Stop&Wait Terminado\n', self.config.host, self.config.port)


class StopNWaitReceiver:
    def __init__(self, config, socket, socket_lock, queue):
        self.chunks = []
        self.config = config
        self.socket = socket
        self.socket_lock = socket_lock
        self.queue = queue
        self.seq = -1
        self.sent_timestamp = 0
        self.timeout = INITIAL_TIMEOUT * 20
        
        self.total_chunks = ceil(self.config.filesize / CHUNK_SIZE)
        self.config.logger.bar(self.total_chunks)

    def send(self, seq):        
        with self.socket_lock:
            self.socket.sendto(encode(Ack(seq)), (self.config.host, self.config.port))
        self.config.logger.log(f">>  ACK {seq}", self.config.host, self.config.port)
        self.sent_timestamp = time()

    def run(self):
        while self.seq < self.total_chunks - 1:
            
            try:
                response = self.queue.get()
                if response.type == 'data':
                    self.config.logger.log(f"<<  DATA {response.seq}", self.config.host, self.config.port)
                    if response.seq == self.seq + 1:
                        self.chunks.append(response.data)
                        self.seq = response.seq
                        self.config.logger.bar_update(self.seq)

            except:
                pass
            
            if self.seq >= 0:
                self.send(self.seq)

        self.config.logger.bar_finish()
        fin_receiver(self.socket, self.socket_lock, self.config, self.queue, self.timeout) 
        self.config.logger.log('Stop&Wait Terminado\n', self.config.host, self.config.port)
        return self.chunks