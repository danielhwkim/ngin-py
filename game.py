#!/usr/bin/env python3
from command_pb2 import Head, NStageInfo, JoystickDirectionals, TouchMotion, NEvent, NObject, NVisual, NBody, NClip, NClipType, BodyShape, BodyType, Cmd
import json
import math
from ngin import Nx, EventHandler, NObjectInfo

def conv(v, tileSize):
  return round(v*2.0/tileSize)/2.0

def conv_info(info, tile_size):
  info['x'] = conv(info['x'], tile_size)
  info['y'] = conv(info['y'], tile_size)
  info['width'] = conv(info['width'], tile_size)
  info['height'] = conv(info['height'], tile_size)
  return info


class MyHandler(EventHandler):
  def __init__(self, nx:Nx):
    super().__init__()
    self.nx = nx
    self.key_down_left = False
    self.key_down_right = False
    self.hero_contacts = set()
    self.hero_jump_count = 0
    self.dynamic_id = 1000
    self.facingLeft = False  
    self.ready = False
    self.heroId = 100

  def on_contact(self, contact):
    print(contact)
    #if contact.is_ended == False and contact.info2 == 'missile':
    if contact.info1 == 'hero':
      if contact.info2 in ['floor', 'bar']:
        if contact.is_ended == False:
          if contact.y < 0:
            if len(self.hero_contacts) == 0:
              if self.key_down_left or self.key_down_right:
                self.nx.set_clip_type(contact.id1, NClipType.run, self.facingLeft)
              else:
                self.nx.set_clip_type(contact.id1, NClipType.idle, self.facingLeft)         
              self.hero_jump_count = 0                
            self.hero_contacts.add(contact.id2)
        else:
          if (contact.id2 in self.hero_contacts):
            self.hero_contacts.remove(contact.id2)
      elif contact.info2 == 'fruit':
        if contact.is_ended == False:
          self.nx.set_clip_type(contact.id2, NClipType.hit, self.facingLeft)
      elif contact.info2 == 'box':
        if contact.is_ended == False:
          #print(contact.x, contact.y)
          if (math.abs(contact.y) > math.abs(contact.x)):
            obj = self.objs[contact.id2]
            obj.count += 1
            self.nx.set_clip_type(contact.id2, NClipType.hit, self.facingLeft)
          if (contact.y < 0):
            self.hero_jump_count = 0
            self.nx.lineary(contact.id1, -20)
      elif contact.info2 == 'Trampoline':
        if contact.is_ended == False:
          self.nx.set_clip_type(contact.id2, NClipType.hit, self.facingLeft)
          self.nx.lineary(contact.id1, -30)
          self.hero_jump_count = 0

  def on_key(self, key):
    if key.is_pressed == False:
      if key.name == 'Arrow Left':
        self.key_down_left = False
        if self.key_down_right:
          self.facingLeft = False
          self.nx.constx(self.heroId, 7)
          if len(self.hero_contacts) != 0:
            self.nx.set_clip_type(self.heroId, NClipType.run, self.facingLeft)                    
          else:
            self.nx.set_clip_type(self.heroId, NClipType.noChange, self.facingLeft)
        else:
          self.nx.constx(self.heroId, 0)
          if len(self.hero_contacts) != 0:
            self.nx.set_clip_type(self.heroId, NClipType.idle, self.facingLeft)                  
          else:
            self.nx.set_clip_type(self.heroId, NClipType.noChange, self.facingLeft)
      elif key.name == 'Arrow Right':
        self.key_down_right = False
        if self.key_down_left:
            self.facingLeft = True
            self.nx.constx(self.heroId, -7)
            if len(self.hero_contacts) != 0: 
              self.nx.set_clip_type(self.heroId, NClipType.run, self.facingLeft)     
            else:
              self.nx.set_clip_type(self.heroId, NClipType.noChange, self.facingLeft)      
            
        else:
          self.nx.constx(self.heroId, 0)
          if len(self.hero_contacts) != 0:					
            self.nx.set_clip_type(self.heroId, NClipType.idle, self.facingLeft)                               
          else:
            self.nx.set_clip_type(self.heroId, NClipType.noChange, self.facingLeft)
    else:
      if key.name == 'Arrow Left':
        if not self.key_down_left:
          self.key_down_left = True
          self.facingLeft = True
          self.nx.constx(self.heroId, -7)
          if len(self.hero_contacts) != 0: 
            self.nx.set_clip_type(self.heroId, NClipType.run, self.facingLeft)                          
          else:
            self.nx.set_clip_type(self.heroId, NClipType.noChange, self.facingLeft) 
        else:
          self.nx.set_clip_type(self.heroId, NClipType.noChange, self.facingLeft)                      
            
      elif key.name == 'Arrow Right':
        if not self.key_down_right:
          self.key_down_right = True
          self.facingLeft = False
          self.nx.constx(self.heroId, 7)
          if len(self.hero_contacts) != 0: 		
            self.nx.set_clip_type(self.heroId, NClipType.run, self.facingLeft)                            				
          else:
            self.nx.set_clip_type(self.heroId, NClipType.noChange, self.facingLeft)  
        else:
          self.nx.set_clip_type(self.heroId, NClipType.noChange, self.facingLeft)                      
      elif key.name == 'Arrow Up':	
        if len(self.hero_contacts) != 0: 
          self.nx.lineary(self.heroId, -20)
          self.nx.set_clip_type(self.heroId, NClipType.jump, self.facingLeft)                          
          self.hero_jump_count = 0
        
        elif self.hero_jump_count < 1:
          self.nx.lineary(self.heroId, -20)
          self.nx.set_clip_type(self.heroId, NClipType.doubleJump, self.facingLeft)                  
          self.hero_jump_count = 1   
  def on_event(self, event):
    if event.completed == False:
      return
    if event.info == 'Trampoline':
          self.nx.set_clip_type(event.id, NClipType.idle)
    elif event.info == 'fruit':
          self.nx.remove(event.id)
    elif event.info == 'hero':
          self.nx.set_clip_type(event.id, NClipType.jump, self.facingLeft)
        
    '''
    if event.info == 'box':
          obj = self.objs[event.id]
          print(obj)
          
          if (obj.count == 2):
            for (var i = 0 i < 4 i++):
              var cobj = new CObject(self.dynamic_id++)
              cobj.info = "parts"
              cobj.physical = new CPhysical(CBodyShape.circle, new CVec2(event.x - 0.5 +0.1*i, event.y - 0.5), CBodyType.dynamic)
              cobj.physical.categoryBits = 0x0100
              cobj.physical.maskBits = 0x0FFF
              cobj.physical.size = new CSize(0.5, 0.5)
              #cobj.physical.density = 1.0
              cobj.physical.contactReport = False
              cobj.visible = new CVisible([
                new CAction('Items/Boxes/' + obj.name + '/Break.png', new CSize(28, 24), [i], CActionType.idle),
              ])
              cobj.visible.scale = new CVec2(28 / 16, 24 / 16)
              self.nx.sendObj(cobj)
            

            #self.nginx.opAction(c.id, c.x, c.y)
            self.nx.remove(event.id)
            var cobj = addFruit(self.dynamic_id++, new CVec2(event.x - 0.5, event.y - 0.5), 'Bananas')
            #cobj.physical.type = CBodyType.dynamic
            self.nx.sendObj(cobj)
           else:
            self.nx.setActionType(event.id, CActionType.idle)
      '''    

