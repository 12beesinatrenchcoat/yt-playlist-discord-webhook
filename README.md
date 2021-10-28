# yt-playlist-discord-webhook

![GitHub last commit](https://img.shields.io/github/last-commit/AndyThePie/yt-playlist-discord-webhook?style=flat-square) ![Requires.io](https://img.shields.io/requires/github/AndyThePie/yt-playlist-discord-webhook?style=flat-square) ![quality](https://img.shields.io/badge/quality-none-red?style=flat-square)

a python script that when run, takes all the newest videos in a youtube playlist, and POSTs it to a discord webhook. or at least, it's supposed to. 

> a note: i wrote this to introduce myself to python. the code is a mess, and whether or not it'll work is... iffy. use at your own risk.

## Usage

Look over the [YouTube Data API Overview](https://developers.google.com/youtube/v3/getting-started) in order to obtain your API key, alternatively the necessary steps have been copied below.
1. Create a new project in the [Google Developers Console](https://console.developers.google.com/) and [obtain authorization credentials](https://developers.google.com/youtube/registering_an_application) so your application can submit API requests.
2. After creating your project, make sure the YouTube Data API is one of the services that your application is registered to use: 
    1. Go to the [API Console](https://console.developers.google.com/) and select the project that you just registered.
    2. Visit the [Enabled APIs page](https://console.developers.google.com/apis/enabled).  In the list of APIs, make sure the status is **ON** for the **YouTube Data API v3**.
3. Edit the [.env](/.env) (or set up your environment variables): 

```sh
ApiKey = # youtube api key...
PlaylistID = # the youtube playlist ID (the part after `playlist?list=`)
WebhookUrl = # the webhook url.
EmbedText = # the message you want to be sent with the embed. defaults to: `New video in playlist!` you can also say `videoURL` to send the video's URL.
```

## Running

1. Install all dependencies with `pip install -r requirements.txt`
2. Using whatever your python prefix is, run `main.py`
Windows: `py main.py`
3. If you want to run this at certain times, it is recommended you configure a cron job, [this](https://crontab.guru/) will make your life easier.

## License

[the unlicense](https://unlicense.org/). do whatever you want with it.
