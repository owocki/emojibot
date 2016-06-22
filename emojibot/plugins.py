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
from slackbot_settings import append_search_terms, fontname, bot_name,small_num_image_rows, small_num_image_columns, large_num_image_rows, large_num_image_columns
from emojibot.find_images import find

garbage_collector = []

@respond_to('help', re.IGNORECASE)
def help(message):
    try:
        print('got command help')
        help_message=" :wave: :robot_face: Hello! I'm @"+bot_name+", a slackbot for adding emojis to your slack team _easily_..   Here's how I work: \n\n"+\
            "  _Basic Commands:_  \n" +\
            "  -  `@"+bot_name+" <keyword>` -- searches the internets for images, recommends emojis, which you can then add to your slack team.  \n" +\
            "  -  `@"+bot_name+" more <keyword>` -- same as above, but shows more results.  \n" +\
            "  -  `@"+bot_name+" attach <keyword> <image_name>` -- takes a :camera_with_flash:  you got from above commands, & makes it an emoji.  \n" +\
            "  -  `@"+bot_name+" fastadd <keyword>` -- adds first image found as an emoji for keyword.  \n" +\
            "  _Advanced Commands:_  \n" +\
            "  -   `@"+bot_name+" add <keyword> <url>` -- adds <url> as an an emoji with your desired keyword. Automatically resizes your :camera_with_flash: to 125px x 125px. \n" +\
            "   :paperclip: More details @ `http://github.com/owocki/emojibot` " 
        message.send(help_message)
    except Exception as e:
        handle_exception(message,e)

@respond_to('add (.*) (.*)')
@respond_to('upload (.*) (.*)')
def add_to_slack(message, keyword, url):
    try:
        if message.body['text'].split(' ')[0] == 'fastadd':
            return

        print('got command upload')

        #download image, make sure it is constrained to slacks requirements
        print('- resziing')
        file_path = download_file(url)
        im = Image.open(file_path)
        im = im.resize((125, 125),resample=PIL.Image.ANTIALIAS)
        im.save(file_path)

        #upload to slack
        print('- uploading')
        sanitized_keyword = re.sub(r'\W+', '', keyword)
        upload_emoji(message,sanitized_keyword,url=None,file_path=file_path)

        #cleanup
        print('- gc')
        run_garbage_collector()
    except Exception as e:
        handle_exception(message,e)

@respond_to('fastadd (.*)')
def fastadd(message, keyword):
    try:
        print('got command fastadd')

        #get an image
        print('- searching')
        images = find(keyword,10)
        if len(images) == 0:
            message.send('Could not find any suitable icons... :sheep: :robot_face:')
            return
        url = images[0]

        #download image, make sure it is constrained to slacks requirements
        print('- resziing')
        file_path = download_file(url)
        im = Image.open(file_path)
        im = im.resize((125, 125),resample=PIL.Image.ANTIALIAS)
        im.save(file_path)

        #upload to slack
        print('- uploading')
        sanitized_keyword = re.sub(r'\W+', '', keyword)
        upload_emoji(message,sanitized_keyword,url=None,file_path=file_path)

        #cleanup
        print('- gc')
        run_garbage_collector()
    except Exception as e:
        handle_exception(message,e)


@respond_to('(.*)')
def get(message, keyword):
    try:
        print('catchall {}'.format(keyword))
        words = keyword.split(' ')
        large = False
        if not len(words):
            return
        elif words[0] in ['upload','attach','add','help', 'fastadd']:
            return
        elif words[0] in ['get','find']:
            words = words[1:]
            keyword = " ".join(words)
        elif words[0] in ['more','options']:
            words = words[1:]
            keyword = " ".join(words)
            large = True

        print('got command get {}'.format(keyword))

        #config
        if not large:
            num_rows = small_num_image_rows
            num_columns = small_num_image_columns
        else:
            num_rows = large_num_image_rows
            num_columns = large_num_image_columns
        sanitized_keyword = re.sub(r'\W+', '', keyword)
        attachments = []
        k = 0

        print('- searching')
        for append in append_search_terms:
            search_term = '{} {}'.format(keyword, append).strip()
            sanitized_search_terms = search_term.replace(' ','_')
            print(' - searching {}'.format(search_term))
            # column x row grid, with 1.2 buffer for dupe images, divided by number of searches we'll do
            num_images = int((num_columns * num_rows * 1.2) / len(append_search_terms) ) 
            images = find(search_term,num_images)
            print(' - got {} images'.format(len(images)))
            i = 0
            for image in images:
                i = i + 1
                k = k + 1
                color = "#e6e6e6" if k % 2 else '#59afe1'
                attach_keyword = "{}_{}".format(sanitized_search_terms,i)
                command = "@"+bot_name+" attach {} {}".format(sanitized_keyword,attach_keyword)
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


        print('- validating')
        if len(attachments) == 0:
            message.send('Could not find any suitable icons... :sheep: :robot_face:')
        else:
            print(' - generating {} master image'.format(keyword))
            file_path, rows, comment = gen_master_image(attachments,keyword,num_rows,num_columns,not large)
            message.channel.upload_file('Emoji options', file_path, comment)

            # save to file state
            with open("state.json", "a") as myfile:
                for row in rows:
                    row_json = {
                        'key' : row['key'],
                        'value' : row['value'],
                    }
                    myfile.write(json.dumps(row_json)+"\n")

        run_garbage_collector()
    except Exception as e:
        handle_exception(message,e)


