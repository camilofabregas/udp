from src.messages.ack import Ack
from src.messages.fin import Fin
from src.messages.header import encode
from src.tools.constants import FIN_TIMEOUTS


def fin_sender(socket, socket_lock, config, queue, timeout):
    timeouts_left = FIN_TIMEOUTS 
    while timeouts_left:
        with socket_lock:
            socket.sendto(encode(Fin()), (config.host, config.port))
        config.logger.log('>>  FIN', config.host, config.port)
        
        try:
            response = queue.get(timeout=timeout)
            if response.type == 'fin':
                config.logger.log("<<  FIN", config.host, config.port)
                break
        except:
            timeouts_left -= 1
            
    if not timeouts_left:        
        config.logger.log(f'FIN implicito', config.host, config.port)
                
    
def fin_receiver(socket, socket_lock, config, queue, timeout):
    timeouts_left = FIN_TIMEOUTS  
    while timeouts_left:        
        try:
            response = queue.get(timeout=timeout)
            if response.type == 'fin':
                config.logger.log("<<  FIN", config.host, config.port)
                with socket_lock:
                    socket.sendto(encode(Fin()), (config.host, config.port))
                config.logger.log('>>  FIN', config.host, config.port)
                
                break
            elif response.type == 'data':
                config.logger.log(f"<<  DATA {response.seq}", config.host, config.port)
                with socket_lock:
                    socket.sendto(encode(Ack(response.seq)), (config.host, config.port))
                config.logger.log(f">>  ACK {response.seq}", config.host, config.port)

        except:
            timeouts_left -= 1
            
    if not timeouts_left:        
        config.logger.log(f'FIN implicito')

