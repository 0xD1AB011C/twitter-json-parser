import time
import json
from collections import Counter
from statistics import mean
import csv
import os.path


#Changeable constants
MAXLINES = 3000
TEST_MODE = False #Limits the amount of lines read to MAXLINES
badWords = ["the", "rt", "by", "to", "and", "by", "are", "a", "is", "as",
            "you", "I", "not", "their", "of",'a', 'about', 'all', 'an',
            'another', 'any', 'around', 'at', 'bad', 'beautiful', 'been',
            'better', 'big', 'can', 'every', 'for', 'from', 'good', 'have',
            'her', 'here', 'hers', 'his', 'how',
            'i', 'if', 'in', 'into', 'is', 'it', 'its', 'large', 'later',
            'like', 'little', 'main', 'me', 'mine', 'more', 'my', 'now',
            'of', 'off', 'oh', 'on', 'please', 'small', 'some', 'soon',
            'that', 'the', 'then', 'this', 'those', 'through', 'till', 'to',
            'towards', 'until', 'us', 'want', 'we', 'what', 'when', 'why',
            'wish', 'with', 'would', 'only', 'think', 'up', 'we', 'were', 'will',
            'y', 'your', 'so', 'the', 'killed', 'la', 'just', 'j', 'its', 'it',
            'is', 'if', 'he', 'has', 'guy', 'from','e', 'did', 'do', 'de', 'but',
            'because', 'as', 'be', 'and', 'against', 'a']
#bad words must be lowercase
PROCESS_RETWEETS = True


def identifyTopics(filename, limit=False, limitAmount=MAXLINES): #Finds main topics for a given day
    data = []
    count = 0
    with open(filename) as f:
        for line in f:
            data.append(json.loads(line))
            count += 1
            if limit:
                if(count > limitAmount):
                    break
    topics = []
    splitted = []
    for d in data:
        tmp = d["text_translation"].split()
        for i in tmp: #FOR WORD IN TWEET
            splitted.append(i)
            
    wordCounter = Counter(splitted)
    most_occur = wordCounter.most_common(250)


    wordFiltered = [i for i in most_occur if (i[0]).lower() not in badWords]
    topics.append(wordFiltered)
    return topics

def createData(filename, limit, limitAmount):
    count = 0
    data = []
    with open(filename) as f:
            for line in f:
                data.append(json.loads(line))
                count += 1
                if limit:
                    if(count > limitAmount):
                        break
    return data


def findTweetMainTopic(sorted_filtered_text, topics):
    acq = 0 #Main topic acquired

    for i in sorted_filtered_text: #Descending in terms of usage
        for possible_topic in topics[0]:
            #print("Comparing: " + str(i[0]) + " WITH " + possible_topic[0])
            if i[0] == possible_topic[0]:
                return i[0]
    return False

