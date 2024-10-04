import json
import pandas as pd

# Load the provided JSON file
file_path = 'data/7089722160071200027/full.json'

# Read the JSON data
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Initialize lists to store comments and replies data
comments_data = []
replies_data = []

# Iterate over each comment and its replies
for comment in data.get('comments', []):
    # Extract comment data
    comments_data.append({
        "comment_id": comment.get('cid'),
        "username": comment.get('username'),
        "nickname": comment.get('nickname'),
        "comment": comment.get('comment'),
        "create_time": comment.get('create_time'),
        "likes": comment.get('likes'),
        "total_reply": comment.get('total_reply'),
        "avatar": comment.get('avatar')
    })
    
    # Extract replies data
    for reply in comment.get('replies', []):
        replies_data.append({
            "comment_id": comment.get('cid'),
            "reply_to_nickname": reply.get('reply_to_nickname'),
            "reply_to_username": reply.get('reply_to_username'),
            "reply_text": reply.get('text'),
            "likes": reply.get('likes'),
            "reply_create_time": reply.get('create_time'),
            "reply_username": reply.get('username'),
            "reply_nickname": reply.get('nickname'),
            "reply_avatar": reply.get('avatar')
        })

# Convert the lists to DataFrames
comments_df = pd.DataFrame(comments_data)
replies_df = pd.DataFrame(replies_data)

# Save the DataFrames to CSV files
comments_csv_path = 'dataset/comments.csv'
replies_csv_path = 'dataset/replies.csv'

comments_df.to_csv(comments_csv_path, index=False)
replies_df.to_csv(replies_csv_path, index=False)

(comments_csv_path, replies_csv_path)