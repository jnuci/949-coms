import googleapiclient.discovery
import argparse
import psycopg2
import numpy as np
from psycopg2.extras import RealDictCursor
from config import API_KEY, DB_PASS

def get_channel_id_from_video(youtube, video_id):
    request = youtube.videos().list(
    part = 'snippet',
    id = video_id
    )

    response = request.execute()

    return response['items'][0]['snippet']['channelId']

def get_playlist_id_from_channel(youtube, channel_id):
    request = youtube.channels().list(
        part = 'contentDetails',
        id = channel_id
    )

    response = request.execute()

    return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

def get_all_uploads(youtube, playlist_id):

    video_ids = []

    request = youtube.playlistItems().list(
    part = 'snippet',
    playlistId = playlist_id
    )

    response = request.execute()

    for vid in response['items']:
        video_ids.append(vid['snippet']['resourceId']['videoId'])

    while 'nextPageToken' in response.keys():
        
        page_token = response['nextPageToken']

        request = youtube.playlistItems().list(
        part = 'snippet',
        playlistId = playlist_id,
        pageToken = page_token
        )

        response = request.execute()

        for vid in response['items']:
            video_ids.append(vid['snippet']['resourceId']['videoId'])

    return video_ids

def scrape_comments(video_id):
    all_comments_info = []

    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=API_KEY
    )

    conn = psycopg2.connect(
        host = 'localhost',
        database = 'youtube_comments',
        user = 'postgres',
        password = DB_PASS,
    )

    cursor = conn.cursor()
    cursor.execute("SELECT comment_id FROM comments_raw")

    unique_ids = cursor.fetchall()
    unique_ids = np.array(unique_ids).squeeze()

    channel_id = get_channel_id_from_video(youtube, video_id)

    playlist_id = get_playlist_id_from_channel(youtube, channel_id)

    ids = get_all_uploads(youtube, playlist_id)

    for video_id in ids:

        request = youtube.commentThreads().list(
            part = 'snippet',
            videoId = video_id,
            maxResults = 100
        )

        response = request.execute()

        for item in response['items']:
                comment_id = item['snippet']['topLevelComment']['id']

                if comment_id in unique_ids:
                    continue
                else:
                    all_comments_info.append({'videoid': video_id,
                                            'commentid': comment_id,
                                            'content': item['snippet']['topLevelComment']['snippet']['textDisplay']})
                    
        while 'nextPageToken' in response.keys():

            newToken = response['nextPageToken']

            request = youtube.commentThreads().list(
            part = 'snippet',
            videoId = video_id,
            pageToken = newToken,
            maxResults = 100
            )

            response = request.execute()

            for item in response['items']:
                comment_id = item['snippet']['topLevelComment']['id']

                if comment_id in unique_ids:
                    continue
                else:
                    all_comments_info.append({'videoid': video_id,
                                            'commentid': comment_id,
                                            'content': item['snippet']['topLevelComment']['snippet']['textDisplay']})

    cursor.close()
    conn.close()

    return all_comments_info

def load_raw_text(video_id):

    all_comments_info = scrape_comments(video_id)

    conn = psycopg2.connect(
        host = 'localhost',
        database = 'youtube_comments',
        user = 'postgres',
        password = DB_PASS,
    )

    cursor = conn.cursor()

    try:
        for item in all_comments_info:
            cursor.execute("INSERT INTO comments_raw (video_id, comment_id, content) VALUES (%s, %s, %s)",
                    (item['videoid'], item['commentid'], item['content']))
            
        conn.commit()
            
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")

    finally:
        cursor.close()
        conn.close()

    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type = str, help = 'Video ID from target channel')
    args = parser.parse_args()

    video_id = args.video_id


    if load_raw_text(video_id):
        print('Comment loading complete')

if __name__ == "__main__":
    main()