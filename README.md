# yt-playlist-discord-webhook

![GitHub last commit](https://img.shields.io/github/last-commit/AndyThePie/yt-playlist-discord-webhook?style=flat-square) ![Requires.io](https://img.shields.io/requires/github/AndyThePie/yt-playlist-discord-webhook?style=flat-square) ![quality](https://img.shields.io/badge/quality-none-red?style=flat-square)

a python script that when run, takes all the newest videos in a youtube playlist, and POSTs it to a discord webhook. or at least, it's supposed to. 

> a note: i wrote this to introduce myself to python. the code is a mess, and whether or not it'll work is... iffy. use at your own risk.

## usage

create a `config.ini` file, and uhh:

```ini
[MAIN]
ApiKey = youtube api key...
PlaylistId = the youtube playlist id...
WebhookUrl = the webhook url.
```

something like that. install all the dependencies, and run. set up a `cron` job or something, then cross your fingers.

## license

[the unlicense](https://unlicense.org/). do whatever you want with it.
