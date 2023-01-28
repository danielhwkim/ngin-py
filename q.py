import random
from command_pb2 import Head, NStageInfo, JoystickDirectionals, TouchMotion, NEvent, NObject, NVisual, NBody, NClip, NClipType, BodyShape, BodyType, Cmd
import json
import math
from ngin import Nx, EventHandler, NObjectInfo, EventInfo
from threading import Timer
import threading
import time

hint = "\
### Python\n\
\n\
'''python\n\
run((cmd) =>  {\n\
    for (i=0 i<12 i++) {\n\
        for (j=0 j<12 j++) {\n\
            if (😄) {\n\
                cmd.add(i, j)\n\
            }\n\
        }\n\
    }\n\
    cmd.submit()\n\
})\n\
'''\n\
\n\
### Comparison Operators\n\
\n\
| Operator | Meaning                  |\n\
| -------- | ------------------------ |\n\
| '=='     | Equal to                 |\n\
| '!='     | Not equal to             |\n\
| '<'      | Less than                |\n\
| '>'      | Greater Than             |\n\
| '<='     | Less than or Equal to    |\n\
| '>='     | Greater than or Equal to |\n\
\n\
### math Operators\n\
\n\
From **Highest** to **Lowest** precedence:\n\
\n\
| Operators | Operation        | Example         |\n\
| --------- | ---------------- | --------------- |\n\
| **        | Exponent         | '2 ** 3 = 8'    |\n\
| %         | Modulus/Remainder | '22 % 8 = 6'    |\n\
| //        | Integer division | '22 // 8 = 2'   |\n\
| /         | Division         | '22 / 8 = 2.75' |\n\
| *         | Multiplication   | '3 * 3 = 9'     |\n\
| -         | Subtraction      | '5 - 2 = 3'     |\n\
| +         | Addition         | '2 + 2 = 4'     |\n\
\n\
"


class Stopwatch(threading.Thread):
  def __init__(self, nx, oid, rect):
    super().__init__()
    self.nx = nx
    self.rect = rect
    self.w = rect[2]
    self.h = rect[3]
    self.oid = oid
    self.num = 0
    self.running = False
    
  def run(self):
    self.running = True
    self.nx.svg(self.oid, draw_svg_text(self.w, self.h, '{num}'.format(num=self.num)), self.rect[0], self.rect[1], self.rect[2], self.rect[3])
    while self.running:
      time.sleep(1)
      self.nx.remove(self.oid)
      self.num += 1
      self.nx.svg(self.oid, draw_svg_text(self.w, self.h, '{num}'.format(num=self.num)), self.rect[0], self.rect[1], self.rect[2], self.rect[3])

  def stop(self):
    self.running = False
    self.nx.remove(self.oid)
    return self.num
class CountDown(threading.Thread):
  def __init__(self, nx, width, height, num, time) -> None:
    self.nx = nx
    print(width, height)
    self.fillopacity = 0.5
    self.textsize = 5
    self.width = width
    self.height = height
    self.info = 'CountDown'
    self.num = num
    self.time = time    

  def run(self):
    num = self.num
    self.nx.svg(100+num, draw_svg_text_full_screen(self.width, self.height, "{num}".format(num=num), self.textsize, self.fillopacity), 0, 0, self.width, self.height, self.info)
    while num > 0:
      self.nx.translate(100+num, self.width, 0, self.time, "easeInOut")
      num -= 1
      self.nx.svg(100+num, draw_svg_text_full_screen(self.width, self.height, "{num}".format(num=num), self.textsize, self.fillopacity), -self.width, 0, self.width, self.height, self.info)
      self.nx.translate(100+num, 0, 0, self.time, "easeInOut", True) 
      self.nx.remove(100+num+1) 
    self.nx.translate(100+num, self.width, 0, self.time, "easeInOut", True)
    self.nx.remove(100+num)     


def draw_svg_grid(x, y, func):
  unit = 100
  ori = '<svg viewBox="0 0 {x} {y}">\n'.format(x=unit*x, y=unit*y)
  padding = 5
  for i in range(x):
    for j in range(y):
      if func(i,j):
        ori += '<rect x="{x}" y="{y}" width="{width}" height="{height}" stroke="#777" fill="none" stroke-width="4"/>\n'.format(x=padding + unit*i, y=padding + unit*j, width=unit - padding*2, height=unit - padding*2)
        ori += '<text fill="#777" x="{x}" y="{y}" font-size="{size}" font-family="Roboto" text-anchor="middle" >{i}:{j}</text>\n'.format(x=unit/2 + unit*i, y=unit*0.6 + unit*j, size=unit/3, i=i,j=j)
      else:
        ori += '<rect x="{x}" y="{y}" width="{width}" height="{height}" stroke="#777" fill="#777" stroke-width="4"/>\n'.format(x=padding + unit*i, y=padding + unit*j, width=unit - padding*2, height=unit - padding*2)
  ori += '</svg>'
  return ori

def draw_svg_text_full_screen(x, y, text, size=1, fill="#111", fillopacity=1):
  unit = 100
  padding = 5  
  ori = '<svg viewBox="0 0 {x} {y}">\n'.format(x=x*unit, y=y*unit)
  #ori += '<rect x="{x}" y="{y}" width="{width}" height="{height}" stroke="#777" fill="#777" stroke-width="4"/>\n'.format(x=padding, y=padding, width=x*unit - padding*2, height=y*unit - padding*2)
  ori += '<text fill="{fill}" fill-opacity="{fillopacity}" x="{x}" y="{y}" font-size="{size}" font-family="Roboto" text-anchor="middle">{text}</text>\n'.format(fill=fill, fillopacity=fillopacity, x=x*unit/2, y=y*unit*0.65, size=unit*size,text=text)
  ori += '</svg>'
  return ori

