# Emojibot

This is a bot that adds custom emojis to slack _via a slack command, NOT in the admin_.

<img src='http://bits.owocki.com/1o1U2i2e1X2Z/Screen%20Recording%202016-06-21%20at%2006.48%20AM.gif' />

# Setup

1. Clone the repo, `git clone https://github.com/owocki/emojibot.git`
2. `cd` into the repo dir, `cd emojibot`
3. (optional) If you use virtualenv, then make a virtualenv.
4. Run `pip install -r requirements.txt`
5. Run `cp slackbot_settings.py.dist slackbot_settings.py`
6. Edit your `slackbot_settings.py`.  Follow instructions in that file for getting the required slack config values.
7. Run the bot! 

```
python run.py
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


<!-- Google Analytics --> 
<img src='https://ga-beacon.appspot.com/UA-1014419-15/owocki/emojibot' style='width:1px; height:1px;' >