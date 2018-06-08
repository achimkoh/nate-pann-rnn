# TODO: refactor (csv export, better error handling, etc)

import requests, datetime, os, re, json
from bs4 import BeautifulSoup as bs
path_dir = os.path.dirname("./halloffame/")

errors = []

def get_halloffame_list(d):
    with open(path_dir + '/{}.txt'.format(d.strftime("%Y%m%d")), 'w') as f:
        try:
            r = requests.get('http://pann.nate.com/talk/ranking/d?stdt={}'.format(d.strftime("%Y%m%d")), timeout=5)
            soup = bs(r.text, "html.parser")
            dt_list = soup.find_all("dt")
            for url in [dt.find_all("a")[0]["href"] for dt in dt_list if dt.find_all("a", {"onclick":"vndr('BDW03');"})]:
                f.write("%s\n" % url)
            r = requests.get('http://pann.nate.com/talk/ranking/d?stdt={}&amp;page=2'.format(d.strftime("%Y%m%d")), timeout=5)
            soup = bs(r.text)
            dt_list = soup.find_all("dt")
            for url in [dt.find_all("a")[0]["href"] for dt in dt_list if dt.find_all("a", {"onclick":"vndr('BDW03');"})]:
                f.write("%s\n" % url)
            print(d, 'ok')
        except:
            f.write('error')
            errors.append(d)
            print(d, 'error')
d = datetime.date(2013,1,1)

# repeat for each day until today
while d != datetime.date.today():
    get_halloffame_list(d)
    d += datetime.timedelta(days=1)
### if len(errors) &gt; 0, repeat below until there is no error ###

errors2, errors = errors, []

for d in errors2:
    get_halloffame_list(d)
files = [os.path.join(path_dir, f) for f in os.listdir(path_dir) if os.path.isfile(os.path.join(path_dir, f))]
urls = []

for filepath in files:
    with open(filepath, 'r') as f:
        for url in [line.strip() for line in f.readlines()]:
            urls.append(url)

len(files), len(urls) # 1618, 161665

# 네이트 판 수집 목록

# 카테고리
# 제목
# 조회수
# 작성일시
# 작성자
# 본문 텍스트 및 하이퍼링크: article_text
# 이미지 url: article_text에 포함, [img: URL] 형식
# 추천/반대
# 태그
# 리플 개수

# 베플 본문
# 베플 이미지 등 미디어 url
# 베플 작성자
# 베플 젠더?
# 베플 작성일
# 베플 추천/비추
# 베플의 답글 개수

