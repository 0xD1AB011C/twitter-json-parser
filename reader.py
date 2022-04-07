import time
import json
from collections import Counter
from statistics import mean
import csv
from os.path import exists


#Changeable constants
MAXLINES = 1000
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



def identifyTopics(filename, limit=False, limitAmount=MAXLINES):
    
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



def parseDay(filename, limit=False, limitAmount=MAXLINES):
    start = time.process_time()
    print("PARSING FILE WITH NAME " + filename)
    topics = identifyTopics(filename, limit, limitAmount)

    data = []
    count = 0
    test = []
    with open(filename) as f:
        for line in f:
            data.append(json.loads(line))

            
            count += 1
            if limit:
                if(count > limitAmount):
                    break
                
    
    splittedHashtags = []
    locations = []

    topTweets = []
    allVPOS = []
    allPOS = []
    allNEU = []
    allNEG = []
    allVNEG = []


    resultEntryTypeProcessed = []
    for d in data:
        ALLCURRENTTWEETIDS = []
        
        splitted = []
        tmp = d["text_translation"].split()
        user = d["user"]
        location = user["location"]
        if (location):
            locations.append(location)
        retweet_count = d["retweet_count"]
        fav_count = d["favorite_count"] #Likes
        #print(retweet_count)
        reply_count = d["reply_count"]
        quote_count = d["quote_count"]
        if(reply_count != 0):
            print(reply_count)
        tweet_id = d["id_str"]
        verified = user["verified"]
        coordinates = d["coordinates"]

        
        
        RT = None
        try: #If tweet is a retweet
            RT = d["retweeted_status"]
        except:
            pass
        
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
            

        if tweet_id in ALLCURRENTTWEETIDS: #If tweet ID already processed
            continue
        ALLCURRENTTWEETIDS.append(tweet_id)
        #print(reply_count + quote_count + retweet_count)
        #Retweet count = usually agree
        #Reply count = usually disagree, much more frequent than retweets
        #Quote count = indecisive
        
        #print(tweetScore)
        #print(tweetScore)

        probabilities = None
        hashtags = None
        
        try:
            entities = d["entities"]
            hashtags = entities["hashtags"]
            sentiment = entities["sentiment"]
            probabilities = sentiment["probabilities"]
        except:
            pass

        try:
           h = hashtags[0]
           splittedHashtags.append(h["text"])

        except:
            pass
            
        
        #print(hashtags)
        veryPos = None
        midPos = None
        midNeutral = None
        midNeg = None
        veryNeg = None
        if(probabilities != None):
            veryPos = probabilities["Very positive"]
            midPos = probabilities["Positive"]
            midNeutral = probabilities["Neutral"]
            midNeg = probabilities["Negative"]
            veryNeg = probabilities["Very negative"]

            allVPOS.append(veryPos)
            allPOS.append(midPos)
            allNEU.append(midNeutral)
            allNEG.append(midNeg)
            allVNEG.append(veryNeg)
            #print(veryPos)
        #if(splittedHashtags != []):
            #print(splittedHashtags)
        tweetScore = None
        if(veryPos != None):#Has emotion score
            tweetScore = ((retweet_count*5) * (reply_count*1.5) * (quote_count*0.5) * (fav_count*1)) * ( (veryPos+veryNeg) + (midPos+midNeg)  )
        else: #Doesnt
            tweetScore = (retweet_count*5) * (reply_count*1.5) * (quote_count*0.5) * (fav_count*1)

        topTweets.append((tweet_id, tweetScore)) 
        
        #print(extract_element_from_json(d, ["entities","sentiment","probabilities"]) ) FIND A WAY TO PARSE NESTED JSON
        #emotionalPos.append(json_extract(d, 'Positive'))
        #emotionalNeut.append(json_extract(d, 'Neutral'))
        #emotionalNega.append(json_extract(d, 'Very negative'))
        #emotionalVeryNega.append(json_extract(d, 'Negative'))
        for i in tmp: #FOR WORD IN TWEET
            splitted.append(i)
        #topics
        wordCounter = Counter(splitted)
        most_occur = wordCounter.most_common(100)


        wordFiltered = [i for i in most_occur if (i[0]).lower() not in badWords]
        #print(wordFiltered)
        currentTopic = None

        acq = 0

        #print(tmp)
        #print(topics)
        #time.sleep(10)
        for i in wordFiltered:
            for i2 in topics:
                for i22 in i2:
                    #print(i22[0])
                    #time.sleep(0.1)
                    #print("matching: " + str(i) + " " + str(i2))
                    
                    if (i[0] == i22[0]): #IF WORD IN TWEET IS FOUND IN TOPIC LIST
                        currentTopic = i[0]
                        #print("aquired!")
                        acq = 1
                        break
        
        #print(currentTopic)
        
        if (currentTopic != None) and (midNeutral != None) and (currentTopic.isidentifier()): #GARBAGE TWEET
            #print("processing..")
            found = 0
            for entry in resultEntryTypeProcessed:
                #print("E: " + str(entry[0][0]))
                #print("C: " + str(currentTopic))
                if (currentTopic).lower() == (entry[0][0]).lower():#Great, append!
                    #print("Found entry: " + str(currentTopic))
                    found = 1
                    entry[1][1] += 1 #Append count of tweets
                    if(location != None):
                        entry[2].append(location)

                    if len(entry[3]) > 50:
                        pass
                    else:
                        entry[3].append((tweet_id, tweetScore)) ###
                    entry[4][0] += veryPos
                    entry[4][1] += midPos
                    entry[4][2] += midNeutral
                    entry[4][3] += midNeg
                    entry[4][4] += veryNeg
                    entry[5].append(splittedHashtags)
                    if(coordinates):
                        entry[6].append(coordinates["coordinates"])
            if found == 0: #not found, create obj and append
                #print("Creating topic!")
                param0 = [currentTopic]
                param1 = [filename, 1]
                param2 = [location]
                param3 = [(tweet_id, tweetScore, verified)] ###
                param4 = [veryPos, midPos, midNeutral, midNeg, veryNeg]
                param5 = [splittedHashtags]
                param6 = []
                entry = [param0, param1, param2, param3, param4, param5, param6]
                #print(entry)
                #time.sleep(1)
                resultEntryTypeProcessed.append(entry)
        #print("done")
    print("Cleaning up")
    
    #print(hashFiltered)

    
    for x in resultEntryTypeProcessed: #Final processing
        #Hashtags
        hashCounter = Counter(x[5][0])
        finalHashtags = hashCounter.most_common(25)
        tmp = []
        for f in finalHashtags:
            tmp.append(f[0])
        x[5] = tmp 
        
        #location
        locationCounter = Counter(x[2])
        finalLocation = locationCounter.most_common(50)
        x[2] = finalLocation
        tmp = []
        for f in finalLocation:
            tmp.append(f[0])
        x[2] = tmp 
        #Emotions
        emtItr = 0
        for emt in x[4]:
            x[4][emtItr] = (x[4][emtItr] / x[1][1])
            emtItr += 1

        #tOpTweets
        x[3] = sorted(x[3], key = lambda i: float(i[1]), reverse = True)
        x[3] = (x[3])[:50]

        finalX = []
        for i in x[3]:
            appnd = (i[0], False)
           
            if(len(i) > 2):
                #finalX.append(i[2])
                appnd = (i[0], i[2])
            finalX.append(appnd)
        x[3] = finalX

