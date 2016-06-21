# Emojibot 💩🤖🌈💨

This is a bot that adds custom emojis your slack team; *inline in Slack*. 🤔👌  No more putzing around in your web browser. 💃🎉

Supports *all* of the below via slack. 👇

1. Searching google images. 📷
2. Uploading images to slack's (IMHO hard to find) emoji admin. 🚀

<img src='https://raw.githubusercontent.com/owocki/emojibot/master/examples/howto.gif' />

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

# Feedback

[Tweet the author at @owocki](http://twitter.com/owocki)

<!-- Google Analytics --> 
<img src='https://ga-beacon.appspot.com/UA-1014419-15/owocki/emojibot' style='width:1px; height:1px;' >