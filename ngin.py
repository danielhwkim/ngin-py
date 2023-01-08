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
from command_pb2 import Head, CStageInfo, JoystickDirectionals, ActionEvent, CmdInfo, NObject, NVisual, NBody, NClip, NClipType, BodyShape, BodyType, Cmd
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
    if c.head == Head.key:
      self.on_key(c.key)
    elif c.head == Head.contact:
      self.on_contact(c.contact)
    elif c.head == Head.event:
      self.on_event(c.event)
    elif c.head == Head.directional:
      self.on_directional(c.directional)
    elif c.head == Head.button:
      self.on_button(c.button)
    elif c.head == Head.tap:
      c.tap.y = -c.tap.y
      self.on_tap(c.tap)
    else:
      print(self.unexpected, c)

  def on_key(self, c):
    print(self.unexpected, c)     
  def on_contact(self, c):
    print(self.unexpected, c) 
  def on_event(self, c):  
    print(self.unexpected, c)   
  def on_directional(self, c):    
    print(self.unexpected, c) 
  def on_button(self, c):
    print(self.unexpected, c) 
  def on_tap(self, c):
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

  def wait_ack_id(self, id):
    self.return_ack = True
    while True:
      r = self.event_loop()
      if r == id:
        break;
      print('Unexpected Ack:', r)
    self.return_ack = False
    return r    

  def wait_cmd(self):
    self.return_cmd = True
    r = self.event_loop()
    self.return_cmd = False
    return r   

  def event_loop(self) -> None:
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
      if c.head == Head.ack:
        c = c.ack
        if self.return_ack:
          #print(f'ACK:{c.code} {c.info}')          
          return c.code
        else:
          print(f'Unexpected: ACK - {c.code} {c.info}')
      elif c.head == Head.cmd:
        c = c.cmd
        if self.return_cmd:
          #print(f'Cmd:{c}')          
          return c
        else:
          print(f'Unexpected: Cmd - {c}')
      else:
        self.handler.handle(c)

