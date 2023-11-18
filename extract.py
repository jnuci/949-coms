import googleapiclient.discovery
import argparse
import psycopg2
import numpy as np
from config import API_KEY, DB_PASS, LOCALHOST

# retrive channel id from youtube data API
def get_channel_id_from_video(youtube, video_id):
    request = youtube.videos().list(
        part = 'snippet',
        id = video_id
    )

    response = request.execute()

    return response['items'][0]['snippet']['channelId']

# retrieve playlist id of all channel uploads
def get_playlist_id_from_channel(youtube, channel_id):
    request = youtube.channels().list(
        part = 'contentDetails',
        id = channel_id
    )

    response = request.execute()

    return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

# retrieve each video id from playlist id
def get_all_uploads(youtube, playlist_id):
    
    video_ids = []

    request = youtube.playlistItems().list(
    part = 'snippet',
    playlistId = playlist_id
    )

    response = request.execute()

    # store video ids in array
    for vid in response['items']:
        video_ids.append(vid['snippet']['resourceId']['videoId'])

    # if another page of video ids exists
    # retrive video ids from next page
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

# retrieve data for each comment
def scrape_comments(video_id):
    all_comments_info = []

    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=API_KEY
    )

    conn = psycopg2.connect(
        host = LOCALHOST,
        port = 5432,
        database = 'youtube_comments',
        user = 'postgres',
        password = DB_PASS,
    )

    # retrieve previously loaded comments
    cursor = conn.cursor()
    cursor.execute("SELECT comment_id FROM comments_raw")

    unique_ids = cursor.fetchall()
    unique_ids = np.array(unique_ids).squeeze()

    new_ids = set()

    channel_id = get_channel_id_from_video(youtube, video_id)

    playlist_id = get_playlist_id_from_channel(youtube, channel_id)

    ids = get_all_uploads(youtube, playlist_id)

    # keep count of comments with likes value updated
    updated = 0

    for video_id in ids:

        request = youtube.commentThreads().list(
            part = 'snippet',
            videoId = video_id,
            maxResults = 100
        )

        response = request.execute()

        # iterate over each comment in response and collect relevant data
        for item in response['items']:
                comment_id = item['snippet']['topLevelComment']['id']

                content = item['snippet']['topLevelComment']['snippet']['textDisplay']

                published = item['snippet']['topLevelComment']['snippet']['publishedAt']

                username = item['snippet']['topLevelComment']['snippet']['authorDisplayName']

                pfp_url = item['snippet']['topLevelComment']['snippet']['authorProfileImageUrl']

                likes = item['snippet']['topLevelComment']['snippet']['likeCount']

                # update like count if comment previously loaded
                # otherwise add comment to resulting array
                if comment_id in unique_ids or comment_id in new_ids:
                    cursor.execute('UPDATE comments_raw SET likes = %s WHERE comment_id = %s', (likes, f'{comment_id}'))
                    conn.commit()
                    updated += 1
                else:
                    new_ids.add(comment_id)
                    all_comments_info.append({'videoid': video_id,
                                            'commentid': comment_id,
                                            'content': content,
                                            'published': published,
                                            'username': username,
                                            'profile_image': pfp_url,
                                            'likes': likes})
                    
        # repeat process while another page of comments exists
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

                content = item['snippet']['topLevelComment']['snippet']['textDisplay']

                published = item['snippet']['topLevelComment']['snippet']['publishedAt']

                username = item['snippet']['topLevelComment']['snippet']['authorDisplayName']

                pfp_url = item['snippet']['topLevelComment']['snippet']['authorProfileImageUrl']

                likes = item['snippet']['topLevelComment']['snippet']['likeCount']

                if comment_id in unique_ids or comment_id in new_ids:
                    cursor.execute('UPDATE comments_raw SET likes = %s WHERE comment_id = %s', (likes, f'{comment_id}'))
                    conn.commit()
                    updated += 1
                else:
                    new_ids.add(comment_id)
                    all_comments_info.append({'videoid': video_id,
                                            'commentid': comment_id,
                                            'content': content,
                                            'published': published,
                                            'username': username,
                                            'profile_image': pfp_url,
                                            'likes': likes})
    cursor.close()
    conn.close()

    return all_comments_info, updated

# loading comment data into source database
def load_raw_text(video_id):
    all_comments_info, updated = scrape_comments(video_id)

    # if no new comments, return early
    if not all_comments_info:
        print("No new comments found")
        return True, updated, 0
    
    conn = psycopg2.connect(
        host = LOCALHOST,
        port = 5432,
        database = 'youtube_comments',
        user = 'postgres',
        password = DB_PASS,
    )

    cursor = conn.cursor()

    try:
        for item in all_comments_info:
            cursor.execute("INSERT INTO comments_raw (video_id, comment_id, content, published, username, profile_image, likes) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (item['videoid'], item['commentid'], item['content'], item['published'], item['username'], item['profile_image'], item['likes']))
            
        conn.commit()
            
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")

    finally:
        cursor.close()
        conn.close()

    return True, updated, len(all_comments_info)

# load raw text and log changes
def main():
    # add parsing argument for video id
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', type = str, help = 'Video ID from target channel')

    args = parser.parse_args()

    video_id = args.i

    loaded, updated, new = load_raw_text(video_id)

    if loaded:
        print(f'{updated} total comments updated')
        print(f'{new} new comments found')
        print('Comment loading complete')
    
if __name__ == "__main__":
    main()