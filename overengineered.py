from typing import final
import cv2
import numpy as np
import urllib.request
import xml.etree.ElementTree as ET
import sys
from tqdm import tqdm
import re

from copy import deepcopy

_, origin, meeting_id, fps = sys.argv

FPS = int(fps)

def format_url(path: str):
  return "{}/presentation/{}/{}".format(origin, meeting_id, path)
def fetch(path: str):
    url = format_url(path)
    f = urllib.request.urlopen(url)
    return f.read()

def dw_image(url: str):
  resp = fetch(url)
  imgarr = np.asarray(bytearray(resp), dtype="uint8")
  return cv2.imdecode(imgarr, cv2.IMREAD_COLOR)

def hex_to_brg(hex: str):
  h = hex.lstrip('#')
  return tuple(int(h[i:i+2], 16) for i in (4, 2, 0))

def path_str_to_poly(p: str):
  # p = "M217.05484 621.57536L217.05483 621.57539L215.00003 619.5206L206.78085 613.35619L206.78085 611.30141L198.56167 605.13706L196.50687 603.08221L190.34249 601.02743L184.17811 603.08221L173.90413 609.24662L165.68497 617.46582L155.41099 627.7398L147.19181 638.01371L134.86304 654.45211L130.75345 666.78087L126.64386 677.05485"
  poss = re.split("M|L|\s|,|C", p)[1:]
  cols = []
  for i in range(int(len(poss) / 2) -1):
    cols.append([int(float(poss[i*2]) / VIEWBOX_WIDTH * WIDTH), int(float(poss[(i+1)*2]) / VIEWBOX_HEIGHT * HEIGHT)])
  
  return np.array(cols).reshape((-1,1,2))

def parse_svg_style(style: str):
  return dict([x.split(":") for x in re.split(";", style)])

def parse_svg_entry(z: ET.Element):
  return (
    path_str_to_poly(z.find("{http://www.w3.org/2000/svg}path").attrib["d"]),
    float(z.attrib["timestamp"]), 
    parse_svg_style(z.attrib["style"])
  )

print("Downloading shapes")

shapes = ET.fromstring(fetch("shapes.svg").decode("utf8"))
_, _, VIEWBOX_WIDTH, VIEWBOX_HEIGHT = [int(x) for x in shapes.attrib["viewBox"].split(" ")]
images = [(x.attrib, dw_image(x.attrib["{http://www.w3.org/1999/xlink}href"])) for x in shapes.findall("{http://www.w3.org/2000/svg}image")]

WIDTH = images[0][1].shape[1]
HEIGHT = images[0][1].shape[0]

drawings = [parse_svg_entry(z) for sl in [x.findall("{http://www.w3.org/2000/svg}g") for x in shapes.findall("{http://www.w3.org/2000/svg}g")] for z in sl if z.find("{http://www.w3.org/2000/svg}path") != None]

cursor_data = ET.fromstring(fetch("cursor.xml").decode("utf8"))
cursors = list(map(lambda x: (x.attrib["timestamp"], x.find("cursor").text.split(" ")), cursor_data.findall("event")))

metadata = ET.fromstring(fetch("metadata.xml").decode("utf8"))
duration_milliseconds = int(metadata.find("playback").find("duration").text)

cur_slide_idx = 0
cur_cursor_idx = 0
cur_drawing_idx = 0

fourcc = cv2.VideoWriter_fourcc(*"X264")
out = cv2.VideoWriter('deskshare.mkv', fourcc, FPS, (WIDTH, HEIGHT))
frames = int(duration_milliseconds / 1000 * FPS)


print("Rendering")
cursor_x = 0
cursor_y = 0
for frame in tqdm(range(frames)):
  cur_cursor = cursors[cur_cursor_idx]
  
  cursor_x = int((float(cur_cursor[1][0])) * WIDTH)
  cursor_y = int((float(cur_cursor[1][1])) * HEIGHT)

  cur_drawing = drawings[cur_drawing_idx]
  attr, slide_img = images[cur_slide_idx]

  frame_img = deepcopy(slide_img)

  cv2.circle(frame_img, (cursor_x, cursor_y), 7, (0, 0, 255), -1)
  cv2.polylines(frame_img, [cur_drawing[0]], False, hex_to_brg(cur_drawing[2]["stroke"]), int(float(cur_drawing[2]["stroke-width"])))

  out.write(frame_img)

  cur_second = (float(frame) / float(frames)) * (float(duration_milliseconds) / 1000.0)
  print(cur_second)

  while(cur_slide_idx < len(images) - 1 and cur_second >= float(attr["out"])):
    cur_slide_idx = cur_slide_idx + 1
  
  while(cur_cursor_idx < len(cursors) - 1 and cur_second >= float(cur_cursor[0])):
    cur_cursor_idx = cur_cursor_idx + 1

  while(cur_drawing_idx < len(drawings) - 1 and cur_second >= float(cur_drawing[1])):
    cur_drawing_idx = cur_drawing_idx + 1

out.release()

print("Done rendering")
print("Downloading audio")
webcams = urllib.request.urlretrieve(format_url("video/webcams.webm"), "webcams.webm")
