from src.arqs.fin import fin_receiver, fin_sender
from src.messages.header import *
import threading
from math import ceil
from time import time, sleep
from progressbar import ProgressBar

from src.tools.constants import CHUNK_SIZE, FIXED_TIMEOUT, INITIAL_TIMEOUT, WINDOW_SIZE

class SelectiveRepeatSender:
    def __init__(self, chunks, config, socket, socket_lock, queue, window_size=WINDOW_SIZE):
        self.chunks = chunks
        self.config = config
        self.socket = socket
        self.socket_lock = socket_lock
        self.queue = queue
        self.timeout = INITIAL_TIMEOUT
  
        self.sent_first_time = 0        
        self.window_size = window_size
        self.first_w_seq = 0
        self.window_sent = [(0, None)] * self.window_size
        self.window_ack = [False] * self.window_size
        self.config.logger.bar(len(self.chunks))
        

    def update_timeout(self, rtt):
      self.timeout = rtt * 2
      if self.timeout > 1:
        self.timeout = 1
      if self.timeout < 0.001:
        self.timeout = 0.001
      
    def not_finished(self):
      return self.first_w_seq < len(self.chunks)
    
    def unsend(self, seq):
      i = seq - self.first_w_seq
      if i >= 0 and i < self.window_size:
        self.window_sent[i] = (0, None)  
    
    def send(self, seq, resend=False):
      i = seq - self.first_w_seq
      if i >= 0 and i < self.window_size:
        chunk = self.chunks[seq]
        with self.socket_lock:
          self.socket.sendto(encode(Data(seq, chunk)),
                                (self.config.host, self.config.port))
  
        self.config.logger.log(f'>>  DATA {seq}', self.config.host, self.config.port)
        timestamp = time()
        timer = threading.Timer(self.timeout, self.unsend, [seq])
        timer.start()
        self.window_sent[i] = (timestamp, timer)
    
    def try_send_window(self):
      for i in range(0, self.window_size):
        if self.first_w_seq + i < len(self.chunks) and self.window_sent[i][1] == None:
          self.sent_first_time +=1
          self.send(self.first_w_seq + i)
          
    def set_ack(self, ack_seq):
      self.config.logger.log(f'<<  ACK {ack_seq}',  self.config.host, self.config.port)
      i = ack_seq - self.first_w_seq
      if i >= 0 and i < self.window_size:
        timestamp, timer = self.window_sent[i]
        timer.cancel()
        self.update_timeout(time() - timestamp)
        
        self.window_ack[i] = True

    def update_window(self):
      while self.window_ack[0]:
        self.window_ack.pop(0)
        self.window_ack.append(False)
        
        timestamp, timer = self.window_sent.pop(0)
        timer.cancel()
        self.window_sent.append((0, None))
        
        self.first_w_seq += 1
        self.config.logger.bar_update(self.first_w_seq)

      
    def run(self):
      while self.not_finished():
        self.try_send_window()
        
        try:
          response = self.queue.get(timeout=self.timeout)
          while response:
            if response.type == 'ack':
              self.set_ack(response.seq)
            response = self.queue.get(Block=False)
            
        except:
          pass
        self.update_window()
        
      self.config.logger.bar_finish()
      fin_sender(self.socket, self.socket_lock, self.config, self.queue, self.timeout)  
      self.config.logger.log('Selective Repeat Terminado', self.config.host, self.config.port)

class SelectiveRepeatReceiver:
    def __init__(self, config, socket, socket_lock, queue, window_size=WINDOW_SIZE):
        self.config = config
        self.chunks = [None] * ceil(self.config.filesize / CHUNK_SIZE)
        self.socket = socket
        self.socket_lock = socket_lock
        self.queue = queue
        
        self.window_size = window_size
        self.first_w_seq = 0
        self.window_received = [None] * self.window_size
        self.config.logger.bar(len(self.chunks))
        
    def not_finished(self):
      return self.first_w_seq < len(self.chunks)
        
    def send_ack(self, seq):
      with self.socket_lock:
        self.socket.sendto(encode(Ack(seq)),
                               (self.config.host, self.config.port))
        self.config.logger.log(f'>>  ACK {seq}',  self.config.host, self.config.port)

        
    def handle_data(self, data):
      i = data.seq - self.first_w_seq
      self.config.logger.log(f'<<  DATA {data.seq}',  self.config.host, self.config.port)
      if i < 0:
        self.send_ack(data.seq)
      elif i < self.window_size:
        self.chunks[data.seq] = data.data
        self.send_ack(data.seq)
        self.window_received[i] = True
      
        
    def update_window(self):
      while self.window_received[0]:
        self.window_received.pop(0)
        self.window_received.append(False)
        
        self.first_w_seq += 1
        self.config.logger.bar_update(self.first_w_seq)
        
        
    def run(self):
      while self.not_finished():
        try:
          response = self.queue.get()            
          while response:
            if response.type == 'data':
              self.handle_data(response)
            response = self.queue.get(Block=False)
                  
        except:
          pass
        self.update_window()
          
      self.config.logger.bar_finish()
      fin_receiver(self.socket, self.socket_lock, self.config, self.queue, FIXED_TIMEOUT) 
      self.config.logger.log('Selective Repeat Terminado\n',  self.config.host, self.config.port)
      return self.chunks
