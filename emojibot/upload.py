# Thanks https://github.com/smashwilson/slack-emojinator

import os
import requests
from slackbot_settings import team_name, cookie
from bs4 import BeautifulSoup

url = "https://{}.slack.com/customize/emoji".format(team_name)

def do_upload(filename, emoji_name):

    print(" ---- processing upload to slack, {}.".format(filename))

    headers = {
        'Cookie': cookie,
    }

    # Fetch the form first, to generate a crumb.
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    soup = BeautifulSoup(r.text,'lxml')
    crumb = soup.find("input", attrs={"name": "crumb"})["value"]

    data = {
        'add': 1,
        'crumb': crumb,
        'name': emoji_name,
        'mode': 'data',
    }
    files = {'img': open(filename, 'rb')}
    r = requests.post(url, headers=headers, data=data, files=files, allow_redirects=False)
    if r.status_code != 200:
        return ['Could not authenticate you.  Check your `team_name` and  `cookie` settings. ']
    soup = BeautifulSoup(r.text,'lxml')
    errors = [ele.text for ele in soup.findAll('p', attrs={'class':'alert'})]
    return errors
