# Slack Emojibot 💩🤖🌈💨

This is a bot that adds custom emojis your slack team; *inline in Slack*. 🤔👌  No more putzing around in your web browser. 💃🎉

Supports *all* of the below via slack. 👇

1. Searching google images. 📷
2. Uploading images to slack's (IMHO hard to find) emoji admin. 🚀

<img src='https://raw.githubusercontent.com/owocki/emojibot/master/examples/howto.gif' />

# Help Menu

<img src='http://bits.owocki.com/0q1i460V1S0n/Image%202016-06-21%20at%2010.02.13%20AM.png' />

# Setup

1. Clone the repo, `git clone https://github.com/owocki/emojibot.git`
2. `cd` into the repo dir, `cd emojibot`
3. (optional) If you use virtualenv, then make a virtualenv.
4. Run `pip install -r requirements.txt`
5. Run `cp slackbot_settings.py.dist slackbot_settings.py`
6. Edit your `slackbot_settings.py`.  Follow instructions in that file for getting the required slack config values.
7. Run `setup.sh`
8. Run the bot!  `python run.py`

```
python run.py
```

## Ubuntu

I run my jobs on Ubuntu.  This may help you if you do too:

```
#Pillow
apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
#libXML
apt-get install libxslt1-dev libxml2

```

# Optional Config

You can further customize your results in `slackbot_settings.py` with the following options:

```
## number of images to return per image search performed
## (useful if your emojibot is clogging up a channel with images)
num_image_results = 5
## append the following terms to searches.  e,g: if user inputs '@emojibot find cop', then a search for 'cop', 'cop emoji', 'cop cartoon' will be performed
## (ALSO useful if your emojibot is clogging up a channel with images)
append_search_terms = ['', 'emoji', 'cartoon']
```

# Feedback

[Tweet the author at @owocki](http://twitter.com/owocki)

<!-- Google Analytics --> 
<img src='https://ga-beacon.appspot.com/UA-1014419-15/owocki/emojibot' style='width:1px; height:1px;' >