def parseDay(filename, limit=False, limitAmount=MAXLINES):
    start = time.process_time()
    print("PARSING FILE WITH NAME " + filename)
    topics = identifyTopics(filename, limit, limitAmount)
    data = []
    count = 0
    data = createData(filename, TEST_MODE, limitAmount) #Fetch data from file

    resultEntryTypeProcessed = [] #Declare final data structure
    raw_data = []
    tweet_processed_list_ids = []

    for d in data: #For tweet in day, let d = tweet
        tweet_text = d["text_translation"].split()



        tweet_text_split = []
        for i in tweet_text: #FOR WORD IN TWEET
            tweet_text_split.append(i)

        wordcounter_object = Counter(tweet_text_split)
        tweet_preprocessed = [i for i in (wordcounter_object.most_common(100)) if (i[0]).lower() not in badWords] #Top 100 words in current tweet

        tweet_current_topic = findTweetMainTopic(tweet_preprocessed, topics)

        #print(tweet_current_topic)
        if(tweet_current_topic == False): #Tweet is garbage and not a useful topic
            continue #Iterate next tweet
        if(tweet_current_topic.isidentifier()): #Topic is valid name
            pass
        else:
            continue
        tweet_current_topic = tweet_current_topic.lower()
        #Tweet is good and valid topic so fetch all information
        user = d["user"] #MAIN USER OBJECT
        user_location = user["location"]
        retweet_count = d["retweet_count"]
        fav_count = d["favorite_count"] #Likes
        reply_count = d["reply_count"]
        quote_count = d["quote_count"]
        tweet_id = d["id_str"]
        verified = user["verified"]
        coordinates = d["coordinates"]
        RT = None
        try: #Declares 'RT' if tweet is a retweet
            RT = d["retweeted_status"]
        except:
            pass
        #
        if (RT != None) and (PROCESS_RETWEETS): #If tweet is a retweet overwrite incorrect vals
            fav_count = RT["favorite_count"] #Likes
            quote_count = RT["quote_count"]
            reply_count = RT["reply_count"]
            retweet_count = RT["reply_count"]
            tweet_id = RT["id_str"]
            verified = user["verified"]
            #print("lol")
        if (RT != None) and (PROCESS_RETWEETS == False):
            continue

        if tweet_id in tweet_processed_list_ids: #If tweet ID already processed, can happen if two people retween the same tweet
            continue
        else:
            tweet_processed_list_ids.append(tweet_id) #Commence processing and thus add tweet ID to our list


###################################################################################################################################################
        #PROCESSING  
        try:
            entities = d["entities"]
            hashtags = entities["hashtags"]
            sentiment = entities["sentiment"]
            probabilities = sentiment["probabilities"]
            
            user_mentions = entities["user_mentions"]
            
                #print(names)
            
        except:
            pass



        if(probabilities != None):
            veryPos = probabilities["Very positive"]
            midPos = probabilities["Positive"]
            midNeutral = probabilities["Neutral"]
            midNeg = probabilities["Negative"]
            veryNeg = probabilities["Very negative"]

        tweetScore = None #How interesting is a tweet metric
        if(veryPos != None):#Has emotion score
            tweetScore = ((retweet_count*5) * (reply_count*1.5) * (quote_count*0.5) * (fav_count*1)) * ( (veryPos+veryNeg) + (midPos+midNeg)  )
        else: #Doesnt
            tweetScore = ((retweet_count*5) * (reply_count*1.5) * (quote_count*0.5) * (fav_count*1))  

        #0 = topic
        #1 = topHashtags
        #2 = alltweetIDS
        #3 = allmentions
        #4 = locations
        #5 = coordinates
        #6 = emotionArray
        #7 = wordCloud
        #EmotionArray = []
        emotionArrayTemplate = [ [], [], [], [], [] ]

        raw_data_object = (tweet_current_topic, [], [], [], [], [], emotionArrayTemplate, [])

        raw_data_object_index = 0
        found_in_data = False
        for raw in raw_data:
            if raw[0] == tweet_current_topic: #Exists
                found_in_data = True
                break
            raw_data_object_index += 1
        if(found_in_data):
            pass
        else:
            raw_data.append(raw_data_object) #doesnt exist yet, create
            raw_data_object_index = len(raw_data)-1
        #raw_data[raw_data_object_index] to access entry


        if(hashtags):
            for i in range(len(hashtags)):
                raw_data[raw_data_object_index][1].append(hashtags[i]["text"])

        

        if verified: #If verified flag exists
            raw_data[raw_data_object_index][2].append((tweet_id, verified, tweetScore)) #Add tweet ID
        raw_data[raw_data_object_index][2].append((tweet_id, False, tweetScore)) #Add tweet ID alternate
        
        if(user_mentions):
            for i in range(len(user_mentions)):
                raw_data[raw_data_object_index][3].append(user_mentions[i]["screen_name"]) #Add mentions

        if(user_location):
            raw_data[raw_data_object_index][4].append(user_location)

        if(coordinates):
            raw_data[raw_data_object_index][5].append(coordinates["coordinates"])

        if(veryPos):
            e = [veryPos, midPos, midNeutral, midNeg, veryNeg]
            raw_data[raw_data_object_index][6].append(e)

        if(True):
            raw_data[raw_data_object_index][7].extend(tweet_preprocessed)

    return raw_data


