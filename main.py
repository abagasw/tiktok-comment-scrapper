import re
import os
import requests
import math

from json import dumps
from comment import Comment, logging

if __name__ == '__main__':
    # Daftar URL yang akan diproses
    url_list = [
        "https://www.tiktok.com/@kevingeraldinguyen/video/7089722160071200027"
    ]

    max_comments = 1000  # Batas maksimal komentar
    max_replies = 1000  # Batas maksimal reply
    output = 'data'  # Folder output default

    for url in url_list:
        # Logika untuk memproses URL seperti sebelumnya
        if "vm.tiktok.com" in url or "vt.tiktok.com" in url:
            videoid = requests.head(url, stream=True, allow_redirects=True, timeout=5).url.split("/")[5].split("?", 1)[0]
        elif re.match("^\d+$", url):
            videoid = url
        else:
            videoid = url.split("/")[5].split("?", 1)[0]
        
        comment: Comment = Comment()

        [json_full, dummy] = [[], {}]
        total_comments = 0  # Untuk melacak jumlah total komentar yang diambil

        for i in range(math.ceil(max_comments / 50)):
            if total_comments >= max_comments:
                break  # Berhenti jika sudah mencapai batas komentar maksimal

            data: dict = comment.execute(videoid, i * 50)

            output_path: str = f'{output}/{videoid}'

            if not os.path.exists(output_path):
                os.makedirs(output_path)

            if data:
                dummy = data
                current_comments = len(data['comments'])
                
                # Jika total komentar + komentar baru melebihi batas, potong komentar yang diambil
                if total_comments + current_comments > max_comments:
                    remaining_comments = max_comments - total_comments
                    json_full += data['comments'][:remaining_comments]
                    total_comments += remaining_comments
                else:
                    json_full += data['comments']
                    total_comments += current_comments

                # Membatasi jumlah balasan untuk setiap komentar
                total_replies_collected = 0  # Untuk melacak jumlah balasan yang dikumpulkan
                for comment_data in json_full:
                    if 'replies' in comment_data:
                        total_replies = len(comment_data['replies'])

                        # Batasi jumlah balasan jika melebihi batas total_replies
                        if total_replies_collected + total_replies > max_replies:
                            remaining_replies = max_replies - total_replies_collected
                            comment_data['replies'] = comment_data['replies'][:remaining_replies]
                            total_replies_collected += remaining_replies
                        else:
                            total_replies_collected += total_replies

                        # Berhenti mengambil lebih banyak balasan jika sudah mencapai batas maksimal
                        if total_replies_collected >= max_replies:
                            break

                with open(f'{output_path}/{i * 50}-{(i + 1) * 50}.json', 'w', encoding='utf-8') as file:
                    file.write(dumps(data, ensure_ascii=False, indent=2))
                    logging.info(f'Output data : {output_path}/{i * 50}-{(i + 1) * 50}.json')

        dummy['comments'] = json_full

        with open(f'{output_path}/full.json', 'w', encoding='utf-8') as file:
            file.write(dumps(dummy, ensure_ascii=False, indent=2))
            logging.info(f'Output data : {output_path}/full.json')

        logging.info(f'Scrapping Success, Output all data for video {videoid}: {output_path}')