def draw_svg_text(x, y, text):
    unit = 100    
    ori = '<svg viewBox="0 0 {x} {y}">\n'.format(x=x*unit, y=y*unit)
    #ori += '<rect x="{x}" y="{y}" width="{width}" height="{height}" style="fill:rgb(0,0,255);stroke-width:3;stroke:rgb(0,0,0)"/>\n'.format(x=0, y=0, width=x*unit, height=y*unit)      
    ori += '<text fill="#888" x="{x}" y="{y}" font-size="{unit}" font-family="Roboto" text-anchor="middle">{text}</text>\n'.format(x=unit*x/2, y=unit*0.9, unit=unit, text=text)
    ori += '</svg>'
    return ori

def test01(nx, width, height, margin, func):
  aset = set()
  nothing_to_delete = 0

  for i in range(width):
    for j in range(height):
      if func(i,j):
        aset.add(i*100+j)
  nx.svg(100, draw_svg_grid(width, height, func), 0, 0, width, height)

  counter = CountDown(nx, width, height, 3, 1)
  counter.run()
  handler = MyHandler(nx)
  handler.submitted = False
  while True:
    handler.completed = False
    nx.main_loop(handler)
    if handler.submitted:
      break
    print(handler.x, handler.y)
    o = nx.obj_builder(10, "fruit")
    clip = nx.clip_builder('Items/Fruits/Bananas.png', 32, 32, [])
    clip.stepTime = 0.05
    v = nx.visual_builder(o, [clip])
    v.x = 0.5 + handler.x
    v.y = 0.5 + handler.y
    nx.send_obj(o)
    n = handler.x*100+handler.y
    if n in aset:
      aset.remove(n)
    else:
      nothing_to_delete += 1

  result = True

  if len(aset) == 0 and nothing_to_delete == 0:
    message = "SUCCESS!"
    size = 2
    fill = "blue"
    fillopacity = 1
  else:
    message = "FAILURE!"
    size = 2
    fill = "red"
    fillopacity = 1
    result = False

  nx.svg(10000, draw_svg_text_full_screen(width+margin, height, message, size, fill, fillopacity), 0, 0, width+margin, height)
  counter.run()  
  nx.removeAll()
  return [result, len(aset) + nothing_to_delete]


class MyHandler(EventHandler):
  def __init__(self, nx:Nx):
    super().__init__()
    self.nx = nx

  def on_relay(self, c):
    print('relay', c)    
    cmd = c.strings[1]
    if cmd == 'input':
      self.x = c.ints[1]
      self.y = c.ints[2]
      self.completed = True
    elif cmd == 'submit':
      self.submitted = True
      self.completed = True


if __name__ == "__main__":
  nx = Nx('bonsoirdemo')
  width = 12
  height = 12
  margin = 3
  gid = 100  
  stage = nx.stage_builder(width + margin, height)
  stage.background = 'Blue'
  nx.send_stage_info(stage)
  nx.hint(hint)

    
  funcsAll = [[lambda i,j:i<j, lambda i,j:i<=j, lambda i,j:i>j, lambda i,j:i>=j],
    [lambda i,j:i==j, lambda i,j:i!=j, lambda i,j:i == j+2, lambda i,j:i != j-2],
    [lambda i,j:i < j*2, lambda i,j:i > j*2, lambda i,j:i <= j/2, lambda i,j:i >= j/2, lambda i,j:i+j<15, lambda i,j:i*j<50],
    [lambda i,j:j%2, lambda i,j:i%2, lambda i,j: j<=6, lambda i,j:i<=6, lambda i,j:i>6, lambda i,j:j>6],
    [lambda i,j:j%2 != i%2, lambda i,j:j%2 == i%2, lambda i,j:j%3 == i%3, lambda i,j:j%3 != i%3]]

  print(math.floor(random.random()*10))
  print(math.floor(random.random()*10))
  print(math.floor(random.random()*10))
  print(math.floor(random.random()*10))
  print(math.floor(random.random()*10))

  x = 100
  y = 100
  u = 100

  d = '<svg width="100" height="100">\
    <rect width="100" height="100" style="fill:rgb(0,0,255);stroke-width:0;stroke:rgb(0,0,0)" />\
  </svg>'
  '<text fill="#111" x="{x}" y="{y}" font-size="{unit}" font-family="Roboto" text-anchor="middle">{text}</text>\n'
  d1 = '<svg viewBox="0 0 100 100">\
    <text fill="#111" x="0" y="0" font-size="100" font-family="Roboto" text-anchor="middle">A</text>\
  </svg>'

  stopwatch = Stopwatch(nx, 200, [12,0,2,1])
  stopwatch.start()


  c = 0
  func = 0
  while c < len(funcsAll):
    if func == 0:
      funcs = funcsAll[c]
      v = random.random()*len(funcs)
      r = math.floor(v)
      print(c, len(funcs), v, r)
      func = funcs[r]
    result = test01(nx, width, height, margin, func)   
    print(result)
    if result[0]:
      c += 1
      func = 0
    else:
      stopwatch.num += 10
  nx.main_loop(MyHandler(nx))  

