from gifs import ItGifs
import it_config
import pytumblr
import re

# Positive lookbehind + match every char except space + lazy + lookahead insertion to remove the trailing "
REGEX = re.compile('(?<=src=")\S+?(?=")')
client = pytumblr.TumblrRestClient(it_config.TUMBLR_API_KEY)

def get_posts(url, t, offset=0):
    images = []
    while True:
        content = client.posts(url, filter="raw", offset=offset)
        if len(content["posts"]) == 0:
            break
        offset += 20
        parse_posts(content, t)
    return images

def parse_posts(posts, t):
    images = []
    for post in posts["posts"]:
        if post.get("body") is None:
            print post
            continue
        regex_res = REGEX.search(post["body"])
        title = post["title"]
        source = post["post_url"]
        #tags = post["tags"] # sometimes we can have some surprises...
        if regex_res is None:
            print post
            continue
        image_url = regex_res.group(0)
        t.add_image(image_url, source, title)
    return images

if __name__ == '__main__':
    tumblrs = ['lesjoiesdusysadmin.tumblr.com', 'devopsreactions.tumblr.com', 'lesjoiesducode.fr',
               'lifeofasoftwareengineer.tumblr.com', 'frontenddevreactions.tumblr.com']
    t = ItGifs()
    for tumblr in tumblrs:
        print tumblr
        get_posts(tumblr, t)
    t.close()