if __name__ == "__main__":
  nx = Nx('bonsoirdemo')
  f = open('./data/level03.json', "r")
  j = json.loads(f.read())
  f.close()
  tiles = j['layers'][0]
  objlayer = j['layers'][1]  
  data = tiles['data']
  tile_size = j['tilewidth']
  #precision = 3
  stage = nx.stage_builder(tiles['width'], tiles['height'])
  #stage.debug = True
  stage.background = 'Blue'
  stage.gravityX = 0
  stage.gravityY = 60
  stage.joystickDirectionals = JoystickDirectionals.horizontal
  nx.send(Head.stage, stage, True)
  nx.send_obj( nx.tiles_builder('Terrain/Terrain (16x16).png', tile_size, tiles['width'], tiles['height'], tiles['data']))
  objs = objlayer['objects']

  for obj in objs:
    obj['id'] += 100
    conv_info(obj, tile_size)
    id = obj['id']
    x = obj['x']
    y = obj['y']
    name = obj['name']
    width = obj['width']
    height = obj['height']
    print(name, id)

    if name in ['Apple', 'Bananas', 'Cherries', 'Kiwi', 'Orange', 'Pineapple', 'Strawberry']:
      o = nx.obj_builder(id, "fruit")
      p = nx.body_builder(o, BodyShape.circle, x, y)
      p.type = BodyType.staticBody
      p.isSensor = True
      clips = [nx.clip_builder('Items/Fruits/' + name + '.png', 32, 32, []), 
              nx.clip_builder('Items/Fruits/Collected.png', 32, 32, [], NClipType.hit, False)]
      clips[0].stepTime = 0.05
      clips[1].stepTime = 0.05
      v = nx.visual_builder(o, clips)
      v.scaleX = 1.5
      v.scaleY = 1.5
      nx.send_obj(o)
    elif name == 'hero':
      obj['id'] = 100
      id = 100
      width = 2
      height = 2
      character = 'Mask Dude'

      o = nx.obj_builder(id, name)
      p = nx.body_builder(o, BodyShape.polygon, x, y)
      p.width = width
      p.height = height
      
      hx = width/4
      hy = height/2
      d = hx/4      
      p.floats.extend([-hx, -hy + d, 
                       -hx + d, -hy,
                       hx -d, -hy,
                       hx, -hy +d, 
                       hx, hy-d-d,
                       hx -d, hy-d,
                       -hx+d, hy-d,
                       -hx, hy-d-d])

      p.type = BodyType.dynamicBody

      clips = [
        nx.clip_builder('Main Characters/' + character +'/Idle (32x32).png', 32, 32, [], NClipType.idle), 
        nx.clip_builder('Main Characters/' + character +'/Run (32x32).png', 32, 32, [], NClipType.run),
        nx.clip_builder('Main Characters/' + character +'/Jump (32x32).png', 32, 32, [], NClipType.jump),
        nx.clip_builder('Main Characters/' + character +'/Hit (32x32).png', 32, 32, [], NClipType.hit, False),
        nx.clip_builder('Main Characters/' + character +'/Fall (32x32).png', 32, 32, [], NClipType.fall),
        nx.clip_builder('Main Characters/' + character +'/Wall Jump (32x32).png', 32, 32, [], NClipType.wallJump, False),
        nx.clip_builder('Main Characters/' + character +'/Double Jump (32x32).png', 32, 32, [], NClipType.doubleJump, False),
        ]
      for clip in clips:
        clip.stepTime = 0.05
      v = nx.visual_builder(o, clips)
      v.width = width
      v.height = height
      v.y = -0.13
      nx.send_obj(o)
    elif name == 'floor':
      o = nx.obj_builder(id, name)
      p = nx.body_builder(o, BodyShape.rectangle, x, y)
      p.type = BodyType.staticBody
      p.width = width
      p.height = height
      nx.send_obj(o)
    elif name == 'Trampoline':
      o = nx.obj_builder(id, name)
      p = nx.body_builder(o, BodyShape.rectangle, x, y)
      p.type = BodyType.staticBody
      p.isSensor = True
      clips = [nx.clip_builder('Traps/Trampoline/Idle.png', 28, 28, []), 
              nx.clip_builder('Traps/Trampoline/Jump (28x28).png', 28, 28, [], NClipType.hit, False)]
      clips[0].stepTime = 0.05
      clips[1].stepTime = 0.05
      v = nx.visual_builder(o, clips)
      v.width = 1.7
      v.height = 1.7
      v.y = -0.4
      nx.send_obj(o)
  nx.main_loop(MyHandler(nx))


  
