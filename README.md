# [Nate Pann RNN, a twitter bot](https://twitter.com/pann_rnn)

## Project description

[Nate Pann](http://pann.nate.com) is a popular internet forum in South Korea. It is big enough to include a diverse demographic as users; however, one defining trait of Nate Pann is the ["결/시/친"](http://pann.nate.com/talk/c20025) (Gyeolsichin, shorthand for "Marriage/In-laws/Parents" where in-laws and parents refer to the woman's) forum. Gyeolsichin has an established status as a place where women in distress caused by diverse elements of the patriarchic Korean society come to rant. This characteristic makes it unique compared to other public online communities of comparable sizes, many of which display male-dominant voices. 

This project is an attempt to explore the collective memories embodied in online communities. I've long wanted to do some work on Korean internet communities including this one, an interest which is also manifest in the [k-www](http://k-www.kr/en) project. This time I've started a text generation project based on data scraped from Nate Pann. I scraped most of Nate Pann's ["Best Articles"](http://pann.nate.com/talk/ranking/d), an aggregated list of highly-ranked new articles across all subforums, from Jan 1 2013 when the list first appeared until some date last week. Among the 169,795 articles, 18,884 belong to Gyeolsichin.

I set up Insik Kim's [kor-char-rnn-tensorflow](https://github.com/insikk/kor-char-rnn-tensorflow) on a cloud server with a Tesla P40 GPU. An exploratory training of an LSTM model (hidden=700, layer=3, seq=100) with titles (1MB) took about 10hrs (reaching about 0.5 loss at epoch 1000); for the main content (70MB) it seems closer to 150hrs for 100 epochs. There must be more efficient and computationally sophisticated ways to do this but I've decided to give it a go since I have some free credit to spend.

Using the trained models (early-epoch model for main content), I set up a script that generates a title and a content; for titles, filter out sentences that come directly from the training set; parses the generated text so each one begins and ends with a more or less complete sentence; generates an html file styled to look similar to Nate Pann, but with a different logo that signals its fakeness; exports screenshots, which is a common way these postings are shared on Twitter; and runs a bot that posts a tweet everyday with said images attached.

The result is the [Nate Pann RNN](https://twitter.com/pann_rnn) Twitter bot, and I'm liking the results so far. The main text generation is rather incoherent, but I expect to see better results once the training on content is complete.

## Info

### Text generation

- Requires [tensorflow](https://www.tensorflow.org)
- You need to download model files from [this link](http://restapi.fs.ncloud.com/nate-pann-rnn-models/nate-pann-rnn-models.tar.gz), and extract the archive inside this directory. 
- Subdirectory paths will be `./save/gsc-body` and `./save/gsc-title`
- running `sample-title.py` and `sample-body.py` will generate text from respective model files

### Twitter bot

- Requires [selenium](http://selenium-python.readthedocs.io/), [Pillow](https://pillow.readthedocs.io/) for screenshot rendering and [Tweepy](http://tweepy.readthedocs.io/) for twitter access
- You need to (optionally) create a new Twitter account for the bot, [create a Twitter app](https://apps.twitter.com/), go in the settings and create an access token. The secret credentials are used by `bot.py`.
- `run_pannbot.sh` will run text generation, generate a screenshot using the text, and post a tweet to the account in question

### Scraper

- `scraper.py` shows how I scraped data from Nate Pann. It's a very crude script with lots of manual cleaning, shared here for reference only. 
- Not sharing raw data because copyright