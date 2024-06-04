# Overview

So you want to turn your Raspberry Pi with a Pi Camera into an AI poetry-writing parlor trick?  You've come to the right place.  That's exactly what this little project is all about!

Note: you will need a *paid* OpenAI account to use the API.  So far it looks like each poem, using GPT-4o, is costing me under two cents.

# Hardware

For the brains, I'm using a Raspberry Pi Zero 2 W.  Pretty much any camera-capable Pi should work, but you'll need network connectivity of some form or another in order to hit the OpenAI API and generate a poem.

The python script will output to STDOUT.  I have a miniature screen and keyboard attached so that I can login and run it from an interactive shell, but you can also just SSH into the thing and run over the network.  I'd love to see someone turn this into a service that I can just run on the main tty without logging in, too.

I am using the third generation Pi camera, but older versions should be fine as long as they're compatible with the python3 picamera2 libraries.

# Raspberry Pi OS Image Additions

I used a stock Raspberry Pi OS Lite image on mine and then added some things.  The Lite image is just that, light, and doesn't include a desktop environment.  You can, in theory, use a full install if you prefer but I haven't tested it.

First, you'll need to add all the pycamera2 extras:

```
sudo apt install -y python3-picamera2
```

Next you'll need to install the OpenAI libraries.  These are not available as a nice and tidy Debian package yet, so you'll have to install them over the system libraries.  Given this Pi is only ever going to do my camera stuff, I'm comfortable with that disgusting hack.  If you're not, you're on your own getting it installed the proper way.  (Pull requests welcome!)

```
sudo apt install -y python3-pip
sudo pip3 install openai --break-system-packages
```

By default, the script will write a copy of the image and poem to the `/var/camera` directory.  This does not exist on a stock system, so you'll need to create it and make it writable by the user running the script.

```
sudo mkdir /var/camera
sudo chmod 0777 /var/camera
```


# OpenAI API Key

You will need an OpenAI API key.  I'm afraid this will cost you money, but so far I'm finding that each poem costs me under two cents.

# Running the script

First, you'll need to export an environment variable with your OpenAI API key.  You might add this to your `.bashrc` file if you feel comfortable putting secrets there.  For example:

```
export OPENAI_API_KEY='sk-your-api-zHaTB11wgIYT'
```

Also, you may wish to suppress the debug output of the camera.  It can be quite chatty.  You'll see what I mean.  This, too, might be something you want to add to your `.bashrc` file.  Here's how to make it log at the ERROR level.

```
export LIBCAMERA_LOG_LEVELS=3
```

And now, just run the script!

```
python3 camera.py
```

It will load up the libraries, which takes a few seconds.  Then it will take a photo and upload it to OpenAI instructing it to describe the scene in a four-line poem.  It will print out the result.  Then it goes into a loop waiting for you to hit return, indicating that you want it to take another picture and write another poem.

You'll find that the initial invocation requires at least ten seconds before an image is even taken, let alone passed to OpenAI for poetry writing.  The subsequent captures are almost instantaneous after you hit return, but the poetry writing will still take a few seconds.

There are a few options that can be tuned through command-line flags.

Use the `--debug` flag to have the script tell you what it's doing when.

Use the `--log-dir` flag with an argument to tell it to store things in a different directory than the default `/var/camera` directory.

Use the `--temperature` flag to pass a different temperature to OpenAI than the default `0.7`.

# Caveats

* The script is pretty simple, lacking sophisticated error handling and tuning.
* Use of the actual OpenAI library feels unnecessary and this could be re-written with just an HTTPS request.