#FINISHED
    print("Fully processed...")
    print("Writing to .CSV!")

    for x in resultEntryTypeProcessed:

        
        
        header = ['date', 'location', 'id', 'vpos', 'pos', 'neu', 'neg', 'vneg', 'hashtags']
        data = [    x[1][0], x[2], x[3], x[4][0], x[4][1], x[4][2], x[4][3], x[4][4], x[5], x[6]    ]
        name = x[0][0] + ".csv"
        
        with open(str(name), 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            if exists(name): #If creating file, write header
                pass
            else:
                writer.writerow(header) #Not working correctly.
            writer.writerow(data)
            f.close()
    

    ##########
    #print(resultEntryTypeProcessed)
    print("Time taken: " + str((time.process_time() - start)) + "s")
    print("Finished parsing file with name " + filename + "!")
    print("\n\n\n")
    return wordFiltered


    



######################################################################################

print("<Welcome to Wills JSON parser!>")
print("See README.TXT")
print("\n\nEnter the filenames to parse in the format:\nfilename.json, filename.json, filename.json\n")

x = input()
#x = "2020-03-01.json"
totalStartTime = time.process_time()
list = x.split (",")
for i in list:
    i = i.lstrip()
    wordF = parseDay(i, TEST_MODE) #2nd arg: 0 or 1 limit enabled #3rd arg limit amount if limit enabled (default 1k)

print("TOTAL time taken: " + str((time.process_time() - totalStartTime)) + "s")

#2020-03-01.json, 2020-03-02.json, 2020-03-03.json
