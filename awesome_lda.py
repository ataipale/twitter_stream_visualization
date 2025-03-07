
import sys, os, re
import numpy as np
import lda
import twokenizer
from sklearn.feature_extraction.text import CountVectorizer
import langdetect 

import pickle

filter_prefix_set = ('@', 'http', 'rt', 'www')

def processTweets(tweets):
    """Remove non-english tweets, then stop-words from tweets, and run CountVectorize."""

    english_tweets = getEnglishTweets(tweets)
    real_tweets = getRealWords(english_tweets)
    tdm, feature_names = countVectorize(real_tweets)

    return (tdm, feature_names, real_tweets)

def countVectorize(tweets):
    # use Sklearn's kit to fit and transform the array of just real words from the 
    # tweets and make TDM
    count_vectorizer = CountVectorizer(min_df = 1, stop_words = 'english')
    tdm = count_vectorizer.fit_transform(tweets)
    feature_names = np.array(count_vectorizer.get_feature_names())

    return (tdm, feature_names)

def getRealWords(tweets):
    real_tweets = []
    for tweet_split in tweets:
        if tweet_split:
            tokenized = twokenizer.tokenize(tweet_split)
            # get rid of stopwords
            # no_stopwords_tweet = [word for word in tokenized if word not in common_words_set]
            # get rid of punctuation and internet terms
            just_real_words = [re.sub(r'[^\w\s]','', word) for word 
                                        in tokenized 
                                        if not word.startswith(filter_prefix_set)
                                    ]
            if just_real_words:
                real_tweets.append(" ".join(just_real_words))

    return real_tweets

def getEnglishTweets(tweets):
    english_tweets = []
    for status in tweets:
        if status:
            # ignore non-ascii characters, make all lowercase letters
            tweet_split = status.encode('ascii', 'ignore').lower()
            # get rid of useless characters in tweets, and makes words from string
            if tweet_split:
                # ignore non-English tweets
                # print tweet_split
                try:
                    lang = langdetect.detect(tweet_split)
                except langdetect.lang_detect_exception.LangDetectException:
                    continue

                if lang == 'en':
                    english_tweets.append(tweet_split)

    return english_tweets

# process and clean the tweets and return a TDM of tweets/vocab and vocab(feature_names)
def processJsonData(JSON_array):
    # Return just the text from the tweets represented as JSON data
    tweets = []
    for item in JSON_array:
        status = item.get("text")
        if status:
            tweets.append(status)

    # [ item.get("text") if item.get("text") is not None else '' for x in row ]

    return tweets

def trainModel(tdm):
    npmatrix = np.array(tdm.toarray())
    model = lda.LDA(n_topics=40, n_iter=50, random_state=1)
    model.fit(npmatrix)
    return model

def getTopics(model, feature_names, n_top_words):
    # topic_word is a matrix of point estimate of word distribution per topic. 
    # Shape = [n_topics, n_features]
    topic_word = model.components_ 
    topic_dict = []
    
    for i, word_dist in enumerate(topic_word):
        print "Here are feature_names:"
        # Below: For each feature, sort the vocab based on word distribution 
        # and give me the 8 most relatively important words in each doc
        topic_words = np.array(feature_names)[np.argsort(word_dist)][:-n_top_words:-1]
        topic_dict.append(topic_words) 
        print('Topic {}: {}'.format(i, ' '.join(topic_words)))

    return topic_dict

def transform_tweets(model, tweets):

    '''
    Transforms Incoming tweet data and returns the tweet and topic
    '''

    # Prepare Data for Transformation
    processed_data_tdm, _, real_tweets = processTweets(tweets)
    npmatrix = np.array(processed_data_tdm.toarray())

    # Transform Data
    doc_topic = model.transform(npmatrix)

    return (doc_topic, real_tweets) 

def printTransformedTweets(tweets, doc_topic, topic_dict):
    topics_from_tweet = []
    for title, topic_dist in zip(tweets, doc_topic):
        topics = topic_dict[topic_dist.argmax()]
        print("(TOPIC {} ::) {} ".format(' '.join(topics), title))
        for topic in topics:
            topics_from_tweet.append(topic)
    return topics_from_tweet


def saveModel(model, feature_names, topic_dict, filename):
    pickle_dict = dict(model = model, feature_names = feature_names, topic_dict = topic_dict)
    pickle.dump( pickle_dict, open(filename, "wb"))

def loadModel(filename):
    model_object = pickle.load(open(filename, "rb" ))

    model = model_object.get('model')
    feature_names = model_object.get('feature_names')
    topic_dict = model_object.get('topic_dict')

    return (model, feature_names, topic_dict)
