import lda
import json
import awesome_lda
import random

model_file = "awesome.object" 

def tweet_to_topic(in_tweet, number_of_topics):
    # Read Model from File
    model, _, topic_dict = awesome_lda.loadModel(model_file)
    in_tweet = [in_tweet]

    try:
        doc_topic, real_tweets = awesome_lda.transform_tweets(model, in_tweet)
        topics = awesome_lda.printTransformedTweets(real_tweets, doc_topic, topic_dict)
    except Exception, e:
        print e
        # finding a random topic between all the topics generated by our model
        # if the status is meaningless (non_english, all stop words...)
        random.seed()
        rand_topic = random.randint(1, 40)
        topics = topic_dict[rand_topic]

    return topics[:number_of_topics]

def main():

    '''
    Read in $LIMIT tweets, and transform them against model that was saved to file
    '''
    with open('my_fake_tweets.json', 'r') as file:
        tweet = file.read()
        topic_array= tweet_to_topic(tweet, 3)
        for topic in topic_array:
            print topic

if __name__ == '__main__':
    main()

