import json
import requests
import sys
import warnings
from dragnet import extract_content
from gensim.summarization import summarize, keywords

warnings.filterwarnings('ignore', category=UserWarning)

url = sys.argv[1]
content = extract_content(requests.get(url).content)
summary = summarize(content, word_count=200)
keywords = keywords(content, words=10, lemmatize=True, split=True)
percent_reduction = round((1 - (float(len(summary)) / len(content))) * 100)

data = {
  'summary': summary.replace('\n', ' '),
  'keywords': keywords,
  'percent_reduction': percent_reduction
}

print(json.dumps(data))
