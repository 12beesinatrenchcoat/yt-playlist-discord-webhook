# dependency hell
import argparse
from datetime import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed
from googleapiclient.discovery import build
import iso8601
import socket
import time

# a single argument.
parser = argparse.ArgumentParser(description="Fetch videos from a YouTube playlist, and then post them to a Discord webhook.")
parser.add_argument('--offset', type=int, default=0, help="offset timestamp by x seconds. (e.g. a value of 60 will send videos added up to 60 seconds ago / the script was last run.)")
args = parser.parse_args()

from decouple import config
api_key = config('ApiKey')
playlist_id = config('PlaylistID')
embed_text = config('EmbedText')

youtube = build('youtube', 'v3', developerKey=api_key)


def get_user_info(_user_id):
    # TODO: return user name (who added to playlist) + profile picture (author img)
    return


def get_playlist_items():

    # look for file titled "last_video_timestamp"
    # this is used to compare timestamps of videos in the playlist (no old videos sent (again)!)
    now = datetime.now().timestamp()
    try:
        with open('last_video_timestamp', 'r+') as f:
            last_video_timestamp = float(f.read())
            f.seek(0)
            f.write(str(now))
            f.truncate()

    except FileNotFoundError:  # if there is no file, default to using current time.
        with open('last_video_timestamp', 'w') as f:
            f.write(str(now))
            last_video_timestamp = now

    args = parser.parse_args()
    last_video_timestamp -= args.offset  # adjusting last_video_timestamp by the offset.

    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=50  # TODO: pagination instead of this nonsense
    )

    for attempt in range(10):
        try:
            print('executing request...')
            response = request.execute()
        except socket.timeout:
            print('request timed out...')
            continue
        else:
            print('request successful!')
            break
    else:
        print('request timed out. a lot. something has gone catastrophically wrong.')
        exit()

    videos = []

    for video in response['items']:

        snippet = video['snippet']
        timestamp = iso8601.parse_date(snippet['publishedAt']).timestamp()
        video['snippet']['publishedAt'] = timestamp

        if timestamp > last_video_timestamp:
            videos.insert(0, video)
        else:
            break

    for video in videos:          # Let the user decide what they want the embed message to say, if the config has "videoURL" then send the video URL.
        if embed_text is None:    # The video URL will not embed as there is already an embed on the message.
            execute_webhook("New video in playlist!", video_info_to_embed(video)) # If configuration field is blank then run the default.
        if embed_text == "VideoURL":  # sends video URL.
            snippet = video['snippet']  # This is needed as otherwise it uses the old snippet.
            execute_webhook('https://youtu.be/' + snippet['resourceId']['videoId'], video_info_to_embed(video)) 
        else:
            execute_webhook(embed_text, video_info_to_embed(video))  # If nothing else then use what the user put in.

    print("that's all folks!")


def video_info_to_embed(video):

    print(video)

    snippet = video['snippet']

    video_owner_channel_url = 'https://youtube.com/channels/' + snippet['videoOwnerChannelId']
    video_url = 'https://youtu.be/' + snippet['resourceId']['videoId']

    try:
        thumbnail_url = snippet['thumbnails']['maxres']['url']
    except KeyError:
        thumbnail_url = snippet['thumbnails']['high']['url']

    embed = DiscordEmbed()

    embed.set_title(snippet['title'])
    embed.set_url(video_url)
    embed.set_author(name=snippet['videoOwnerChannelTitle'], url=video_owner_channel_url)
    embed.set_thumbnail(url=thumbnail_url)
    embed.set_timestamp(snippet['publishedAt'])
    embed.set_color(16711680)

    return embed


def execute_webhook(content, embed):

    webhook_url = config('WebhookUrl')
    webhook = DiscordWebhook(url=webhook_url, content=content)

    webhook.add_embed(embed)

    response = webhook.execute()

    if response.status_code == 429:  # for some reason there's an additional rate limit. whoops.
        retry_after = response.json()['retry_after']
        print(retry_after)
        time.sleep(retry_after/1000)
        response = webhook.execute()

    headers = response.headers
    print('limit ' + headers['x-ratelimit-remaining'] + ' cooldown ' + headers['x-ratelimit-reset-after'])
    if headers['x-ratelimit-remaining'] == '0':
        print('sleeping...')
        time.sleep(float(headers['x-ratelimit-reset-after']) + 0.1)


if __name__ == '__main__':
    get_playlist_items()
