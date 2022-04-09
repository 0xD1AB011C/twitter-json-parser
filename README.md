
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

DATE |  HASHTAGS | TWEET_IDS | MENTIONS | LOCATIONS | COORDINATES | EMOTIONS | TOP_WORDS

DATE: The filename of the parsed original .json dumped

HASHTAGS: An array of the top hashtags used when tweeting about the given subject, sorted in decsending order

TWEET_IDS: A 2D array composing of the top 50 tweets for the given subject for the day. Entries in the array follow (TWEET_ID, BOOL VERIFIED, TWEET_SCORE)

MENTIONS: An array of the most mentioned users when tweeting about the given subject.

LOCATIONS: An array of the most popular locations, set by the individual user for their account information, not necessarily where the tweet was from.

COORDINATES: An array of any found coordinates for any tweets about the given subject.

EMOTIONS: An array of length 4, containing: VERY_POSITIVE, POSITIVE, NEUTRAL, NEGATIVE, VERY_NEGATIVE. These are average predictions about the tone of all tweets for that day.

TOP_WORDS: The most frequent words used when talking about the given subject.
