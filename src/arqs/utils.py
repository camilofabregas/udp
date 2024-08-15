from src.arqs.selective_repeat import SelectiveRepeatReceiver, SelectiveRepeatSender
from .stop_n_wait import StopNWaitSender, StopNWaitReceiver


arq_by_side = {
   "stop&wait": {
      "sender": StopNWaitSender, 
      "receiver": StopNWaitReceiver
   } ,

   "selectiveRepeat": {
      "sender": SelectiveRepeatSender, 
      "receiver": SelectiveRepeatReceiver
   } 
}