
import urllib.request
import os
import sys

def fetch_file(origin: str, meeting_id: str, type: str):
  print("downloading {}".format(type))
  f = urllib.request.urlopen("{}/presentation/{}/{}".format(origin, meeting_id, type))
  return f.read()

def merge(origin: str, meeting_id: str, output_name: str):
  deskshare = fetch_file(origin, meeting_id, "deskshare/deskshare.webm")
  webcams = fetch_file(origin, meeting_id, "video/webcams.webm")
  DESKSHARE_PATH = "/tmp/{}-deskshare.webm".format(meeting_id)
  WEBCAMS_PATH = "/tmp/{}-webcams.webm".format(meeting_id)
  OUTPUT_PATH = "/tmp/{}.webm".format(output_name)
  
  with open(DESKSHARE_PATH, "wb") as f:
    f.write(deskshare)

  with open(WEBCAMS_PATH, "wb") as f:
    f.write(webcams)
  
  command = "ffmpeg -y -i {} -i {} -c copy {}".format(DESKSHARE_PATH, WEBCAMS_PATH, OUTPUT_PATH)
  os.system(command)

  return OUTPUT_PATH

if __name__ == "__main__":
  origin = sys.argv[1]
  meeting_id = sys.argv[2]
  print(merge(origin, meeting_id, meeting_id))
