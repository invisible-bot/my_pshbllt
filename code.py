import requests as req
from bs4 import BeautifulSoup as Soup
import json
from time import sleep
import concurrent.futures as fu
import os

API = 'o.ADUeCnTDHAZHP32ZOIVrF8EDPVxeSnXy'

RECENT = 'recent.txt'
PREFIX = 'http://www.sinhala24news.com'
NEWS_LINK = 'http://www.sinhala24news.com/2/getnews.php?newsid={}'


def send_notification_via_pushbullet(title, body):
    data_send = {
        "type": "note",
        "title": title,
        "body": body
    }

    ACCESS_TOKEN = API
    resp = req.post('https://api.pushbullet.com/v2/pushes', data=json.dumps(data_send),
                    headers={
                        'Authorization': 'Bearer ' + ACCESS_TOKEN,
                        'Content-Type': 'application/json'
                    })
    if resp.status_code != 200:
        raise Exception('Something wrong')
    else:
        print('complete sending')


def catch_news(news_id):
    r = req.get(NEWS_LINK.format(news_id))
    soup = Soup(r.content, 'html5lib')

    head = soup.find('p', class_='NewsText').text.strip()
    link = PREFIX + soup.a['href'][2:]

    return [head, link]


def _filtering(news):
    if not os.path.isfile(RECENT):
        with open(RECENT, 'w') as ff:
            for each in news:
                ff.write('\n' + each[1])

        return news

    with open(RECENT, 'r') as f:
        old = f.read().splitlines()

    filtered = []
    for each in news:
        if each[1] in old:
            continue
        filtered.append(each)

    with open(RECENT, 'w') as ff:
        for each in news:
            ff.write('\n' + each[1])

    return filtered


def main():
    while True:
        with fu.ThreadPoolExecutor() as e:
            # print('Grabbing News')
            news = list(e.map(catch_news, [x for x in range(10)]))
            # print(f'Got {len(news)} News')

        # print('Filtering')
        filtered = _filtering(news)
        # https://dashboard.heroku.com/new?template=https://github.com/invisible-bot/my_pshbllt
        # print(f'After Filtering {len(news)}')

        # print('Sending each')
        for each in filtered:
            send_notification_via_pushbullet(each[0], each[1])

        # send_notification_via_pushbullet('over', 'Over')
        # print('Sleeping started')
        # from tqdm import tqdm
        # for _ in tqdm(range(10), total=10, unit=' Minutes', desc=' Sleeping'):
        sleep(60 * 60)


if __name__ == '__main__':
    main()
