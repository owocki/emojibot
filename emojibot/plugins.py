import re
import os
import urllib
import random
import json
import PIL
import hashlib
from PIL import Image, ImageFont, ImageDraw

from slackbot.bot import respond_to
from emojibot.upload import do_upload
from slackbot_settings import append_search_terms, fontname, num_image_columns, num_image_rows
from emojibot.find_images import find


@respond_to('help', re.IGNORECASE)
def help(message):
    help_message=" :wave: :robot_face: Hello! I'm @emojoibot, a slackbot for adding emojis to your slack team _easily_..   Here's how to use me: \n\n"+\
        "  _Basic Commands:_  \n" +\
        "  :point_right:  `@emojibot get <keyword>` -- searches the internets for images, recommends emojis, which you can then add to your slack team.  \n" +\
        "  :point_right:  `@emojibot attach <keyword> <image_name>` -- takes a :camera_with_flash:  you got from `@emojibot get` and makes it an emoji.  \n" +\
        "  _Advanced Commands:_  \n" +\
        "  :point_right:   `@emojibot add <keyword> <url>` -- adds <url> as an an emoji with your desired keyword. \n" +\
        "  :cop:  :point_up: MUST CONFORM TO SLACKS EMOJI REQUIREMENTS: :point_right: `Square images work best. Image can't be larger than 128px in width or height, and must be smaller than 64K in file size.`\n" +\
        "   :paperclip: More details @ `http://github.com/owocki/emojibot` " 
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
        search_term = '{} {}'.format(keyword, append).strip()
        sanitized_search_terms = search_term.replace(' ','_')
        # column x row grid, with 1.2 buffer for dupe images, divided by number of searches we'll do
        num_images = int((num_image_columns * num_image_rows * 1.2) / len(append_search_terms) ) 
        images = find(search_term,num_images)
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
                'author_link': image,
                'text': text,
                'color': color
            })


    if len(attachments) == 0:
        message.send('Could not find any suitable icons... :sheep: :robot_face:')
    else:
        file_path, rows, comment = gen_master_image(attachments,keyword)
        message.channel.upload_file('Emoji options', file_path, comment)

        # save to file state
        with open("state.json", "a") as myfile:
            for row in rows:
                row_json = {
                    'key' : row['key'],
                    'value' : row['value'],
                }
                myfile.write(json.dumps(row_json)+"\n")



@respond_to('attach (.*) (.*)')
def get(message, keyword, dict_key):
    message.send(':robot_face: on it. give me a moment to :ship::two: :slack: ')
    url = get_val_from_state(dict_key)
    if not url:
        message.reply(':sheep: :robot_face: could not find a recent image for `{}`  ...  did you `@emojibot get` it?'.format(dict_key))
    else:
        upload_emoji(message,keyword,url)

#helper messages

def gen_master_image(attachments,keyword):

    #config
    font = ImageFont.truetype(fontname, 12)
    bottom_font = ImageFont.truetype(fontname, 16)
    inner_image_size_width = 50
    inner_image_size_height = 50
    buffer_size_height = 20
    buffer_size_width = 5
    num_rows = num_image_rows
    num_columns = num_image_columns
    master_image_size_width = ((inner_image_size_width + buffer_size_width) * num_columns )
    master_image_size_height = ((inner_image_size_height + buffer_size_height) * num_rows )

    images = []
    hashes = []
    for attachment in attachments:
        url = attachment['author_icon']
        command = attachment['text']

        #get file from remote
        file_path = 'static/' + "".join([random.choice('abcdefghijklmnopqrstuvwxyz11234567890') for _ in range(40)])
        urllib.urlretrieve (url, file_path)
        im = Image.open(file_path)

        #check for uniqueness, only add if unique
        image_file = open(file_path).read()
        _hash = hashlib.md5(image_file).hexdigest()
        if _hash not in hashes:
            images.append((im,url))
            hashes.append(_hash)
    images.reverse()
    master_images = images

    #create new image
    new_im = Image.new('RGB', (master_image_size_width,master_image_size_height), "white")

    #Iterate through a 4 by 4 grid with 100 spacing, to place my image
    rows = []
    for row in range(0,num_rows):
        for column in range(0,num_columns):
            #paste the image at location i,j:
            try:
                im, url = images.pop()
                width, height = im.size
                if width < inner_image_size_width:
                    im = im.resize((inner_image_size_width, inner_image_size_height),resample=PIL.Image.ANTIALIAS)
                x_pos = column * (inner_image_size_width + buffer_size_width)
                y_pos = row * (inner_image_size_height + buffer_size_height)
                #resize opened image 
                im.thumbnail((inner_image_size_width,inner_image_size_height))
                new_im.paste(im, (x_pos,y_pos))
                draw = ImageDraw.Draw(new_im)
                img_key = "{}{}x{}".format(keyword[0:3],row,column)
                draw.text((x_pos, y_pos + inner_image_size_height),img_key,"black",font=font)
                rows.append({'key':img_key,'value': url})
            except Exception as e:
                print(e)
                images = master_images

    comment = "To attach an emoji, use command `@emojibot attach {} [IMG_REFERENCE]`".format(keyword)
    draw.text((0, y_pos + ((inner_image_size_height + buffer_size_height)) ),comment,"black",font=bottom_font)
    file_path = 'static/' + "".join([random.choice('abcdefghijklmnopqrstuvwxyz11234567890') for _ in range(40)]) + ".png"
    new_im.save(file_path)
    return file_path, rows, comment

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
        intros = ['Here is', 'Allow me to introduce', 'Please welcome', 'Say hai to', 'Hot new thang']
        intro = random.choice(intros)
        message.reply('Emoji added! {} -> `:{}:` :{}:'.format(intro, keyword,keyword))
    except:
        if len(errors) == 0:
            message.reply('Slack replied with unknown error.')
        else:
            message.reply('Slack replied with the following errors: \n \n {}.'.format("\n".join(errors)))


def get_val_from_state(keyword):
    print('looking at db..')
    with open("state.json", "r") as myfile:
        lines = myfile.readlines()
        lines.reverse()
        for line in lines:
            row = json.loads(line)
            if row['key'] == keyword.strip():
                return row['value']

    return None
 

