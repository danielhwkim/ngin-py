#!/usr/bin/env python3
import argparse
import logging
from time import sleep
from typing import cast
#import asyncio
import threading
from zeroconf import IPVersion, ServiceBrowser, ServiceStateChange, Zeroconf, ZeroconfServiceTypes
#import cmd
import socket
from command_pb2 import Head, CStageInfo, JoystickDirectionals, ActionEvent, CmdInfo, CObject, CVisible, CPhysical, CAction, CActionType, BodyShape, BodyType, Cmd
import struct
import json
import math

class ServiceListener:
  def __init__(self, event_result_available, verbose) -> None:
    self.event_result_available = event_result_available
    self.verbose = verbose

  def remove_service(self, zeroconf, type, name) -> None:
    if self.verbose:
      print("Service %s removed" % (name,))

  def add_service(self, zeroconf, type, name) -> None:
    info = zeroconf.get_service_info(type, name)
    if self.verbose:
      print("Service %s added, service info: %s" % (name, info))
    if info:
      #print(f"ip:{info.parsed_scoped_addresses()[0]}:{info.port}")
      #addresses = ["%s:%d" % (addr, cast(int, info.port)) for addr in info.parsed_scoped_addresses()]
      #print("  Addresses: %s" % ", ".join(addresses))
      #print("  Weight: %d, priority: %d" % (info.weight, info.priority))
      #print(f"  Server: {info.server}")
      self.result = info.parsed_scoped_addresses()[0]
      if info.properties:
        if self.verbose:
          print("  Properties are:")
        for key, value in info.properties.items():
            print(f"    {key}: {value}")
      else:
        #print("  No properties")
        pass
      self.event_result_available.set()

  def update_service(self, zeroconf, type, name) -> None:
    #info = zeroconf.get_service_info(type, name)
    #if self.verbose:
    #  print("Service %s updated, service info: %s" % (name, info))
    pass

class EventHandler:
  def handle(self, c):
    match c.head:
      case Head.key:
        self.keyHandler(c)
      case Head.contact:
        self.contactHandler(c)
      case Head.event:
        self.eventHandler(c)
      case Head.directional:
        self.directionalHandler(c)
      case Head.button:
        self.buttonHandler(c)
      case _:
        print('Unexpected:', c)

  def keyHandler(self, c):
    print('Unexpected:', c)     
  def contactHandler(self, c):
    print('Unexpected:', c) 
  def eventHandler(self, c):  
    print('Unexpected:', c)   
  def directionalHandler(self, c):    
    print('Unexpected:', c) 
  def buttonHandler(self, c):
    print('Unexpected:', c) 

class Recv:
  def __init__(self, socket:socket) -> None:
    self.remaining = 0
    self.socket = socket
    self.returnAck = False
    self.returnCmd = False

  def waitAck(self):
    self.returnAck = True
    r = self.eventLoop()
    self.returnAck = False
    return r

  def waitCmd(self):
    self.returnCmd = True
    r = self.eventLoop()
    self.returnCmd = False
    return r   

  def eventLoop(self):
    while True:    
      if self.remaining < 4:
        if self.remaining == 0:
          self.buff = self.socket.recv(1024)
        else:
          self.buff = self.buff[self.index:] + self.socket.recv(1024)
        self.index = 0
        self.remaining = len(self.buff)

      size = int.from_bytes(self.buff[self.index:self.index+4], "little")
      self.index += 4
      self.remaining -= 4

      while self.remaining < size:
        chunk = self.socket.recv(1024)
        self.remaining += len(chunk)
        self.buff += chunk

      data = self.buff[self.index:self.index+size]
      self.index +=size
      self.remaining -= size

      c = CmdInfo()      
      c.ParseFromString(data)
      match c.head:
        case Head.ack:
          c = c.ack
          if self.returnAck:
            #print(f'ACK:{c.code} {c.info}')          
            return c.code
          else:
            print(f'Unexpected: ACK - {c.code} {c.info}')
        case Head.cmd:
          c = c.cmd
          if self.returnCmd:
            #print(f'Cmd:{c}')          
            return c
          else:
            print(f'Unexpected: Cmd - {c}')
        case _:
          self.handler.handle(c)

