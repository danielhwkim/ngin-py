import random
from command_pb2 import Head, NStageInfo, JoystickDirectionals, TouchMotion, NEvent, NObject, NVisual, NBody, NClip, NClipType, BodyShape, BodyType, Cmd
import json
import math
from ngin import Nx, EventHandler, NObjectInfo, EventInfo
from threading import Timer

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


class Util:
  def __init__(self, nx) -> None:
    self.nx = nx

  def draw_svg_grid(self, x, y, func):
    unit = 100
    ori = '<svg viewBox="0 0 {x} {y}>\n'.format(x=unit*x, y=unit*y)
    padding = 5
    for i in range(x):
      for j in range(y):
        if func(i,j):
          ori += '<rect x="{x}" y="{y}" width="{width}" height="{height}" stroke="#777" fill="none" stroke-width="4" />\n'.format(x=padding + unit*i, y=padding + unit*j, width=unit - padding*2, height=unit - padding*2)
          ori += '<text fill="#777" x="{x}" y="{y}" font-size="{size}" font-family="Roboto" text-anchor="middle" >{i}:{j}</text>\n'.format(x=unit/2 + unit*i, y=unit*0.6 + unit*j, size=unit/3, i=i,j=j)
        else:
          ori += '<rect x="{x}" y="{y}" width="{width}" height="{height}" stroke="#777" fill="#777" stroke-width="4" />\n'.format(x=padding + unit*i, y=padding + unit*j, width=unit - padding*2, height=unit - padding*2)
    ori += '</svg>'
    return ori

  def draw_svg_text_full_screen(self, x, y, text, size=1, fill="#111", fillopacity=1):
    unit = 100    
    ori = '<svg viewBox="0 0 {x} {y}">\n'.format(x=x*unit, y=y*unit)
    ori += '<text fill="{fill}" fill-opacity="{fillopacity}" x="{x}" y="{y}" font-size="{size}" font-family="Roboto" text-anchor="middle" >{text}</text>\n'.format(fill=fill, fillopacity=fillopacity, x=x*unit/2, y=y*unit/2 + unit*size*0.35, size=unit*size,text=text)
    ori += '</svg>'
    return ori

  def count_down(self, width, height, num, time):
    print(width, height, num, time)
    fillopacity = 0.5
    textsize = 5
    self.nx.svg(100+num, self.drawSvgTextFullScreen(width, height, "{num}".format(num=num), textsize, fillopacity), 0, 0, width, height)

    while num > 0:
      self.nx.translate(100+num, width, 0, time)
      num -=1
      self.nx.svg(100+num, self.drawSvgTextFullScreen(width, height, "{num}".format(num=num), textsize, fillopacity), 0, 0, width, height)
      self.nx.translate(100+num, width, 0, time, "ease", True)
      value = self.nx.translate(100+num, 0, 0, time, True)

      print('ack:', value)
  
      self.nx.remove(100+num+1)
      value = self.nx.translate(100+num, width, 0, time, True)

      print('ack:', value)
      self.nx.remove(100+num)

      print('end')

  def draw_svg_text(self, x, y, text):
      unit = 100    
      ori = '<svg viewBox="0 0 {x} {y}">\n'.format(x=x*unit, y=y*100)
      ori += '<text fill="#888" x="{x}" y="{y}" font-size="{unit}" font-family="Roboto" text-anchor="middle">{text}</text>\n'.format(x=x, y=y + unit, unit=unit, text=text)
      #ori += '<rect x="{x}" y="{y}" style="fill:rgb(0,0,255);stroke-width:3;stroke:rgb(0,0,0)/>\n'.format(x=x, y=y + unit)      
      ori += '</svg>'
      return ori


class Stopwatch:
  def __init__(self, nx, oid, rect):
    self.nx = nx
    self.rect = rect
    self.w = rect[2]
    self.h = rect[3]
    self.oid = oid
    self.num = 0
    self.running = False      
    self.util = Util(nx)  
    
  def time_out(self):
    if not self.running:
      return

    self.nx.remove(self.oid)

    self.num += 1
    self.nx.svg(self.oid, self.util.draw_svg_text(self.w, self.h, '{num}'.format(num=self.num)), self.rect[0], self.rect[1], self.rect[2], self.rect[3])
    self.nx.timer(self.oid, 1)
    #Timer(1000, )
    
  def run(self):
    self.running = True
    self.nx.svg(self.oid, self.util.draw_svg_text(self.w, self.h, '{num}'.format(num=self.num)), self.rect[0], self.rect[1], self.rect[2], self.rect[3])
    self.nx.timer(self.oid, 1)
    #Timer(1000, )

  def stop(self):
    self.running = False
    return self.num

class MyHandler(EventHandler):
  def __init__(self, nx:Nx):
    self.nx = nx     
  
  def on_tap(self, tap):
    print(tap.x, tap.y)
    #nx.translate(100, tap.x, tap.y, 0, 'easeInOut', True)

  def on_event(self, c:EventInfo):
    print(c)
    if c.id == 200:
      self.stopwatch.time_out()


if __name__ == "__main__":
  nx = Nx('bonsoirdemo')
  handler = MyHandler(nx)
  nx.set_event_handler(handler)  
  width = 12
  height = 12
  margin = 3
  gid = 100  

  nx.send_stage_info(nx.stage_builder(width + margin, height))
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
  nx.svg(300, d, 0, 0, 1, 1)  
  nx.svg(300, d, 1, 1, 2, 2)
  #util = Util(nx) 
  #nx.svg(400, util.draw_svg_text(1, 1, 'A'), 0, 0, 1, 1)


  handler.stopwatch = Stopwatch(nx, 200, [12,0,2,1])
  handler.stopwatch.run()

  '''
  c = 0
  func = 0
  while c < funcsAll.length:
    if func == 0:
      funcs = funcsAll[c]
      v = math.random()*funcs.length
      r = math.floor(v)
      print(c, funcs.length, v, r)
      func = funcs[r]
    #result = test01(nx, width, height, margin, func, stopwatch)
    #print(result)
    #if result[0]:
    #  c += 1
    #  func = 0
    #else:
    #  stopwatch.num += 10'''
  nx.main_loop()  

