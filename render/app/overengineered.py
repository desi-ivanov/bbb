from types import FunctionType, LambdaType
import cv2
import numpy as np
import urllib.request
import xml.etree.ElementTree as ET
import sys
from tqdm import tqdm
import re
import os
from copy import deepcopy

def format_url(origin: str, meeting_id: str, path: str):
  return "{}/presentation/{}/{}".format(origin, meeting_id, path)
  
def fetch(origin: str, meeting_id: str, path: str):
    url = format_url(origin, meeting_id, path)
    f = urllib.request.urlopen(url)
    return f.read()

def dw_image(origin: str, meeting_id: str, url: str):
  resp = fetch(origin, meeting_id, url)
  imgarr = np.asarray(bytearray(resp), dtype="uint8")
  return cv2.imdecode(imgarr, cv2.IMREAD_COLOR)

def hex_to_brg(hex: str):
  h = hex.lstrip('#')
  return tuple(int(h[i:i+2], 16) for i in (4, 2, 0))

def path_str_to_poly(p: str):
  poss = re.split("M|L|\s|,|C", p)[1:]
  cols = []
  for i in range(int(len(poss) / 2) -1):
    cols.append([int(float(poss[i*2]) ), int((float(poss[i*2+1])) )])
  
  return np.array(cols).reshape((-1,1,2))

def parse_svg_style(style: str):
  return dict([x.split(":") for x in re.split(";", style)])

def parse_svg_entry(z: ET.Element):
  return (
    path_str_to_poly(z.find("{http://www.w3.org/2000/svg}path").attrib["d"]),
    float(z.attrib["timestamp"]), 
    parse_svg_style(z.attrib["style"]),
    float(z.attrib["undo"])
  )

def render(origin: str, meeting_id: str, fps: int, output_name: str, logger: FunctionType):
  DESKSHARE_PATH = "/tmp/deskshare-{}.mkv".format(meeting_id)
  WEBCAMS_PATH = "/tmp/webcams{}.webm".format(meeting_id)
  OUTPUT_PATH = "/tmp/{}.mkv".format(output_name)

  logger("Downloading shapes")

  shapes = ET.fromstring(fetch(origin, meeting_id, "shapes.svg").decode("utf8"))
  images = [(x.attrib, dw_image(origin, meeting_id, x.attrib["{http://www.w3.org/1999/xlink}href"])) for x in shapes.findall("{http://www.w3.org/2000/svg}image")]

  WIDTH = images[0][1].shape[1]
  HEIGHT = images[0][1].shape[0]

  drawings = [parse_svg_entry(z) for sl in [x.findall("{http://www.w3.org/2000/svg}g") for x in shapes.findall("{http://www.w3.org/2000/svg}g")] for z in sl if z.find("{http://www.w3.org/2000/svg}path") != None]
  drawings = sorted(drawings, key=lambda x: x[1])

  cursor_data = ET.fromstring(fetch(origin, meeting_id, "cursor.xml").decode("utf8"))
  cursors = [(x.attrib["timestamp"], x.find("cursor").text.split(" ")) for x in cursor_data.findall("event")]

  metadata = ET.fromstring(fetch(origin, meeting_id, "metadata.xml").decode("utf8"))
  duration_milliseconds = int(metadata.find("playback").find("duration").text)

  cur_slide_idx = 0
  cur_cursor_idx = 0
  next_drawing_idx = 0

  fourcc = cv2.VideoWriter_fourcc(*"X264")
  out = cv2.VideoWriter(DESKSHARE_PATH, fourcc, fps, (WIDTH, HEIGHT))
  frames = int(duration_milliseconds / 1000 * fps)


  logger("Rendering")
  cursor_x = 0
  cursor_y = 0

  cur_drawings = []

  log_breakpoints = 10
  log_frames = list(map(lambda i: int(i * frames/log_breakpoints), range(log_breakpoints)))
  for frame in tqdm(range(frames)):
    cur_cursor = cursors[cur_cursor_idx]
    
    cursor_x = int((float(cur_cursor[1][0])) * WIDTH)
    cursor_y = int((float(cur_cursor[1][1])) * HEIGHT)

    attr, slide_img = images[cur_slide_idx]

    frame_img = deepcopy(slide_img)

    cv2.circle(frame_img, (cursor_x, cursor_y), 7, (0, 0, 255), -1)
    for drawing in cur_drawings:
      if(drawing[3] < 0 or cur_second < drawing[3]):
        cv2.polylines(frame_img, [drawing[0]], False, hex_to_brg(drawing[2]["stroke"]), int(float(drawing[2]["stroke-width"])))

    out.write(frame_img)

    cur_second = (float(frame) / float(frames)) * (float(duration_milliseconds) / 1000.0)

    while(cur_slide_idx < len(images) - 1 and cur_second >= float(images[cur_slide_idx][0]["out"])):
      cur_slide_idx = cur_slide_idx + 1
      cur_drawings = []
    
    while(cur_cursor_idx < len(cursors) - 1 and cur_second >= float(cursors[cur_cursor_idx][0])):
      cur_cursor_idx = cur_cursor_idx + 1

    while(next_drawing_idx < len(drawings) and cur_second >= float(drawings[next_drawing_idx][1])):
      cur_drawings.append(drawings[next_drawing_idx])
      next_drawing_idx = next_drawing_idx + 1
    
    if frame in log_frames:
      logger("Rendering {}%".format(int(frame / frames * 100)))
    

  out.release()
  logger("Done rendering")
  logger("Downloading audio")
  urllib.request.urlretrieve(format_url(origin, meeting_id, "video/webcams.webm"), WEBCAMS_PATH)
  logger("Merging")
  os.system("ffmpeg -y -i {} -i {} -map 0 -map 1 -acodec copy -vcodec copy {}".format(DESKSHARE_PATH, WEBCAMS_PATH, OUTPUT_PATH))
  return OUTPUT_PATH

if __name__ == "__main__":
  origin = sys.argv[1]
  meeting_id = sys.argv[2]
  fps = int(sys.argv[3])
  output_name = sys.argv[4] if len(sys.argv) > 4 else meeting_id
  render(origin, meeting_id, fps, output_name, print)