import os
import requests
import re
import time
import warnings
from dragnet import extract_content
from gensim.summarization import summarize, keywords
from slackclient import SlackClient
from urllib.parse import urlparse

warnings.filterwarnings('ignore', category=UserWarning)

COMMAND_REGEX = re.compile('^!tldr <(https?://[^\s]+)>')
RESPONSE_TEMPLATE = u'%s %s %i%% reduced:\n> %s\n*Keywords* %s'
ERROR_RESPONSE = '¯\_(ツ)_/¯'
RTM_READ_DELAY = 1
WORD_COUNT = int(os.environ.get('WORD_COUNT') or 200)
KEYWORD_COUNT = int(os.environ.get('KEYWORD_COUNT') or 5)
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')

if not SLACK_BOT_TOKEN:
    print('Error: SLACK_BOT_TOKEN env var must be set')
    exit(1)
slack_client = SlackClient(SLACK_BOT_TOKEN)
bot_id = None


def tldrafy(user, url):
    domain = urlparse(url).netloc
    content = extract_content(requests.get(url).content)
    summary = summarize(content, word_count=WORD_COUNT)
    keyword_list = keywords(content, words=KEYWORD_COUNT, lemmatize=True, split=True)
    percent_reduction = round((1 - (float(len(summary)) / len(content))) * 100)
    return '<@%s>' % user, \
           '<%s|%s>' % (url, domain), \
           percent_reduction, \
           summary.replace('\n', ' '), \
           ', '.join(keyword_list)


def parse_events(slack_events):
    for event in slack_events:
        if event['type'] == 'message' and 'subtype' not in event:
            match = COMMAND_REGEX.match(event['text'])
            if match:
                try:
                    response = RESPONSE_TEMPLATE % tldrafy(event['user'], match.group(1))
                except Exception as err:
                    print('Error: %s' % err)
                    response = ERROR_RESPONSE
                slack_client.api_call('chat.postMessage',
                                      channel=event['channel'],
                                      text=response)


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print('@tldrbot connected')
        bot_id = slack_client.api_call('auth.test')['user_id']
        while True:
            parse_events(slack_client.rtm_read())
            time.sleep(RTM_READ_DELAY)
    else:
        print('Error: Could not connect')
        exit(1)