def finalizeData(data):

    for targetIndex in range(len(data)):

        ################################################ HASHTAGS
        for i in range(len(data[targetIndex][1])):
            data[targetIndex][1][i] = data[targetIndex][1][i].lower()

        c = Counter(data[targetIndex][1])

        x = c.most_common(25)
        tmp = []
        for i in x:
            tmp.append(i[0])
        data[targetIndex][1].clear()
        data[targetIndex][1].append(tmp)
        ################################################ TWEET IDS
        tmp = sorted(data[targetIndex][2], key=lambda x: x[2], reverse=True)
        data[targetIndex][2].clear()
        data[targetIndex][2].append(tmp[:50])
        ################################################ MENTIONS
        for i in range(len(data[targetIndex][3])):
            data[targetIndex][3][i] = data[targetIndex][3][i].lower()

        c = Counter(data[targetIndex][3])
        x = c.most_common(25)
        tmp = []
        for i in x:
            tmp.append(i[0])
        data[targetIndex][3].clear()
        data[targetIndex][3].append(tmp)
        ################################################ LOCATIONS
        for i in range(len(data[targetIndex][4])):
            data[targetIndex][4][i] = data[targetIndex][4][i].lower()

        c = Counter(data[targetIndex][4])
        x = c.most_common(25)
        tmp = []
        for i in x:
            tmp.append(i[0])
        data[targetIndex][4].clear()
        data[targetIndex][4].append(tmp)
        ################################################ COORDINATES
        pass
        ################################################ EMOTION ARRAY
        tmp = [0,0,0,0,0]
        ctr = 0
        for i in data[targetIndex][6]:
            if(i):
                tmp[0] += i[0]
                tmp[1] += i[1]
                tmp[2] += i[2]
                tmp[3] += i[3]
                tmp[4] += i[4]
                ctr += 1
        tmp[0] = tmp[0]/ctr
        tmp[1] = tmp[1]/ctr
        tmp[2] = tmp[2]/ctr
        tmp[3] = tmp[3]/ctr
        tmp[4] = tmp[4]/ctr
        data[targetIndex][6].clear()
        data[targetIndex][6].append(tmp)

        ################################################ WORD CLOUD
        tmp = sorted(data[targetIndex][7], key=lambda x: x[1], reverse=True)
        data[targetIndex][7].clear()
        data[targetIndex][7].append(tmp[:25])

        ################################################ FINISHED
    #while(True):
        #print("Enter number to show:")
        #x = input()
        #print(data[0][int(x)])
        #print("\n\n\n")
    return data


def exportData(data, filename):
    print("Writing to .CSV!")
    for targetIndex in range(len(data)):
        filename = os.path.splitext(filename)[0]
        writeLine = [     filename,  data[targetIndex][1][0], data[targetIndex][2][0], data[targetIndex][3][0], data[targetIndex][4][0], data[targetIndex][5], data[targetIndex][6][0], data[targetIndex][7][0]     ]
        name = data[targetIndex][0] + ".csv"
        with open(str(name), 'a', encoding='UTF8', newline='') as f:
            writer_object = csv.writer(f)
            writer_object.writerow(writeLine)
            f.close()



def main():
    print("<Welcome to Wills JSON parser!>")
    print("See README.TXT")
    print("\n\nEnter the filenames to parse in the format:\nfilename.json, filename.json, filename.json\n")

    x = input()
    #x = "2020-03-01.json"
    totalStartTime = time.process_time()
    list = x.split (",")
    for i in list:
        i = i.lstrip()
        data = parseDay(i, TEST_MODE) #2nd arg: 0 or 1 limit enabled #3rd arg limit amount if limit enabled (default 1k)
        finalData = finalizeData(data)
        exportData(finalData, i)

    print("TOTAL time taken: " + str((time.process_time() - totalStartTime)) + "s")


#CODE


main()






