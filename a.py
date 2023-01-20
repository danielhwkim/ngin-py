import random
from command_pb2 import Head, NStageInfo, JoystickDirectionals, TouchMotion, NEvent, NObject, NVisual, NBody, NClip, NClipType, BodyShape, BodyType, Cmd
import json
import math
from ngin import Nx, EventHandler, NObjectInfo, EventInfo, Nc
from threading import Timer

class MyHandler(EventHandler):
  def __init__(self, nc:Nc):
    self.nc = nc     
  

if __name__ == "__main__":
  nc = Nc('bonsoirdemo')
  handler = MyHandler(nc)
  nc.relay(["a"], [7], [0.7])