# 기타 미디어? iframe 
# "이어지는 판"
def get_talk(url):
    r = requests.get(url, timeout=5)
    soup = bs(r.text, "html5lib")
    if b'alert' in r.content[:20]:
        return 'missing'
    
    # body text, links, images
    article = soup.find("div", {"id":"contentArea"})
    for img in article.find_all('img'):
        try:
            img.replaceWith('[img {}]'.format(img.attrs['src']))
        except KeyError:
            try:
                img.replaceWith(img.attrs['alt'])
            except:
                img.replaceWith('[img]')
            # img src
    for iframe in article.find_all('iframe'):
        try:
            iframe.replaceWith('[iframe {} {}]'.format(iframe.attrs['swaf:cywrite:default_thumb_img'], iframe.text))
        except:
            try:
                iframe.replaceWith('[iframe {} {}]'.format(iframe.attrs['src'], iframe.text))
            except:
                iframe.replaceWith('[iframe]')
    for a in article.find_all('a'):
        try:
            a.replaceWith('{} {}'.format(a.attrs['href'], a.text))
        except:
            a.replaceWith(a.text)
    article_text = re.sub(r'\n+',r'\n',article.get_text('\n').strip().replace(u'\xa0', u' ')) # reduce redundant spaces

    # metadata
    info = soup.find("div", {"class":"info"})

    # todo: turn into json
    article_author = info.find(True, {"class":"writer"}).text.strip() 
    article_title = soup.find("div", {"class":"post-tit-info"}).h4.text
    article_date = info.find(True, {"class":"date"}).text.strip() 
    article_hits = int(''.join(info.find(True, {"class":"count"}).text[2:].split(','))) # hits are saved as int
    article_comments = int(''.join(soup.find("div",{"class":"cmt_tit"}).strong.text.split(','))) 
    article_ups = int(''.join(soup.find_all("div", {"class":"up"})[-1].find("span",{"class":"count"}).text.split(','))) 
    article_downs = int(''.join(soup.find_all("div", {"class":"down"})[-1].find("span",{"class":"count"}).text.split(','))) 
    # category: discard first item since it is always "talk", which is the data source. also, retain only text.
    article_categories = ';'.join([a.text for a in soup.find("span", {"class":"location"}).find_all('a')[1:]])
    article_tags = ';'.join([a.text for a in soup.find("dl", {"class":"tagbox"}).find_all('a')])
    
    talk = {'text':article_text, 'title':article_title, 'author':article_author, 'date':article_date,
            'hits':article_hits, 'comments':article_comments, 'up': article_ups, 'down':article_downs,
            'tags':article_tags, 'category':article_categories, 'type':'talk', 'id':url.split('/')[-1]}
    
    # "best" comments
    if soup.find("div",{"class":"cmt_best"}): # check if document has beples
        cmt_best = soup.find_all("div",{"class":"cmt_best"})[-1]
        beples = []
        for beple in cmt_best.find_all('dl',{"class":"cmt_item"}):
            beple_author = beple.find("span",{"class":"nameui"}).text
            try:
                beple_author += "${}".format(beple.find("span",{"class":"gender"}).text) # some comments show gender of commenter
            except:
                True
            beple_ups = int(''.join(beple.find("dd",{"class":"n_good"}).text.split(',')))
            beple_downs = int(''.join(beple.find("dd",{"class":"n_bad"}).text.split(',')))
            beple_comments = int(''.join(beple.find("a",{"class":"cmtsum"}).em.text.split(',')))
            beple_date = beple.find("i").text

            usertxt = beple.find("dd",{"class":"usertxt"})
            for img in usertxt.find_all('img', {"alt":"사용자첨부이미지"}):
                img.replaceWith('[img {}]'.format(img.attrs['src']))
            beple_text = usertxt.text.strip()

            beples.append({'text':beple_text, 'author':beple_author, 'date':beple_date,
                           'comments':beple_comments, 'up':beple_ups, 'down':beple_downs, 'type':'beple'})
        talk['beples'] = beples
        
    # continue_pann (postings are related within a series)
    if soup.find("div",{"class":"continue_pann"}):
        series = []
        for related_url in [a.attrs['href'] for a in soup.find("div",{"class":"continue_pann"}).find_all('a', {"class":"seriesItem"})]:
            if '.com/b' in related_url:
                related_url = '.com/talk/'.join(related_url.split('.com/b'))
            if not related_url in urls and not related_url in urls_to_revisit:
#                 urls.append(related_url)
                urls_to_revisit.append(related_url)
            series.append(related_url.split('/')[-1])
        talk['series'] = series

    return talk 
# scrape_errors = []

# for url in urls:
#     with open(data_dir+'/{}.json'.format(url.split('/')[-1]), 'w') as f:
#         try:
#             json.dump(get_talk(url), f, ensure_ascii=False)
#         except:
#             scrape_errors.append(url)
#             f.write('error at {}'.format(url))
#             print('error at {}: {}'.format(urls.index(url), url))
data_dir = os.path.dirname("./data/")
talks_data = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if '.json' in f]
talks = []

for filepath in talks_data:
    with open(filepath, 'r') as f:
        try:
            talks.append(json.load(f))
        except json.JSONDecodeError:
            with open(filepath, 'r') as f:
                talks.append(f.readline())
            
len(talks), len(talks_data)
urls_to_revisit = []

for i in range(len(talks)):
    if type(talks[i]) == str:
        try:
            urls_to_revisit.append(talks[i].split()[-1])
        except:
            print(i, talks[i], talks_data[i])
        
len(urls_to_revisit)
urls_to_revisit.append('http://pann.nate.com/talk/317449810')
urls_to_revisit.append('http://pann.nate.com/talk/317450563')
urls_to_revisit.append('http://pann.nate.com/talk/317981595')
urls_to_revisit.append('http://pann.nate.com/talk/318075989')
urls_to_revisit.append('http://pann.nate.com/talk/321884623')
urls_to_revisit.append('http://pann.nate.com/talk/322235446')
urls_to_revisit.append('http://pann.nate.com/talk/318656211')
scrape_errors = []

for url in urls_to_revisit:
    with open(data_dir+'/{}.json'.format(url.split('/')[-1]), 'w') as f:
        try:
            json.dump(get_talk(url), f, ensure_ascii=False)
        except:
            scrape_errors.append(url)
            f.write('error at {}'.format(url))
            print('error at {}: {}'.format(urls_to_revisit.index(url), url))