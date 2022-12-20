#!/usr/bin/env python3
from command_pb2 import Head, CStageInfo, JoystickDirectionals, ActionEvent, CmdInfo, CObject, CVisible, CPhysical, CAction, CActionType, BodyShape, BodyType, Cmd
import json
import math
from ngin import Nx, EventHandler, CObjectInfo

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

  def getDynamicId(self):
    self.dynamic_id += 1
    return self.dynamic_id

  def missile(self):
    info = self.nx.getObjInfo(100)
    info = CObjectInfo(info.floats)
    new_id = self.getDynamicId()
    o = self.nx.objBuilder(new_id, "missile")

    p = self.nx.physicalBuilder(o, BodyShape.rectangle, info.x-0.5 + 2*math.sin(info.angle), info.y-0.5 - 2*math.cos(info.angle))
    p.angle = info.angle
    v = self.nx.visibleBuilder(o, [nx.actionBuilder('kenney_pixelshmup/tiles_packed.png', 16, [1, 2, 3])])
    self.nx.send(Head.cobject, o, True)
    self.nx.forward(new_id, 0, 20)
    self.nx.timer(new_id, 0.7)

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
      if contact.info2 == 'missile':
        self.nx.remove(contact.id2)

        o = self.nx.objBuilder(self.getDynamicId(), "fire")
        o.tid = contact.id1
        v = self.nx.visibleBuilder(o, [nx.actionBuilder('kenney_pixelshmup/tiles_packed.png', 16, [5])])
        self.nx.send(Head.cobject, o, True)

  def eventHandler(self, c):
    event = c.event
    if event.info == 'missile':
      self.nx.remove(event.id)

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