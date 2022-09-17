# yt-playlist-discord-webhook

![GitHub last commit](https://img.shields.io/github/last-commit/AndyThePie/yt-playlist-discord-webhook?style=flat-square) 
![quality](https://img.shields.io/badge/quality-none-red?style=flat-square) 
![Maintenance](https://img.shields.io/maintenance/no/2022?style=flat-square)

A Python script that when run, takes all the newest videos in a YouTube playlist, and POSTs it to a discord webhook. 
Or at least, it's supposed to. 

> A note: I wrote this to introduce myself to Python. The code is a mess, and whether it'll work is... iffy. Use at your own risk.  
> Additionally, I have no real intention of maintaining this. things may be broken down the line. Apologies.

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
2. Run `main.py`.
   - Optionally, use `--offset [seconds]` to filter videos added [seconds] ago.

Consider running a [cron job](https://crontab.guru/), using [GitHub Actions](/.github/workflows/YTPDW.yml), or just some looping script to run this at a regular interval.

## License

[The Unlicense](https://unlicense.org/). Do whatever you want with it.
