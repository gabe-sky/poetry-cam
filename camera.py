#!/bin/env python3
#
# This quick an dirty script takes a picture on a Raspberry Pi equipped with a
# Pi camera, and then uploads it to OpenAI and asks for a description of the
# scene in a four line poem.
#
# You will need to have a writable directory for storing the images and text.
# It defaults to /var/camera.  So, for instance, make it thusly:
#
#          sudo mkdir /var/camera && chmod 0777 /var/camera
#
# You will need to set an environment variable in the shell that is running this
# script.  This is your OpenAI API secret.
#
#          export OPENAI_API_KEY='sk-camera-api-zHaTB11wgIYT5IF6u4HuT'
#
# Then just run the script without any arguments and it should just work.

import argparse
import base64
from openai import OpenAI
from picamera2 import Picamera2
import time

# Let's parse some arguments!
parser = argparse.ArgumentParser()
parser.add_argument('--debug', '-d', action='store_true')
parser.add_argument('--logdir', '-l', default='/var/camera')
parser.add_argument('--temperature','-t', type=float, default=0.7)
args = parser.parse_args()

# Create an object for the camera and set its configuration
picam2 = Picamera2()
camera_config = picam2.create_still_configuration(main={"size": (1920, 1080)})
picam2.configure(camera_config)

# This function does the main work.  It takes a picture, uploads it to OpenAI
# and gets back the description.
def poetry():
  # What time is it?
  timestamp = int(time.time())
  if args.debug == True: print(f"Timestamp: {timestamp}")

  # Power up, wait a moment, and then capture.  Save the file into /var/camera
  # for posterity.  This directory needs to be writable by the user running the
  # script.
  if args.debug == True: print("Starting camera...")
  picam2.start()
  time.sleep(1)
  if args.debug == True: print("Taking photo...")
  picam2.capture_file(f"{args.logdir}/{timestamp}.jpg")
  if args.debug == True: print("Stopping camera...")
  picam2.stop()

  # Base 64 encode the jpeg
  with open(f"{args.logdir}/{timestamp}.jpg", "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode('utf-8')

  # Fire up an OpenAI object and ask it to describe the scene we just captured.
  client = OpenAI()
  if args.debug == True: print("Making OpenAI request...")
  response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "What's going on in this image?  Please describe it in a four line poem.  If there is a person, be sure to focus on that.",
          },
          {
            "type": "image_url",
            "image_url": {
              "url": f"data:image/jpeg;base64,{base64_image}",
            },
          },
        ],
      }
    ],
    max_tokens=300,
    temperature=args.temperature,
  )

  # Print out the poem.
  print(f"\n{response.choices[0].message.content}\n")

  # Record the poem for posterity in /var/camera
  with open(f"{args.logdir}/{timestamp}.txt","w") as file:
    file.write(response.choices[0].message.content)

def main():
  try:
    while True:
      poetry()
      input(f"Hit return to do it again ...\n(Or control-C to quit.)")
  except KeyboardInterrupt:
    pass

if __name__ == "__main__":
  main()