class CObjectInfo:
  def __init__(self, info:list[float]):
    self.x, self.y, self.width, self.height, self.angle, self.linearx, self.lineary, self.angular = info


class Nx:
  def __init__(self, host:str, port:int, verbose:bool = False):
    self.host = host
    self.port = port

    HOST = host
    if host[3] != '.':
      HOST = self.find_ip(f'_{self.host}._tcp.local.', verbose)  # The server's hostname or IP address
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    self.socket.connect((HOST, self.port))
    self.recv = Recv(self.socket)

  def setEventHandler(self, handler):
    self.recv.handler = handler

  def find_ip(self, type, verbose=False):
      event_result_available = threading.Event()
      zeroconf = Zeroconf()
      listener = ServiceListener(event_result_available, verbose)
      browser = ServiceBrowser(zeroconf, type, listener)
      event_result_available.wait()
      #print(f'ip:{listener.result}')
      #try:
      #    input("Press enter to exit...\n\n")
      #finally:
      #    zeroconf.close()
      zeroconf.close()
      return listener.result

  def send(self, head:Head, data, ack:bool = False):
    bs = data.SerializeToString()
    head_bytes = struct.pack('<L', head)  
    len_bytes = struct.pack('<L', len(bs))
    #print(f'size:4 + {len(bs)}')
    self.socket.sendall(head_bytes + len_bytes + bs)
    if(ack):
      return self.recv.waitAck()

  def stageBuilder(self, width:float, height:float):
    c = CStageInfo()
    c.background = 'Blue'
    c.gravityX = 0
    c.gravityY = 0
    c.width = width
    c.height = height
    c.debug = False
    c.joystickDirectionals = JoystickDirectionals.none
    c.joystickPrecision = 3
    c.button1 = ActionEvent.DOWN
    c.button2 = ActionEvent.DOWN
    return c

  def tilesBuilder(self, path:str, tileSize:float, width:float, height:float, data:list[int]):
    c = CObject()
    c.tid = 0
    v = c.visible       
    #v = CVisible()
    v.current = CActionType.tiles
    v.x = 0
    v.y = 0
    v.width = width
    v.height = height
    v.scaleX = 1
    v.scaleY = 1
    v.anchorX = 0
    v.anchorY = 0
    a = CAction()
    a.path = path
    a.stepTime = 200/1000
    a.tileSizeX = tileSize
    a.tileSizeY = tileSize
    a.indices.extend(data)
    a.repeat = False
    a.type = CActionType.tiles
    v.actions.append(a)
    return c

  def objBuilder(self, id:int, info:str) -> CObject:
    c = CObject()
    c.tid = 0
    c.id = id
    c.info = info
    return c

  def physicalBuilder(self, obj:CObject, shape:BodyShape, x:float, y:float) -> CPhysical:
    p = obj.physical
    p.x = x
    p.y = y
    p.width = 1
    p.height = 1
    p.restitution = 0
    p.friction = 0
    p.density = 0
    p.angle = 0
    p.isSensor = False
    p.categoryBits = 0x0001
    p.maskBits = 0xFFFF
    p.fixedRotation = True
    p.type = BodyType.dynamic
    p.trackable = True
    p.contactReport = True
    p.passableBottom = False
    p.shape = shape
    return p

  def visibleBuilder(self, obj:CObject, actions:list[CAction]):
    v = obj.visible
    v.current = CActionType.idle
    v.priority = 0
    v.x = 0
    v.y = 0
    v.width = 1
    v.height = 1
    v.scaleX = 1
    v.scaleY = 1
    v.anchorX = 0.5
    v.anchorY = 0.5
    v.actions.extend(actions)
    return v

  def actionBuilder(self, path:str, tileSize:float, indices:list[int], type:CActionType = CActionType.idle, repeat:bool=True) -> CAction:
    a = CAction()
    a.path = path
    a.tileSizeX = tileSize
    a.tileSizeY = tileSize
    a.indices.extend(indices)
    a.stepTime = 0.2
    a.type = type
    a.repeat = repeat
    return a

  def mainLoop(self):
    self.recv.eventLoop()


  def follow(self, id:int) -> None:
    c = Cmd()
    c.strings.append('follow')
    c.ints.append(id)
    self.send(Head.cmd, c)

  def remove(self, id:int) -> None:
    c = Cmd()
    c.strings.append('remove')
    c.ints.append(id)
    self.send(Head.cmd, c)

  def angular(self, id:int, value:float) -> None:
    c = Cmd()
    c.strings.append('angular')
    c.ints.append(id)
    c.floats.append(value)
    self.send(Head.cmd, c)

  def submit(self, id:int) -> None:
    c = Cmd()
    c.strings.append('submit')
    c.ints.append(4041)
    self.send(Head.cmd, c)

  def getObjInfo(self, id:int):
    c = Cmd()
    c.strings.append('objinfo')
    c.ints.append(id)
    self.send(Head.cmd, c)
    v = self.recv.waitCmd()
    return v

  def setActionType(self, actionType:CActionType, isFlipHorizontal:bool = False) -> None:
    c = Cmd()
    c.strings.append('actionType')
    c.ints.append(id)
    c.ints.append(1 if isFlipHorizontal == True else 0)    
    c.ints.append(actionType)
    self.send(Head.cmd, c)

  def linearTo(self, id:int, x:float, y:float, speed:float):
    c = Cmd()
    c.strings.append('linearTo')
    c.ints.append(id)
    c.floats.append(x)
    c.floats.append(y)
    c.floats.append(speed)
    self.send(Head.cmd, c)
    v = self.recv.waitCmd()
    return v
    
  def forward(self, id:int, angle:float, speed:float) -> None:
    c = Cmd()
    c.strings.append('forward')
    c.ints.append(id)
    c.floats.append(angle)
    c.floats.append(speed)    
    self.send(Head.cmd, c)

  def linear(self, id:int, x:float, y:float) -> None:
    c = Cmd()
    c.strings.append('lineary')
    c.ints.append(id)
    c.floats.append(x)    
    c.floats.append(y)        
    self.send(Head.cmd, c)

  def force(self, id:int, x:float, y:float) -> None:
    c = Cmd()
    c.strings.append('force')
    c.ints.append(id)
    c.floats.append(x)    
    c.floats.append(y)        
    self.send(Head.cmd, c)

  def impluse(self, id:int, x:float, y:float) -> None:
    c = Cmd()
    c.strings.append('impluse')
    c.ints.append(id)
    c.floats.append(x)    
    c.floats.append(y)        
    self.send(Head.cmd, c)

  def angular(self, id:int, velocity:float) -> None:
    c = Cmd()
    c.strings.append('angular')
    c.ints.append(id)
    c.floats.append(velocity)    
    self.send(Head.cmd, c)

  def torque(self, id:int, torque:float) -> None:
    c = Cmd()
    c.strings.append('torque')
    c.ints.append(id)
    c.floats.append(torque)    
    self.send(Head.cmd, c)

  def linearx(self, id:int, velocity:float) -> None:
    c = Cmd()
    c.strings.append('linearx')
    c.ints.append(id)
    c.floats.append(velocity)    
    self.send(Head.cmd, c)

  def lineary(self, id:int, velocity:float) -> None:
    c = Cmd()
    c.strings.append('lineary')
    c.ints.append(id)
    c.floats.append(velocity)    
    self.send(Head.cmd, c)


  def constx(self, id:int, velocity:float) -> None:
    c = Cmd()
    c.strings.append('constx')
    c.ints.append(id)
    c.floats.append(velocity)    
    self.send(Head.cmd, c)

  def consty(self, id:int, velocity:float) -> None:
    c = Cmd()
    c.strings.append('consty')
    c.ints.append(id)
    c.floats.append(velocity)    
    self.send(Head.cmd, c)

  def timer(self, id:int, time:float) -> None:
    c = Cmd()
    c.strings.append('timer')
    c.ints.append(id)
    c.floats.append(time)
    self.send(Head.cmd, c)    
 


