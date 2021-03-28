# dependency hell
from datetime import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed
from googleapiclient.discovery import build
import configparser
import iso8601
import socket
import time

config = configparser.ConfigParser()
config.read('config.ini')
api_key = config['MAIN']['ApiKey']
playlist_id = config['MAIN']['PlaylistId']

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
            f.write(str(now))

    except FileNotFoundError:
        with open('last_video_timestamp', 'w') as f:
            f.write(str(now))
            last_video_timestamp = now

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

    for video in videos:
        execute_webhook("New video in playlist!", video_info_to_embed(video))

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

    webhook_url = config['MAIN']['WebhookUrl']
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
