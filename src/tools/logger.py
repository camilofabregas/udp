from datetime import datetime
import os

from progressbar import ProgressBar

class Logger:
    def __init__(self, side, verbose):
        self.side = side
        self.verbose = verbose
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        if self.side == 'client':
            filename = f"logs/client_{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}.log"
            self.file = open(filename, 'w')
        else:
            self.file = open('logs/server.log', 'w')

    def log(self, msg, host=None, port=None, force=False):
        if host and port and self.side == 'server':
            line = f"[{host}:{port}] {msg}"
        else:
            line = msg

        self.file.write(line + '\n')
        if self.verbose or force:
            print(line)
    
    def bar(self, length):
        if self.side == 'client' and not self.verbose:
            self.bar = ProgressBar(max_value=length)
    
    def bar_update(self, value):
        if self.side == 'client' and not self.verbose:
            self.bar.update(value)
    
    def bar_finish(self):
        if self.side == 'client' and not self.verbose:
            self.bar.finish()