class MyHandler(EventHandler):
  def __init__(self, nx):
    self.nx = nx
    self.nx = nx;        
    self.key_down_left = False
    self.key_down_right = False
    self.actor_contacts = set()
    self.actor_jump_count = 0
    self.dynamic_id = 1000
    self.facingLeft = False  
    self.ready = False          

  def goRight(self):
    self.nx.angular(100, 1)

  def goLeft(self):
    self.nx.angular(100, -1)

  def stop(self):
    self.nx.angular(100, 0)


  def missile(self):
    info = self.nx.getObjInfo(100)
    info = CObjectInfo(info.floats)

    o = self.nx.objBuilder(101, "missile")
    p = self.nx.physicalBuilder(o, BodyShape.rectangle, info.x-0.5 + 2*math.sin(info.angle), info.y-0.5 - 2*math.cos(info.angle))
    p.angle = info.angle
    v = self.nx.visibleBuilder(o, [nx.actionBuilder('kenney_pixelshmup/tiles_packed.png', 16, [1, 2, 3])])
    self.nx.send(Head.cobject, o, True)
    self.nx.forward(101, 0, 20)
    self.nx.timer(101, 1)

  def keyHandler(self, c):
    c = c.key
    if c.isPressed == False:
      match c.name:
        case 'Arrow Left':
          self.key_down_left = False
          if self.key_down_right:
            self.goRight()
          else:
            self.stop()	
        case 'Arrow Right':
          self.key_down_right = False
          if self.key_down_left:
            self.goLeft()
          else:
            self.stop()
    else:
      match c.name:
        case 'Arrow Left':
          self.key_down_left = True         
          self.goLeft()
        case 'Arrow Right':
          self.key_down_right = True            
          self.goRight()
        case 'Arrow Up':	
          self.missile()

  def contactHandler(self, c):
    contact = c.contact
    if contact.isEnded == False:
      if contact.id1 == 101:
        self.nx.remove(contact.id1)

        o = self.nx.objBuilder(1000, "fire")
        o.tid = contact.id2
        v = self.nx.visibleBuilder(o, [nx.actionBuilder('kenney_pixelshmup/tiles_packed.png', 16, [5])])
        self.nx.send(Head.cobject, o, True)

  def eventHandler(self, c):
    print(c)


