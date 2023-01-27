#!/usr/bin/env python3
from command_pb2 import Head, NStageInfo, JoystickDirectionals, TouchMotion, NEvent, NObject, NVisual, NBody, NClip, NClipType, BodyShape, BodyType, Cmd
import json
import math
from ngin import Nx, EventHandler, NObjectInfo
import struct
import xml.etree.ElementTree as ET

def load_png_file(path_img):
  f = open(path_img, "rb")
  fname = path_img.split('/')[-1]
  img_data = f.read()

  nx.image(fname, img_data)
  width, height = struct.unpack('>ii', img_data[16:24])
  print(width, height)
  return (fname, width, height)

class MyHandler(EventHandler):
  def __init__(self, nx:Nx):
    super().__init__()
    self.nx = nx     
  
  def on_tap(self, tap):
    print(tap.x, tap.y)
    nx.translate(100, tap.x, tap.y, 0.25, 'linear', True)

if __name__ == "__main__":
  nx = Nx('bonsoirdemo')
  #nx.set_event_handler(MyHandler(nx))
  f = open('./data/planes0.tmj', "r")
  j = json.loads(f.read())
  f.close()
  t = j['layers'][0]
  tileSize = j['tilewidth']
  stage = nx.stage_builder(30, 20)
  stage.debug = True
  stage.tap = TouchMotion.ALL
  stage.tapMinMoveDistance = 0.5
  nx.send_stage_info(stage)

  path_ships = 'kenney_pixelshmup/ships_packed.png'

  #nx.send_obj(nx.tiles_builder('kenney_pixelshmup/tiles_packed.png', tileSize, t['width'], t['height'], t['data']))
  #print(r)

  #path_img = './generic-items-160-assets/PNG/Colored/genericItem_color_041.png'
  pngFile = './generic-items-160-assets/Spritesheet/genericItems_spritesheet_colored.png'
  xmlfile = './generic-items-160-assets/Spritesheet/genericItems_spritesheet_colored.xml'
  fname, fwidth, fheight = load_png_file(pngFile)
  tree = ET.parse(xmlfile)  
  root = tree.getroot()

  ind = 91
  print(root[ind].attrib['name'])

  #for x in root:
  #  print(x.attrib)
  #  for y in x.attrib:
  #    print(y, x.attrib[y])

  o = nx.obj_builder(100, "hero")
  #p = nx.body_builder(o, BodyShape.circle, 10, 10)
  #p.angle = 1.5
  s = 4  
  #p.width = s
  #p.height = s
  x = float(root[ind].attrib['x'])
  y = float(root[ind].attrib['y'])
  width = float(root[ind].attrib['width'])
  height = float(root[ind].attrib['height'])

  v = nx.visual_builder(o, [nx.sprite_builder(fname, x, y, width, height)])
  v.x = 10
  v.y = 10
  v.width = s
  v.height = s*height/width
  nx.send_obj(o, True)

  #r = nx.linear_to(100, 15, 15, 20)
  #print(r)
  #nx.translate_to(100, 15, 15, 1, 'easeInOut', True)

  nx.transform(100, {'translate':(15, 15), 'scale':(1.5, 1.5), 'angle':2*math.pi}, 1, 'easeInOut', True)
  nx.transform(100, {'translate':(5, 5), 'scale':(1.5, 1.5), 'angle':0}, 0.5, 'easeInOut', True) 
  nx.translate(100, 15, 15, 1, 'easeInOut', True)

  nx.main_loop(MyHandler(nx))