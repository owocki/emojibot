from slackbot.bot import respond_to
import re
import os
from emojibot.upload import do_upload
import urllib
import random
from slackbot_settings import num_image_results, append_search_terms
from emojibot.find_images import find

@respond_to('help', re.IGNORECASE)
def help(message):
    help_message=" :wave: :robot_face: Hello! I'm @emjoibot, a slackbot for added emojis.   Here's how to use me: \n\n"+\
        "  _Basic Commands:_  \n" +\
        "  :point_right:  `@emojibot get <keyword>` -- searches the internets for images, recommends emojis, which you can then add to your slack team.  \n" +\
        "  _Advanced Commands:_  \n" +\
        "  :point_right:   `@emojibot add <keyword> <url>` -- adds <url> as an an emoji with your desired keyword. \n" +\
        "  :cop:  :point_up: MUST CONFORM TO SLACKS EMOJI REQUIREMENTS: :point_right: `Square images work best. Image can't be larger than 128px in width or height, and must be smaller than 64K in file size.`\n" +\
        " " 
    message.send(help_message)

@respond_to('add (.*) (.*)')
def giveme(message, keyword, url):
    message.reply('uploading.... ')

    #download file
    #file_path = 'static/' + os.path.basename(url)
    file_path = 'static/' + "".join([random.choice('abcdefghijklmnopqrstuvwxyz11234567890') for _ in range(40)])
    urllib.urlretrieve (url, file_path)

    #send to slack
    errors = []
    try:
        errors = do_upload(file_path,keyword)
        message.react(keyword)
        message.reply('Emoji added! Here is {} :{}:'.format(keyword,keyword))
    except:
        if len(errors) == 0:
            message.reply('Slack replied with unknown error.')
        else:
            message.reply('Slack replied with the following errors: \n \n {}.'.format("\n".join(errors)))


@respond_to('get (.*)')
@respond_to('find (.*)')
def get(message, keyword):
    for append in append_search_terms:
        search_term = '{} {}'.format(keyword, append)
        message.reply('__finding `{}` .... __'.format(search_term))
        images = find(search_term,num_image_results)
        i = 0
        for image in images:
            i = i + 1
            message.send('Image # {} : {} '.format(i,image))


