import requests
import logging
from requests import Response
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [ %(levelname)s ]\t:: %(message)s', datefmt="%Y-%m-%dT%H:%M:%S")

class Comment:
    def __init__(self) -> None:
        self.__result: dict = {}
        self.__result["caption"] = None
        self.__result["date_now"] = None
        self.__result["video_url"] = None
        self.__result["comments"] = []

    # Format timestamp menjadi waktu yang terbaca
    def __format_date(self, milisecond: int) -> str:
        try:
            return datetime.fromtimestamp(milisecond).strftime("%Y-%m-%dT%H:%M:%S")
        except:
            return datetime.fromtimestamp(milisecond / 1000).strftime("%Y-%m-%dT%H:%M:%S")

    # Mendapatkan balasan dari sebuah komentar
    def __get_replies(self, commentid: str, aweme_id: str) -> list:
        data, i = [], 0

        while True:
            try:
                # Mengambil balasan dengan TikTok API
                res: Response = requests.get(
                    f'https://www.tiktok.com/api/comment/list/reply/?aid=1988&comment_id={commentid}&item_id={aweme_id}&count=3&cursor={i * 3}'
                )
                res.raise_for_status()  # Pastikan tidak ada error HTTP
                json_res = res.json()

                if not json_res.get('comments'):
                    break

                data += json_res['comments']
                i += 1

            except Exception as e:
                logging.error(f"Error fetching replies for comment {commentid}: {e}")
                break

        return self.__filter_reply_comments(data)

    # Menyaring dan memformat balasan komentar
    def __filter_reply_comments(self, replies: list) -> list:
        filtered_replies = []

        for reply in replies:
            reply_data = {
                "reply_to_nickname": reply.get("reply_to_nickname", "Unknown"),
                "reply_to_reply_id": reply.get("reply_to_reply_id", ""),
                "reply_to_userid": reply.get("reply_to_userid", ""),
                "reply_to_username": reply.get("reply_to_username", ""),
                "text": reply.get("text", ""),
                "likes": reply.get("digg_count", 0),
                "create_time": self.__format_date(reply['create_time']),
                "username": reply['user']['unique_id'],
                "nickname": reply['user']['nickname'],
                "avatar": reply['user']['avatar_thumb']['url_list'][0]
            }

            filtered_replies.append(reply_data)

        return filtered_replies

    # Menyaring dan memformat komentar
    def __filter_comments(self, comments: list, aweme_id: str) -> list:
        new_comments = []

        for comment in comments:
            # Log deskripsi share_info jika tersedia
            if comment['share_info'].get('desc'):
                logging.info(comment['share_info']['desc'])

            new_comment = {
                "username": comment['user']['unique_id'],
                "nickname": comment['user']['nickname'],
                "comment": comment['text'],
                'create_time': self.__format_date(comment['create_time']),
                "likes": comment.get('digg_count', 0),
                "total_reply": comment.get('reply_comment_total', 0),
                "avatar": comment['user']['avatar_thumb']['url_list'][0]
            }

            # Coba ambil balasan jika ada
            try:
                if comment.get('reply_comment_total', 0) > 0:
                    new_comment.update({
                        "replies": self.__get_replies(comment['cid'], aweme_id)
                    })
            except Exception as e:
                logging.error(f"Error fetching replies for comment {comment['cid']}: {e}")

            new_comments.append(new_comment)

        return new_comments

    # Eksekusi proses scraping berdasarkan videoid
    def execute(self, videoid: str, size: int = 0) -> dict:
        logging.info(f'Starting Scrapping for video with id {videoid}...')

        try:
            # Mengambil data komentar dari TikTok API
            res: Response = requests.get(
                f'https://www.tiktok.com/api/comment/list/?aid=1988&aweme_id={videoid}&count=20&cursor={size}'
            )
            res.raise_for_status()  # Pastikan tidak ada error HTTP
            json_res = res.json()

            if json_res.get('status_code', 1) != 0:
                logging.error('Invalid video id')
                return {}

            # Mengambil informasi penting dari hasil scraping
            self.__result['caption'] = json_res['comments'][0]['share_info']['title']
            self.__result['date_now'] = self.__format_date(json_res['extra']['now'])
            self.__result['video_url'] = json_res['comments'][0]['share_info']['url']
            self.__result['comments'] = self.__filter_comments(json_res['comments'], videoid)

        except Exception as e:
            logging.error(f"Error fetching comments for video {videoid}: {e}")
            return {}

        return self.__result

# Testing kode
if __name__ == '__main__':
    comment = Comment()
    result = comment.execute('7151413379964357914')
    if result:
        print(result)  # Menampilkan hasil scraping