@respond_to('attach (.*) (.*)')
def attach(message, keyword, dict_key):
    try:
        print('got command attach')
        url = get_val_from_state(dict_key)
        if not url:
            message.reply(':sheep: :robot_face: could not find a recent image for `{}`  ...  did you `@'+bot_name+' get` it?'.format(dict_key))
        else:
            sanitized_keyword = re.sub(r'\W+', '', keyword)
            upload_emoji(message,sanitized_keyword,url)
        run_garbage_collector()
    except Exception as e:
        handle_exception(message,e)

###################################################
#helper messages
###################################################

def gen_master_image(attachments,keyword,num_rows,num_columns,enable_more):

    #config
    font = ImageFont.truetype(fontname, 12)
    bottom_font = ImageFont.truetype(fontname, 16)
    inner_image_size_width = 50
    inner_image_size_height = 50
    buffer_size_height = 20
    buffer_size_width = 5
    master_image_size_width = ((inner_image_size_width + buffer_size_width) * num_columns )
    master_image_size_height = ((inner_image_size_height + buffer_size_height) * num_rows )

    images = []
    hashes = []
    print(' -- gen_master_image:downloading.. ')
    for attachment in attachments:
        url = attachment['author_icon']
        command = attachment['text']

        #get file from remote
        file_path = download_file(url)
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
    print(' -- gen_master_image:building image.. ')
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
                print(" --(e) -- "+str(e))
                images = master_images

    comment = "To _attach an emoji_, use command `@"+bot_name+" attach {} IMG_REF`".format(keyword) + \
    ("\nTo _see more results_, use command `@"+bot_name+" more {}`".format(keyword) if enable_more else "")
    draw.text((0, y_pos + ((inner_image_size_height + buffer_size_height)) ),comment,"black",font=bottom_font)
    file_path = gen_file_path()
    new_im.save(file_path)
    garbage_collector.append(file_path)

    return file_path, rows, comment

def gen_file_path():
    file_path = 'static/' + "".join([random.choice('abcdefghijklmnopqrstuvwxyz11234567890') for _ in range(40)]) + ".png"
    return file_path

def run_garbage_collector():
    try:
        while True:
            file_path = garbage_collector.pop()
            os.remove(file_path)
    except:
        pass;



def download_file(url):
    file_path = gen_file_path()
    urllib.urlretrieve (url, file_path)
    garbage_collector.append(file_path)
    return file_path

def upload_emoji(message,keyword,url=None,file_path=None):
    #download file
    #file_path = 'static/' + os.path.basename(url)
    print(' -- downloading file..')
    keyword = keyword.lower()
    if url is not None and file_path is None:
        file_path = download_file(url)
        urllib.urlretrieve (url, file_path)


    #send to slack
    print(' -- uploading file..')
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

def handle_exception(message, e):
    if True:
        message.reply('Unknown error.  Please submit an issue (with a screenshot of your chat window) @ https://github.com/owocki/emojibot/issues')
    else:
        print(e)



def get_val_from_state(keyword):
    print(' -- looking at db..')
    with open("state.json", "r") as myfile:
        lines = myfile.readlines()
        lines.reverse()
        for line in lines:
            row = json.loads(line)
            if row['key'] == keyword.strip():
                return row['value']

    return None
 

