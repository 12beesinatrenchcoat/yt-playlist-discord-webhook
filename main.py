# Dependency hell
import argparse
from decouple import config
from datetime import datetime
from discord_webhook import DiscordWebhook, DiscordEmbed
from googleapiclient.discovery import build
import iso8601
import socket
import time

# Setting up command line argument(s)...
parser = argparse.ArgumentParser(
    description="Fetches videos from a YouTube playlist, \
    and then posts them to a Discord webhook."
)
parser.add_argument(
    '--offset',
    type=int,
    default=0,
    help="Offset timestamp by an amount of seconds. \
    (e.g. A value of 60 will send videos added up to 60 seconds ago \
    / the script was last run.)"
)

args = parser.parse_args()

# Environment variables!
api_key = config('ApiKey')  # API Key for YouTube Data API.
playlist_id = config('PlaylistID')  # Playlist ID for a YouTube playlist.
webhook_url = config('WebhookUrl')
embed_text = config('EmbedText', default=None)  # Optional message content.

youtube = build('youtube', 'v3', developerKey=api_key)


def get_comparison_timestamp():
    # The last time the script was ran. otherwise, return the current time.
    # This is used to determine if a video is "new".

    now = datetime.now().timestamp()

    try:
        with open('comparison_timestamp', 'r+') as f:
            comparison_timestamp = float(f.read())
            f.seek(0)
            f.write(str(now))
            f.truncate()

    except FileNotFoundError:  # Default to using current time.
        with open('comparison_timestamp', 'w') as f:
            f.write(str(now))
            comparison_timestamp = now

    comparison_timestamp -= args.offset

    return comparison_timestamp


def get_playlist_items():
    # Requesting playlistItems from the YouTube API.

    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=50  # TODO: Pagination instead of this nonsense
    )

    for _attempt in range(10):
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
        print('Request timed out... a lot. \
        Something has gone catastrophically wrong.')
        exit()

    return response


def filter_playlist_items_by_timestamp(response, comparison_timestamp):
    # Filtering the response to which videos have been added.
    # Input should be response from playlistItems.list.

    videos = []

    for video in response['items']:

        snippet = video['snippet']
        timestamp = iso8601.parse_date(snippet['publishedAt']).timestamp()
        video['snippet']['publishedAt'] = timestamp

        if timestamp > comparison_timestamp:
            videos.insert(0, video)
        else:
            break

    return videos


def execute_webhook(content, embed):
    # The part in which the message is posted.
    webhook = DiscordWebhook(url=webhook_url, content=content)

    webhook.add_embed(embed)

    response = webhook.execute()

    if response.status_code == 429:  # I guess there's another rate limit.
        retry_after = response.json()['retry_after']
        print(retry_after)
        time.sleep(retry_after/1000)
        response = webhook.execute()

    headers = response.headers
    print('limit ' +
          headers['x-ratelimit-remaining'] +
          ' cooldown ' +
          headers['x-ratelimit-reset-after'])

    if headers['x-ratelimit-remaining'] == '0':
        print('sleeping...')
        time.sleep(float(headers['x-ratelimit-reset-after']) + 0.1)


def video_info_to_embed(video):
    # Taking in video info, then turning it into a Discord Embed.
    print(video)

    snippet = video['snippet']

    video_owner_channel_url = ('https://youtube.com/channels/' +
                               snippet['videoOwnerChannelId'])
    video_url = 'https://youtu.be/' + snippet['resourceId']['videoId']

    try:
        thumbnail_url = snippet['thumbnails']['maxres']['url']
    except KeyError:
        # Alternative thumbnail; not all videos have "maxres" thumbnails
        thumbnail_url = snippet['thumbnails']['high']['url']

    embed = DiscordEmbed()

    embed.set_title(snippet['title'])
    embed.set_url(video_url)
    embed.set_author(name=snippet['videoOwnerChannelTitle'],
                     url=video_owner_channel_url)
    embed.set_thumbnail(url=thumbnail_url)
    embed.set_timestamp(snippet['publishedAt'])
    embed.set_color(16711680)

    return embed


if __name__ == '__main__':
    # Now putting it all together...

    response = get_playlist_items()
    comparison_timestamp = get_comparison_timestamp()

    videos = filter_playlist_items_by_timestamp(response, comparison_timestamp)

    print(embed_text)

    for video in videos:
        if embed_text is None:  # Send the default message.
            execute_webhook("New video in playlist!",
                            video_info_to_embed(video))
        elif embed_text == "VideoURL":  # Sends video URL.
            execute_webhook('https://youtu.be/' +
                            video['snippet']['resourceId']['videoId'],
                            video_info_to_embed(video))
        else:  # If other value, use what the user has specified.
            execute_webhook(embed_text, video_info_to_embed(video))

    print("that's all folks!")
