import re
import os
import urllib
import random
import json

from slackbot.bot import respond_to
from emojibot.upload import do_upload
from slackbot_settings import num_image_results, append_search_terms
from emojibot.find_images import find


@respond_to('help', re.IGNORECASE)
def help(message):
    help_message=" :wave: :robot_face: Hello! I'm @emjoibot, a slackbot for adding emojis to your slack team _easily_..   Here's how to use me: \n\n"+\
        "  _Basic Commands:_  \n" +\
        "  :point_right:  `@emojibot get <keyword>` -- searches the internets for images, recommends emojis, which you can then add to your slack team.  \n" +\
        "  :point_right:  `@emojibot attach <keyword> <image_name>` -- takes a :camera_with_flash:  you got from `@emojibot get` and makes it an emoji.  \n" +\
        "  _Advanced Commands:_  \n" +\
        "  :point_right:   `@emojibot add <keyword> <url>` -- adds <url> as an an emoji with your desired keyword. \n" +\
        "  :cop:  :point_up: MUST CONFORM TO SLACKS EMOJI REQUIREMENTS: :point_right: `Square images work best. Image can't be larger than 128px in width or height, and must be smaller than 64K in file size.`\n" +\
        " " 
    message.send(help_message)

@respond_to('add (.*) (.*)')
def giveme(message, keyword, url):
    message.reply('uploading.... ')

    upload_emoji(message,keyword,url)


@respond_to('get (.*)')
@respond_to('find (.*)')
def get(message, keyword):
    sanitized_keyword = re.sub(r'\W+', '', keyword)
    attachments = []
    message.reply(':robot_face: finding emojis for keyword `{}` ....'.format(keyword))
    k = 0
    for append in append_search_terms:
        search_term = '{} {}'.format(keyword, append)
        sanitized_search_terms = search_term.replace(' ','_')
        images = find(search_term,num_image_results)
        i = 0
        for image in images:
            i = i + 1
            k = k + 1
            color = "#e6e6e6" if k % 2 else '#59afe1'
            attach_keyword = "{}_{}".format(sanitized_search_terms,i)
            command = "@emojibot attach {} {}".format(sanitized_keyword,attach_keyword)
            title = "{} no. {}".format(search_term,i)
            text = "{}".format(command)
            attachments.append({
                'fallback': text,
                'author_name': title,
                "author_icon": image,
#                'author_link': image,
                'text': text,
                'color': color
            })

            # save to file state
            with open("state.json", "a") as myfile:
                row_json = {
                    'key' : attach_keyword.strip(),
                    'value' : image,
                }
                myfile.write(json.dumps(row_json)+"\n")

    if len(attachments) == 0:
        message.send('Could not find any suitable icons... :sheep: :robot_face:')
    else:
        message.send('Here are your options..')
        message.send_webapi('', json.dumps(attachments))

@respond_to('attach (.*) (.*)')
def get(message, keyword, dict_key):
    message.send(':robot_face: on it. give me a moment to :wizard: :slack: ')
    url = get_val_from_state(dict_key)
    if not url:
        message.reply(':sheep: :robot_face: could not find a recent image for `{}`  ...  did you `@emojibot get` it?'.format(dict_key))
    else:
        upload_emoji(message,keyword,url)

#helper messages

def upload_emoji(message,keyword,url):
    #download file
    #file_path = 'static/' + os.path.basename(url)
    print('downloading file..')
    keyword = keyword.lower()
    file_path = 'static/' + "".join([random.choice('abcdefghijklmnopqrstuvwxyz11234567890') for _ in range(40)])
    urllib.urlretrieve (url, file_path)

    #send to slack
    print('uploading file..')
    errors = []
    try:
        errors = do_upload(file_path,keyword)
        message.react(keyword)
        message.reply('Emoji added! Here is `:{}:` :{}:'.format(keyword,keyword))
    except:
        if len(errors) == 0:
            message.reply('Slack replied with unknown error.')
        else:
            message.reply('Slack replied with the following errors: \n \n {}.'.format("\n".join(errors)))


def get_val_from_state(keyword):
    print('looking at db..')
    with open("state.json", "r") as myfile:
        lines = myfile.readlines()
        for line in lines:
            row = json.loads(line)
            if row['key'] == keyword.strip():
                return row['value']

    return None
 

