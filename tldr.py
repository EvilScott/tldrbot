import os
import requests
import re
import time
import warnings
from dragnet import extract_content
from gensim.summarization import summarize, keywords
from slackclient import SlackClient

warnings.filterwarnings('ignore', category=UserWarning)

COMMAND_REGEX = re.compile('^!tldr (https?://[^\s]+)')
RTM_READ_DELAY = 3
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')

if not SLACK_BOT_TOKEN:
    print('SLACK_BOT_TOKEN env var must be set')
    exit(1)
slack_client = SlackClient()
bot_id = None


def tldrafy(url):
    content = extract_content(requests.get(url).content)
    summary = summarize(content, word_count=200)
    keyword_list = keywords(content, words=10, lemmatize=True, split=True)
    percent_reduction = round((1 - (float(len(summary)) / len(content))) * 100)

    return {
      'summary': summary.replace('\n', ' '),
      'keywords': keyword_list,
      'percent_reduction': percent_reduction
    }


def parse_events(slack_events):
    for event in slack_events:
        if event['type'] == 'message' and 'subtype' not in event:
            match = COMMAND_REGEX.match(event['text'])
            if match:
                tldr = tldrafy(match.group(1))  # TODO error handling
                response = u'> %s' % tldr['summary']
                slack_client.api_call('chat.postMessage',
                                      channel=event['channel'],
                                      text=response or '¯\_(ツ)_/¯')


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print('tldrbot connected')
        bot_id = slack_client.api_call('auth.test')['user_id']
        while True:
            parse_events(slack_client.rtm_read())
            time.sleep(RTM_READ_DELAY)
    else:
        print('Could not connect')
        exit(1)