class NObjectInfo:
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

  def send_obj(self, data, ack:bool = False):
    bs = data.SerializeToString()
    head_bytes = struct.pack('<L', Head.object)  
    len_bytes = struct.pack('<L', len(bs))
    #print(f'size:4 + {len(bs)}')
    self.socket.sendall(head_bytes + len_bytes + bs)
    if(ack):
      return self.recv.wait_ack_id(data.id)      

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
    c = NObject()
    c.tid = 0
    v = c.visual       
    #v = NVisual()
    v.current = NClipType.tiles
    v.priority = 0
    v.x = 0
    v.y = 0
    v.width = width
    v.height = height
    v.scaleX = 1
    v.scaleY = 1
    v.anchorX = 0
    v.anchorY = 0
    a = NClip()
    a.path = path
    a.stepTime = 200/1000
    a.x = 0
    a.y = 0
    a.width = tile_size
    a.height = tile_size
    a.indices.extend(data)
    a.repeat = False
    a.type = NClipType.tiles
    v.clips.append(a)
    return c

  def obj_builder(self, id:int, info:str) -> NObject:
    c = NObject()
    c.tid = 0
    c.id = id
    c.info = info
    return c

  def body_builder(self, obj:NObject, shape:BodyShape, x:float, y:float) -> NBody:
    p = obj.body
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
    p.type = BodyType.dynamicBody
    p.trackable = True
    p.contactReport = True
    p.passableBottom = False
    p.shape = shape
    return p

  def visual_builder(self, obj:NObject, clips:list[NClip]):
    v = obj.visual
    v.current = NClipType.idle
    v.priority = 0
    v.x = 0
    v.y = 0
    v.width = 1
    v.height = 1
    v.scaleX = 1
    v.scaleY = 1
    v.anchorX = 0.5
    v.anchorY = 0.5
    v.clips.extend(clips)
    return v

  def clip_builder(self, path:str, width:float, height:float, indices:list[int], type:NClipType = NClipType.idle, repeat:bool=True) -> NClip:
    a = NClip()
    a.path = path
    a.x = 0
    a.y = 0
    a.width = width
    a.height = height
    a.indices.extend(indices)
    a.stepTime = 0.2
    a.type = type
    a.repeat = repeat
    return a

  def sprite_builder(self, path:str, x:float, y:float, width:float, height:float) -> NClip:
    a = self.clip_builder(path, width, height, [0])
    a.x = x
    a.y = y
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

  def _get_obj_info(self, id:int):
    c = Cmd()
    c.strings.append('objinfo')
    c.ints.append(id)
    self.send(Head.cmd, c)
    v = self.recv.wait_cmd()
    return v

  def get_obj_info(self, id:int) -> NObjectInfo:
    info = self._get_obj_info(id)
    return NObjectInfo(info.floats)

  def set_action_type(self, id:int, action_type:NClipType, is_flip_horizontal:bool = False) -> None:
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
    v = self.recv.wait_cmd()
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

  def audio_play(self, asset:str, volume:float = 1) -> None:
    c = Cmd()
    c.strings.append('audio')
    c.strings.append('play')    
    c.strings.append(asset)       
    c.floats.append(volume)
    self.send(Head.cmd, c)    

  def audio_create_pool(self, asset:str, max_playsers:int) -> None:
    c = Cmd()
    c.strings.append('audio')
    c.strings.append('pool')    
    c.strings.append(asset)       
    c.ints.append(max_playsers)
    self.send(Head.cmd, c)    

  def audio_loop(self, asset:str, volume:float = 1) -> None:
    c = Cmd()
    c.strings.append('audio')
    c.strings.append('loop')    
    c.strings.append(asset)       
    c.floats.append(volume)
    self.send(Head.cmd, c)

  def bgm_play(self, asset:str, volume:float = 1) -> None:
    c = Cmd()
    c.strings.append('bgm')
    c.strings.append('play')    
    c.strings.append(asset)       
    c.floats.append(volume)
    self.send(Head.cmd, c)    

  def bgm_stop(self) -> None:
    c = Cmd()
    c.strings.append('bgm')
    c.strings.append('stop')    
    self.send(Head.cmd, c)    

  def bgm_pause(self) -> None:
    c = Cmd()
    c.strings.append('bgm')
    c.strings.append('pause')    
    self.send(Head.cmd, c)   

  def bgm_resume(self) -> None:
    c = Cmd()
    c.strings.append('bgm')
    c.strings.append('resume')    
    self.send(Head.cmd, c)   

  def bgm_volume(self, volume:float) -> None:
    c = Cmd()
    c.strings.append('bgm')
    c.strings.append('volume')
    c.floats.append(volume)
    self.send(Head.cmd, c)

  def audio_cache_load(self, assets:list[str]) -> None:
    c = Cmd()
    c.strings.append('audioCache')
    c.strings.append('load')    
    c.strings.expend(assets)
    self.send(Head.cmd, c)

  def audio_cache_clear(self, assets:list[str]) -> None:
    c = Cmd()
    c.strings.append('audioCache')
    c.strings.append('clear')
    c.strings.append(assets)    
    self.send(Head.cmd, c)

  def audio_cache_clear_all(self) -> None:
    c = Cmd()
    c.strings.append('audioCache')
    c.strings.append('clear')
    self.send(Head.cmd, c)    

  def image(self, key, bytes):
    c = Cmd()
    c.strings.append('image')
    c.strings.append(key)
    c.bytes.append(bytes)
    c.ints.append(99999)
    self.send(Head.cmd, c)
    return self.recv.wait_ack_id(99999)

  def translate(self, id:int, x:float, y:float, time:float, type:str = 'easeInOut', ack:bool=False):
    return self.transform(id, {'translate':(x,y)}, time, type, ack)

  def transform(self, id:int, transform:dict, time:float, type:str = 'easeInOut', ack:bool=False):
    c = Cmd()
    c.strings.append('transform')
    c.strings.append(type)    
    c.ints.append(id)
    c.ints.append(1 if ack else 0)

    c.floats.append(time)  

    if 'translate' in transform.keys():
      c.ints.append(1)
      t = transform['translate']
      c.floats.append(t[0])
      c.floats.append(t[1])      
    else:
      c.ints.append(0)
      c.floats.append(0)
      c.floats.append(0)

    if 'scale' in transform.keys():
      c.ints.append(1)
      s = transform['scale']
      c.floats.append(s[0])
      c.floats.append(s[1])           
    else:
      c.ints.append(0)
      c.floats.append(0)
      c.floats.append(0)

    if 'angle' in transform.keys():
      c.ints.append(1)
      a = transform['angle']
      c.floats.append(a)        
    else:
      c.ints.append(0)
      c.floats.append(0)         

    self.send(Head.cmd, c)
    if ack:
      return self.recv.wait_ack_id(id)      