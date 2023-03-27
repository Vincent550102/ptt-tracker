import requests
import json
import re
import os
import urllib.parse
with open('trackboards.json') as f:
    config = json.load(f)
    track_boards = config['track_boards']
    bad_article_keyword = config['bad_article_keyword']
    chat_id = config['chat_id']

__import__("dotenv").load_dotenv()


class Crawler():
    def __init__(self):
        self.base_url = "https://www.ptt.cc"
        self.old_articles = dict()
        for track_board in track_boards:
            # self.get_article_url_list(track_board)
            self.old_articles[track_board] = self.get_article_url_list(
                track_board)

        pass

    def get_article_url_list(self, board):
        url = self.base_url + "/bbs/{}/index.html"
        regex_template = rf'(?<=href=")(\/bbs\/{board}\/M\.\d+\.A\.\w+\.html)(?![^>]*?{"|".join(bad_article_keyword)})'
        print(regex_template)
        return [art for art in re.findall(
            regex_template, requests.get(url.format(board)).text.replace("\n", "").replace("\t", ""))]

    def get_article_info_and_send(self, article_url):
        url = self.base_url + article_url
        try:
            req_text = requests.get(url).text
            print(article_url)
            # print(req_text)
            user, board, title, post_time = re.findall(r'"article-meta-value">(.*?)<\/span',
                                                       req_text.replace("\n", "").replace("\t", ""))
            content = re.findall(
                rf'{post_time}<\/span><\/div>([\w\W]*?)<span class="f2">', req_text)[0].strip().strip('--').strip()
            # print(content)
            msg = f"""👀[{board}]{title}
👨{user}
⏰{post_time}
---
{content}
---
<a href="{url}">點此查看詳情...</a>"""
        except:
            msg = f"❌{url} parse error"
        finally:
            requests.get(
                f"https://api.telegram.org/bot{os.getenv('botsecret')}/sendMessage?chat_id={chat_id}&text={urllib.parse.quote(msg)}&parse_mode=HTML")
        pass

    def run(self):
        while True:
            for track_board in track_boards:
                for article_url in self.get_article_url_list(track_board):
                    if article_url not in self.old_articles[track_board]:
                        self.old_articles[track_board].append(article_url)
                        self.get_article_info_and_send(article_url)
            __import__("time").sleep(5)


if __name__ == "__main__":
    crawler = Crawler()
    requests.get(
        f"https://api.telegram.org/bot{os.getenv('botsecret')}/sendMessage?chat_id={chat_id}&text='部屬成功'&parse_mode=HTML")
    crawler.run()
    # print(len(crawler.get_article_url_list("soho")))
    # print(crawler.get_article_info_and_send(
    #     "/bbs/CodeJob/M.1678264319.A.DE5.html"))
