import sys
from overengineered import render
from merger import merge
import json
import boto3
import os
import requests
import urllib

TG_API_KEY = os.environ["TG_API_KEY"]


s3 = boto3.client("s3")

def main(jsonbody):

  def send_msg(text: str): 
    requests.get("https://api.telegram.org/bot{}/sendMessage?{}".format(TG_API_KEY, urllib.parse.urlencode({"chat_id": jsonbody["chat_id"], "text": text})))

  origin = jsonbody["origin"]
  meeting_id = jsonbody["meeting_id"]
  output_name = meeting_id

  res = requests.head("{}/presentation/{}/deskshare/deskshare.webm".format(origin, meeting_id))

  # if deskshare exists we are lucky and can just merge 
  # immediately the deskshare recording and the audio 
  if(res.ok):
    output_path = merge(origin, meeting_id, output_name)
    s3_path = "{}.webm".format(output_name)
  else:
    fps = int(jsonbody["fps"]) if "fps" in jsonbody else 3
    output_path = render(origin, meeting_id, fps, output_name, send_msg)
    s3_path = "{}.mkv".format(output_name)

  with open(output_path, "rb") as f:
    s3.upload_fileobj(f, "render-bbb", s3_path)
  signed = s3.generate_presigned_url('get_object',Params={'Bucket': "render-bbb",'Key': s3_path},ExpiresIn=360000)
  
  print(signed)

  send_msg(signed)
  return signed
  

def handler(event, context):
  print(event)
  jsonbody = json.loads(event["body"])
  print(jsonbody)

  signed = main(jsonbody)

  return {
      "statusCode": 200,
      "body": signed,
  }


if __name__ == "__main__":
  print(main({"origin":sys.argv[1], "meeting_id":sys.argv[2]}))