if __name__ == "__main__":
  nx = Nx('bonsoirdemo', 4040)
  nx.setEventHandler(MyHandler(nx))
  f = open('./data/planes0.tmj', "r")
  j = json.loads(f.read())
  f.close()
  t = j['layers'][0]
  tileSize = j['tilewidth']
  nx.send(Head.stage, nx.stageBuilder(t['width'], t['height']), True)  

  nx.send(Head.cobject, nx.tilesBuilder('kenney_pixelshmup/tiles_packed.png', tileSize, t['width'], t['height'], t['data']))

  o = nx.objBuilder(100, "hero")
  p = nx.physicalBuilder(o, BodyShape.circle, 11, 11)
  p.angle = 1.5
  p.width = 2
  p.height = 2
  v = nx.visibleBuilder(o, [nx.actionBuilder('kenney_pixelshmup/ships_packed.png', 32, [1])])
  v.width = 2
  v.height = 2
  nx.send(Head.cobject, o, True)

  nx.follow(100)
  nx.forward(100, 0, 5)

  o = nx.objBuilder(200, "enemy")
  p = nx.physicalBuilder(o, BodyShape.circle, 11, 0)
  p.width = 2
  p.height = 2
  v = nx.visibleBuilder(o, [nx.actionBuilder('kenney_pixelshmup/ships_packed.png', 32, [10])])
  v.width = 2
  v.height = 2
  nx.send(Head.cobject, o, True)

  nx.forward(200, 0, 5)
  nx.angular(200, 1)

  nx.mainLoop()












