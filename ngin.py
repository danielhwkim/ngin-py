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
  unexpected = 'Unexpected:'
  def handle(self, c):
    match c.head:
      case Head.key:
        self.key_handler(c)
      case Head.contact:
        self.contact_handler(c)
      case Head.event:
        self.event_handler(c)
      case Head.directional:
        self.directional_handler(c)
      case Head.button:
        self.button_handler(c)
      case _:
        print(self.unexpected, c)

  def key_handler(self, c):
    print(self.unexpected, c)     
  def contact_handler(self, c):
    print(self.unexpected, c) 
  def event_handler(self, c):  
    print(self.unexpected, c)   
  def directional_handler(self, c):    
    print(self.unexpected, c) 
  def button_handler(self, c):
    print(self.unexpected, c) 

class Recv:
  def __init__(self, socket:socket) -> None:
    self.remaining = 0
    self.socket = socket
    self.return_ack = False
    self.return_cmd = False

  def wait_ack(self):
    self.return_ack = True
    r = self.event_loop()
    self.return_ack = False
    return r

  def wait_cmd(self):
    self.return_cmd = True
    r = self.event_loop()
    self.return_cmd = False
    return r   

  def event_loop(self):
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
          if self.return_ack:
            #print(f'ACK:{c.code} {c.info}')          
            return c.code
          else:
            print(f'Unexpected: ACK - {c.code} {c.info}')
        case Head.cmd:
          c = c.cmd
          if self.return_cmd:
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

  def set_event_handler(self, handler):
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
      return self.recv.wait_ack()

  def stage_builder(self, width:float, height:float):
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

  def tiles_builder(self, path:str, tile_size:float, width:float, height:float, data:list[int]):
    c = CObject()
    c.tid = 0
    v = c.visible       
    #v = CVisible()
    v.current = CActionType.tiles
    v.priority = 0
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
    a.tileSizeX = tile_size
    a.tileSizeY = tile_size
    a.indices.extend(data)
    a.repeat = False
    a.type = CActionType.tiles
    v.actions.append(a)
    return c

  def obj_builder(self, id:int, info:str) -> CObject:
    c = CObject()
    c.tid = 0
    c.id = id
    c.info = info
    return c

  def physical_builder(self, obj:CObject, shape:BodyShape, x:float, y:float) -> CPhysical:
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

  def visible_builder(self, obj:CObject, actions:list[CAction]):
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

  def action_builder(self, path:str, tile_size:float, indices:list[int], type:CActionType = CActionType.idle, repeat:bool=True) -> CAction:
    a = CAction()
    a.path = path
    a.tileSizeX = tile_size
    a.tileSizeY = tile_size
    a.indices.extend(indices)
    a.stepTime = 0.2
    a.type = type
    a.repeat = repeat
    return a

  def main_loop(self):
    self.recv.event_loop()


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

  def submit(self, id:int) -> None:
    c = Cmd()
    c.strings.append('submit')
    c.ints.append(id)    
    c.ints.append(4041)
    self.send(Head.cmd, c)

  def get_obj_info(self, id:int):
    c = Cmd()
    c.strings.append('objinfo')
    c.ints.append(id)
    self.send(Head.cmd, c)
    v = self.recv.wait_cmd()
    return v

  def set_action_type(self, id:int, action_type:CActionType, is_flip_horizontal:bool = False) -> None:
    c = Cmd()
    c.strings.append('actionType')
    c.ints.append(id)
    c.ints.append(1 if is_flip_horizontal == True else 0)    
    c.ints.append(action_type)
    self.send(Head.cmd, c)

  def linear_to(self, id:int, x:float, y:float, speed:float):
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
