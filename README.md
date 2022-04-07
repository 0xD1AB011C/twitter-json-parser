
# Project Title

Wills JSON parser for twitter dataset



## Authors

- [@lit-ware](https://github.com/lit-ware) - Will


## Features

- Scrape multiple .json files
- Limit lines read 
- A 'bad word' list to filter out topics
- Export results to .csv files incrementally
- Automatic string filtering
- Toggle retweet processing


## Documentation

This parser scrapes a pre-dumped .json from the twitter API.

'.json' dumps are processed into various .csv files, these files contain various data for the given topic, the filename is equivalent to the topic.

The data format is as follows for those files:

DATE |  LOCATIONS | TWEET_IDS | VPOS | POS | NEU | NEG | VNEG | HASHTAGS | GEOCORDS

Date: The filename of the parsed original .json dumped

Locations: An array of the users locations for the given data, sorted by most frequent

Tweet ids: A tuple array of the most popular / influential tweets and a boolean flag that declares if the user was verified

VPOS: The tweets estimated 'Very positive' emotion probability

POS: The tweets estimated 'Positive' emotion probability

NEU: The tweets estimated 'Neutral' emotion probability

NEG: The tweets estimated 'Negative' emotion probability

VNEG: The tweets estimated 'Very negative' emotion probability

HASHTAGS: The hashtags most commonly used with the topic in question, in descending order

GEOCORDS: The tweets co-ordinates, should they be found