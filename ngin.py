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
from command_pb2 import Head, NStageInfo, JoystickDirectionals, TouchMotion, NEvent, NObject, NVisual, NBody, NClip, NClipType, BodyShape, BodyType, Cmd
import struct
import json
import math
from collections import deque
import queue

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

class ContactInfo:
  def __init__(self, c):
    self.is_ended = c.ints[1] == 1
    self.info1 = c.strings[0]    
    self.info2 = c.strings[1]
    self.id1 = c.ints[2]    
    self.id2 = c.ints[3]
    self.x = c.floats[0]
    self.y = c.floats[1]
    self.x1 = c.floats[2]
    self.y1 = c.floats[3]
    self.x2 = c.floats[4]
    self.y2 = c.floats[5]
  def __str__(self):
    return "ContactInfo {is_ended} (x:{x}, y:{y}) ({info1}, id:{id1}, x:{x1}, y:{y1}) ({info2}, id:{id2}, x:{x2}, y:{y2})".format(is_ended = 'Ended' if self.is_ended else 'Begun', x=self.x, y=self.y, info1=self.info1, id1=self.id1, x1=self.x1, y1=self.y1, info2=self.info2, id2=self.id2, x2=self.x2, y2=self.y2)
class EventInfo:
  def __init__(self, c):
    self.id = c.ints[2]
    self.info = c.strings[0]
    if self.info == 'distance':
      self.on = c.ints[1] == 1
      self.distance = c.floats[0]
      self.id2 = c.ints[3]
    else:
      self.completed = c.ints[1] == 1      
      self.x = c.floats[0]
      self.y = c.floats[1]

  def __str__(self):
    if self.info == 'distance':
      return "Distance {on} for {id1} and {id2}".format(on = "on" if self.on else "off", id1 = self.id, id2 = self.id2)
    else:   
      return "EventInfo {event} - {completed} for {id1} {info} ({x}, {y})".format(event = self.info, completed = "completed" if self.completed else "not completed", id1 = self.id, info=self.info, x = self.x, y = self.y)

class KeyInfo:
  def __init__(self, c):
    self.name = c.strings[0]
    self.is_pressed = c.ints[1] == 1
  def __str__(self):
    return "KeyInfo is_pressed:{is_pressed} name:{name}".format(is_pressed = self.is_pressed, name=self.name)

class TapInfo:
  def __init__(self, c):
    self.info = c.ints[1]
    self.event = c.ints[2]
    self.x = c.floats[0]
    self.y = -c.floats[1]    
  def __str__(self):
    return "TapInfo info:{info} event:{event} ({x},{y})".format(info = self.info, event=self.event, x=self.x, y=self.y)
  
class ErrorInfo:  
  def __init__(self, c):
    self.name = c.strings[0]
    self.code = c.ints[1]
  def __str__(self):
    return "Error {name} code:{code}".format(name=self.name, code=self.code)


class EventHandler:
  unexpected = 'Unexpected:'
  def __init__(self) -> None:
    self.completed = False

  def handle(self, c):
    head = c.ints[0]
    if head == Head.key:
      self.on_key(KeyInfo(c))
    elif head == Head.contact:
      self.on_contact(ContactInfo(c))
    elif head == Head.event:
      self.on_event(EventInfo(c))
    elif head == Head.directional:
      self.on_directional(c)
    elif head == Head.button:
      self.on_button(c)
    elif head == Head.tap:
      self.on_tap(TapInfo(c))
    elif head == Head.error:
      self.on_error(ErrorInfo(c))
    elif head == Head.relay:
      self.on_relay(c)
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
  def on_error(self, c):
    print(self.unexpected, c)    
  def on_relay(self, c):
    print(self.unexpected, c)       


class EventRunner(threading.Thread):
  def __init__(self, q:queue.Queue, handler:EventHandler):
    super().__init__()
    self.q = q
    self.handler = handler

  def run(self):
    #self.handler.handle(self.event)
    while True:
      data = self.q.get()
      self.handler.handle(data)

class RemoteAction:
  sn = 0
  def __init__(self) -> None:
    #self.id = id
    self.sn = self.get_sn()
    self.lock = threading.Lock()
    self.lock.acquire()

  def acquire(self):
    self.lock.acquire()
  
  def get_sn(self) -> int:
    RemoteAction.sn += 1
    return RemoteAction.sn


class Recv(threading.Thread):
  def __init__(self, socket:socket, q:queue.Queue) -> None:
    super().__init__()
    self.remaining = 0
    self.socket = socket
    self.q = q
    self.remote_actions = set()

  def add_remote_action(self) -> RemoteAction:
    remote_action = RemoteAction()
    self.remote_actions.add(remote_action)
    return remote_action

  def get_remote_action(self, sn:int):
    for remote_action in self.remote_actions:
      if remote_action.sn == sn:
        return remote_action
    return None
 
  def process_remote_action(self, c) -> bool:
    remote_action = self.get_remote_action(c.ints[1])
    if remote_action != None:
      self.remote_actions.discard(remote_action)
      remote_action.value = c
      remote_action.lock.release()
      return True
    return False

  def run(self):
    self.event_loop2()

  def event_loop2(self) -> None:
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

      c = NEvent()      
      c.ParseFromString(data)
      head = c.ints[0]

      if head == Head.ack:
        if not self.process_remote_action(c):
          print(f'Unexpected: Ack - {c}')
      elif head == Head.cmd:
        print(f'Cmd - {c}')
        if not self.process_remote_action(c):
          print(f'Unexpected: Cmd - {c}')
      else:
        self.q.put(c)