'''
    handleDirectional(directional):
      print(directional)
      c = directional
      switch(c.direction):
        'IDLE':
          self.nx.setActionType(self.heroId, CActionType.idle, self.facingLeft)
          self.nx.constx(self.heroId, 0)
          self.key_down_right = False
          self.key_down_left = False
          break
        'MOVE_RIGHT':
          self.facingLeft = False
          self.nx.setActionType(self.heroId, CActionType.run, self.facingLeft)
          self.nx.constx(self.heroId, 7*c.intensity/self.nx.precision)
          self.key_down_right = True
          self.key_down_left = True
          break
        'MOVE_LEFT':
          self.facingLeft = True
          self.nx.setActionType(self.heroId, CActionType.run, self.facingLeft)
          self.nx.constx(self.heroId, -7*c.intensity/self.nx.precision)            
          self.key_down_right = True
          self.key_down_left = True	  
          break
      
      print(c.direction)
    
  
    handleButton(button):
      print(button)
      if (self.hero_contacts.size != 0): 
        self.nx.lineary(self.heroId, -20)
        self.nx.setActionType(self.heroId, CActionType.jump, self.facingLeft)
        self.hero_jump_count = 0
       else if (self.hero_jump_count < 1):
        self.nx.lineary(self.heroId, -20)
        self.nx.setActionType(self.heroId, CActionType.doubleJump, self.facingLeft)        
        self.hero_jump_count = 1
      
      
'''

'''
        'bar':
          var cobj = new CObject(obj.id)
          cobj.info = obj.name
          cobj.physical = new CPhysical(CBodyShape.rectangle, new CVec2(obj.x, obj.y), CBodyType.static)
          cobj.physical.size = new CSize(obj.width,obj.height)
          cobj.physical.passableBottom = True
          nx.sendObj(cobj)            
          break

        'Box1':
        'Box2':
        'Box3':
          var cobj = new CObject(obj.id)
          cobj.info = 'box'
          cobj.physical = new CPhysical(CBodyShape.rectangle, new CVec2(obj.x, obj.y), CBodyType.static)
          cobj.physical.size = new CSize(obj.width,obj.height)
          cobj.visible = new CVisible([
            new CAction('Items/Boxes/' + obj.name + '/Idle.png', new CSize(28, 24), [], CActionType.idle),
            new CAction('Items/Boxes/' + obj.name + '/Hit (28x24).png', new CSize(28, 24), [], CActionType.hit, False),
          ])
          cobj.visible.scale = new CVec2(28 / 18, 24 / 18)
          for (var i=0 i<cobj.visible.actions.length i++):
            cobj.visible.actions[i].stepTime = 50/1000
                      
          nx.eventHandler.objs[obj.id] =:name:obj.name, count:0
          nx.sendObj(cobj) 
          break
'''