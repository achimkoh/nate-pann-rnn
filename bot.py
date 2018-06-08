import random, re
from os import listdir
from os.path import isfile, join

# take recently generated text
# pick latest file
recenttitle = sorted([f for f in listdir('./generated') if f[:6] == 'title-' and f[-4:] == '.txt'])[-1]
recentbody = sorted([f for f in listdir('./generated') if f[:5] == 'body-' and f[-4:] == '.txt'])[-1]

with open('./generated/'+recenttitle, 'r') as f:
    title_raw = f.read()
with open('./generated/'+recentbody, 'r') as f:
    body_raw = f.read()

# stringify current date
today = '.'.join(recenttitle.split('-')[1:4]) + ' ' + ':'.join(recenttitle[:-4].split('-')[4:6])
today_hyphened = '-'.join(recenttitle.split('-')[1:4]) + '-' + '-'.join(recenttitle[:-4].split('-')[4:6])

# split at period or newline and select if longer than 10 characters
title = random.choice([sentence for sentence in re.split('\. |\n', title_raw) if len(sentence) > 10])
print(title)

# find last period and discard everything after; convert \n to <br>, for html
body = body_raw[:[periods.start() for periods in re.finditer('\.', body_raw)][-1]+1].replace('\n', '<br>')
print(body)

# fill in template
with open('template.html', 'r') as f:
    template = f.read()

content = {'title': title, 'body': body, 'date': today,
           'views': "{:,}".format(random.randint(-10000,10000)),
           'upvotes': "{:,}".format(random.randint(0,1000)),
           'downvotes': "{:,}".format(random.randint(0,100)),
           'replies': "{:,}".format(random.randint(-500,500))}

with open('www/today.html', 'w') as f:
    f.write(template.format(**content))

# attempt to collect memory
del recenttitle, title_original, title_raw, recentbody, body_raw, body

# render screenshots
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from PIL import Image
from io import BytesIO
from time import sleep

opts = FirefoxOptions()
opts.add_argument("--headless")
driver = webdriver.Firefox(firefox_options=opts)

width, height = 410, 684
driver.set_window_size(width, height)
driver.get('http://localhost:8000/today.html')
driver.implicitly_wait(5)
sleep(10)

# driver.take_screenshot('test.png')
document_height = driver.execute_script("return document.body.scrollHeight")
num_screenshots = int(document_height / 600) + 1
print(document_height, num_screenshots)

for i in range(num_screenshots):
    if (i != 0 and i == num_screenshots-1): # crop last image for no overlap with previous one
        png = driver.get_screenshot_as_png()
        im = Image.open(BytesIO(png)) # uses Pillow library to open image in memory
        left = 0
        top = document_height % 600
        right = 400
        bottom = 600
        im = im.crop((left, top, right, bottom)) # defines crop points
        im.save('./generated/screenshot-{}-{}.png'.format(today_hyphened, i+1)) # saves new cropped image
    else:
        driver.save_screenshot('./generated/screenshot-{}-{}.png'.format(today_hyphened, i+1))
        driver.execute_script('scrollBy({},{})'.format(0, 600))

screenshots = [f for f in sorted(listdir('./generated')) 
               if f.split('-')[0:6] == ['screenshot']+today_hyphened.split('-') 
               and f.split('.')[-1] == 'png']
print(screenshots)
driver.close()

# connect to API
import tweepy
consumer_key = 'YOUR_TWITTER_APP_CONSUMER_KEY'
consumer_secret = 'YOUR_TWITTER_APP_CONSUMER_SECRET'
access_token = 'YOUR_TWITTER_APP_ACCESS_TOKEN'
access_token_secret = 'YOUR_TWITTER_APP_ACCESS_TOKEN_SECRET'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

def update_today():
    media_ids = [api.media_upload('./generated/'+img).media_id_string for img in screenshots[:4]]
    api.update_status(media_ids=media_ids, status=title)

# do the thing
while True:
    try:
        update_today()
        print('status updated')
        break
    except:
        update_today()