class NObjectInfo:
  def __init__(self, info:list[float]):
    self.x, self.y, self.width, self.height, self.angle, self.linearx, self.lineary, self.angular = info


class Ngin:
  def __init__(self, host:str, port:int = 4040, verbose:bool = False):
    self.host = host
    self.port = port

    HOST = host
    if host[3] != '.':
      HOST = self.find_ip(f'_{self.host}._tcp.local.', verbose)  # The server's hostname or IP address
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    self.socket.connect((HOST, self.port))
    self.q = queue.Queue()
    self.recv = Recv(self.socket, self.q)
    self.recv.start()    


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

  def _send(self, head:Head, data):
    bs = data.SerializeToString()
    head_bytes = struct.pack('<L', head)  
    len_bytes = struct.pack('<L', len(bs))
    #print(f'size:4 + {len(bs)}')    
    self.socket.sendall(head_bytes + len_bytes + bs)

  def send(self, head:Head, data, ack:bool = False):
    if (ack):
      remote_action = self.recv.add_remote_action()
      data.sn = remote_action.sn
      print('send ack:{ack}({sn})'.format(ack=ack, sn=data.sn))    
      self._send(head, data)
      remote_action.acquire()
      return remote_action
    else:
      #print('send ack:{ack}'.format(ack=ack))    
      self._send(head, data)

class Nx(Ngin):
  def __init__(self, host:str):
    super().__init__(host)

  def send_obj(self, data, ack:bool = False):
    return self.send(Head.object, data, ack)

  def send_stage_info(self, data):
    return self.send(Head.stage, data, True)

  def stage_builder(self, width:float, height:float) -> NStageInfo:
    c = NStageInfo()
    c.background = ''
    c.gravityX = 0
    c.gravityY = 0
    c.width = width
    c.height = height
    c.debug = False
    c.joystickDirectionals = JoystickDirectionals.none
    c.joystickPrecision = 3
    c.button1 = TouchMotion.DOWN
    c.button2 = TouchMotion.DOWN
    c.tap = TouchMotion.DOWN
    c.tapMinMoveDistance = 0
    c.distanceTrackingInternal = 0
    return c

  def tiles_builder(self, path:str, tile_size:float, width:float, height:float, data:list[int]) -> NObject:
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

  def visual_builder(self, obj:NObject, clips:list[NClip]) -> NVisual:
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

  def main_loop(self, handler:EventHandler):
    while not handler.completed:
      data = self.q.get()
      handler.handle(data)    


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

  def removeAll(self) -> None:
    c = Cmd()
    c.strings.append('removeAll')
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
    remote_action = self.send(Head.cmd, c, True)
    return remote_action.value

  def get_obj_info(self, id:int) -> NObjectInfo:
    info = self._get_obj_info(id)
    return NObjectInfo(info.floats)

  def set_clip_type(self, id:int, clip_type:NClipType, is_flip_horizontal:bool = False) -> None:
    c = Cmd()
    c.strings.append('clipType')
    c.ints.append(id)
    c.ints.append(1 if is_flip_horizontal == True else 0)    
    c.ints.append(clip_type)
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

  def image(self, key:str, bytes:bytes):
    c = Cmd()
    c.strings.append('image')
    c.strings.append(key)
    c.bytes.append(bytes)
    c.ints.append(99999)
    self.send(Head.cmd, c, True, 99999)
    #return self.recv.wait_ack_id(99999)

  def distance_tracking(self, id1:int, id2:int, dist:float):
    c = Cmd()
    c.strings.append('distance')
    c.ints.append(id1)
    c.ints.append(id2)
    c.floats.append(dist)    
    self.send(Head.cmd, c)


  def translate(self, id:int, x:float, y:float, time:float, type:str = 'easeInOut', need_ack:bool=False):
    return self.transform(id, {'translate':(x,y)}, time, type, need_ack)

  def transform(self, id:int, transform:dict, time:float, type:str = 'easeInOut', need_ack:bool=False):
    c = Cmd()
    c.strings.append('transform')
    c.strings.append(type)    
    c.ints.append(id)
    c.ints.append(1 if need_ack else 0)

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

    self.send(Head.cmd, c, need_ack)

  def hint(self, hint:str) -> None:
    c = Cmd()
    c.strings.append('hint')
    c.strings.append(hint)
    self.send(Head.cmd, c)

  def svg(self, id:int, svg:str, x:float, y:float, width:float, height:float, info:str="", ack:bool=False):
    a = NClip()
    a.path = svg
    a.x = 0
    a.y = 0
    a.width = width
    a.height = height
    a.indices.extend([])
    a.stepTime = 0.2
    a.type = NClipType.svg
    a.repeat = True

    c = NObject()
    c.tid = 0
    c.id = id
    c.info = info

    v = c.visual
    v.current = NClipType.svg
    v.priority = 0
    v.x = x
    v.y = y
    v.width = width
    v.height = height
    v.scaleX = 1
    v.scaleY = 1
    v.anchorX = 0
    v.anchorY = 0
    v.clips.extend([a])
    self.send(Head.object, c, ack)


class Nc(Ngin):
  def __init__(self, host:str):
    super().__init__(host, 4041)

  def relay(self, strings:list[str], ints:list[int], floats:list[float]) -> None:
    c = Cmd()
    c.strings.append('relay')
    c.strings.extend(strings)
    c.ints.append(Head.relay)
    c.ints.extend(ints)
    c.floats.extend(floats)
    self.send(Head.cmd, c)
    
