# Start chrome like so:
# open /Users/calebhattingh/Applications/Chromium.app --args -remote-debugging-port=6001
import time
import json
from pprint import pprint, pformat
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor
import urllib.request
import os.path
from uuid import uuid4 as uid

from chromote import Chromote
from slugify import slugify


__version__ = '0.0.0'


"""
More search examples:

https://www.google.com/search?biw=958&bih=911&tbm=isch&sa=1&q=guitarist&oq=&gs_l=

https://www.google.com.au/search?biw=958&bih=911&tbm=isch&tbs=isz:l&q=guitarist&oq=&gs_l=&gws_rd=cr&ei=LoAcV_jQIY6F0QSBwZ7YDw

http://www.google.com/search?q=%22michael+jackson%22&tbm=isch&tbs=ic:color,isz:lt,islt:4mp,itp:face,isg:to

"""


def enable_jquery(tab):
    code = ["var jq = document.createElement('script');",
            'jq.src = "https://code.jquery.com/jquery-latest.min.js";',
            "document.getElementsByTagName('head')[0].appendChild(jq);",
            "jQuery.noConflict();"]
    for line in code:
        print()
        print(line)
        out = tab.evaluate(line)
        print(out)
        time.sleep(1)



def search(port, query, maxnum=None):
    """
    Large images: tbs=isz:l
    Medium images: tbs=isz:m
    Icon sized images: tba=isz:i
    Image size larger than 400×300: tbs=isz:lt,islt:qsvga
    Image size larger than 640×480: tbs=isz:lt,islt:vga
    Image size larger than 800×600: tbs=isz:lt,islt:svga
    Image size larger than 1024×768: tbs=isz:lt,islt:xga
    Image size larger than 1600×1200: tbs=isz:lt,islt:2mp
    Image size larger than 2272×1704: tbs=isz:lt,islt:4mp
    Image sized exactly 1000×1000: tbs=isz:ex,iszw:1000,iszh:1000
    Images in full color: tbs=ic:color
    Images in black and white: tbs=ic:gray
    Images that are red: tbs=ic:specific,isc:red [orange, yellow, green, teal, blue, purple, pink, white, gray, black, brown]
    Image type Face: tbs=itp:face
    Image type Photo: tbs=itp:photo
    Image type Clipart: tbs=itp:clipart
    Image type Line drawing: tbs=itp:lineart
    Group images by subject: tbs=isg:to
    Show image sizes in search results: tbs=imgo:1
    """
    chrome = Chromote(port=port)
    tab = chrome.tabs[0]
    flags = dict(
            tbm='isch',
            tbs='ic:color,isz:l',
            )
    tmpl = 'http://www.google.com/search?q={query}&{flags}'
    search_url = tmpl.format(
            query='+'.join(query.split(' ')),
            flags='&'.join([k+'='+v for k, v in flags.items()])
            )
    print('Search url:', search_url)
    print(tab.set_url(search_url))
    time.sleep(1)
    # tab.reload()
    time.sleep(1)
    for i in range(5):
        tab.evaluate('window.scrollTo(0,document.body.scrollHeight);')
        print('scrolled a bit...')
        time.sleep(1)

    time.sleep(10)
    code = '''
            Array.prototype.slice.call(
                document.querySelectorAll("a.rg_l")
            ).map(
                function(elem) {
                    return elem.href;
                }
            ).join(",");
            '''
    out = tab.evaluate(code.replace('\n', ''))
    print(len(out))
    time.sleep(1)
    print(len(out))
    pprint(out)
    urls = json.loads(out)['result']['result']['value']
    pprint(urls)
    imgurls = []
    for url in urls.split(',')[:maxnum]:
        try:
            parsed_url = urlparse(url)
            if not parsed_url.path:
                continue
            # print(parsed_url)
            opts = parse_qs(parsed_url.query)
            # print(opts)
            imgurls.append(dict(
                url=opts['imgurl'][0],
                height=opts['h'],
                width=opts['w']))
        except Exception as e:
            # print('Problem with {}: {}'.format(url, e))
            pass


    def dl(url, folder):
        try:
            path = urlparse(url).path
            url_fname = os.path.split(path)[-1]
            fname = uid().hex[:8] + '-' + url_fname
            with urllib.request.urlopen(url, timeout=10) as u:
                data = u.read()
            with open(os.path.join(folder, fname), 'wb') as f:
                f.write(data)
            return True
        except Exception as e:
            print('Problem with {}: {}'.format(url, e))
            return False

    folder = slugify(query) + '-' + uid().hex[:8]
    if not os.path.exists(folder):
        os.mkdir(folder)

    with ThreadPoolExecutor(max_workers=8) as exe:
        jobs = [exe.submit(dl, x['url'], folder) for x in imgurls]
        result = [j.result() for j in jobs]

    return imgurls, tab


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Automate img search')
    parser.add_argument('-p', '--port', type=int, default=6001)
    parser.add_argument('-q', '--query', type=str)
    parser.add_argument('--max', type=int, default=None)
    args = parser.parse_args()
    print(args.query)
    out, tab = search(args.port, args.query, args.max)


if __name__ == '__main__':
    main()
