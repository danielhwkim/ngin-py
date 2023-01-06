#!/usr/bin/env python3
from command_pb2 import Head, CStageInfo, JoystickDirectionals, ActionEvent, CmdInfo, CObject, CVisible, CPhysical, CAction, CActionType, BodyShape, BodyType, Cmd
import json
import math
from ngin import Nx, EventHandler, CObjectInfo
import struct


if __name__ == "__main__":
  nx = Nx('bonsoirdemo', 4040)
  nx.set_event_handler(EventHandler())
  f = open('./data/planes0.tmj', "r")
  j = json.loads(f.read())
  f.close()
  t = j['layers'][0]
  tileSize = j['tilewidth']
  stage = nx.stage_builder(70, 40)
  stage.debug = True
  nx.send(Head.stage, stage, True)  

  path_ships = 'kenney_pixelshmup/ships_packed.png'

  nx.send(Head.cobject, nx.tiles_builder('kenney_pixelshmup/tiles_packed.png', tileSize, t['width'], t['height'], t['data']))

  path_img = './generic-items-160-assets/PNG/Colored/genericItem_color_050.png'
  f = open(path_img, "rb")
  #f.read()
  #path_ships = 'image-genericItem_color_152.png'
  fname = path_img.split('/')[-1]
  img_data = f.read()

  nx.image(fname, img_data)
  width, height = struct.unpack('>ii', img_data[16:24])
  print(width, height)

  o = nx.obj_builder(100, "hero")
  p = nx.physical_builder(o, BodyShape.circle, 60, 30)
  #p.angle = 1.5
  p.width = 4
  p.height = 4
  v = nx.visible_builder(o, [nx.action_builder(fname, width, height, [0])])

  s = 4
  v.width = s
  v.height = s*height/width
  nx.send(Head.cobject, o, True)


  nx.main_loop()