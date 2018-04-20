# TL/DR Slackbot

`tldrbot` makes use of [dragnet](https://github.com/seomoz/dragnet) and [gensim](https://radimrehurek.com/gensim/) 
to create a [Slack](https://slack.com/) bot that summarizes the content at a given URL.

### In Slack
Usage: ```!tldr <url>```

![Example screenshot](../assets/example.png)


### Installation
- [Create a new slack app](https://api.slack.com/apps) and create a bot token.
- ```$ docker pull evilscott/tldrbot```
- ```$ docker run -e SLACK_BOT_TOKEN=<your bot token> --name tldrbot -itd --rm tldrbot```

### Parameters
Pass these in as environmental variables to the ```docker run``` command:
- `SLACK_BOT_TOKEN` (required) your bot token from your app in Slack
- `WORD_COUNT` (default 200) length of summarized article
- `KEYWORD_COUNT` (default 5) number of keywords to return
