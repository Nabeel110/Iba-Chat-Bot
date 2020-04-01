#imports
from flask import Flask, render_template, request, url_for

# New Imports
import nltk
from nltk.stem.lancaster import LancasterStemmer
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import load_model
import random
import json
import pickle
import pandas as pd
import IBA_Web_Scraping as iba
stemmer = LancasterStemmer()


app = Flask(__name__)


# Loading training Data
data = pickle.load( open( "training_data", "rb" ) )
words = data['words']
classes = data['classes']
train_x = data['train_x']
train_y = data['train_y']

# Loading Trained Model
with open('intents.json') as json_data:
    intents = json.load(json_data)

model = load_model('model_chatbot.h5')



# Functions to clean User Input
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=False):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)

    return(np.array(bag))

context = {}

ERROR_THRESHOLD = 0.25

def classify(sentence):
    input_data = pd.DataFrame([bow(sentence, words)], dtype=float, index=['input'])
    results = model.predict(input_data)
    results = [[i,r] for i,r in enumerate(results[0]) if r>ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], r[1]))
    return return_list



# Taking Sentences to respond
def response(sentence, userID='123', show_details=False):
    results = classify(sentence)
    if results:
        while results:
            for i in intents['intents']:
                if i['tag'] == results[0][0]:
                    if 'context_set' in i:
                        if show_details: print ('context:', i['context_set'])
                        context[userID] = i['context_set']
                    if not 'context_filter' in i or (userID in context and 'context_filter' in i and i['context_filter'] == context[userID]):
                        if show_details: print ('tag:', i['tag'])
                        is_news_asked = False
                        if random.choice(i['responses']) == 'Wait while we are fetching recent updates from IBA...'  or random.choice(i['responses']) == 'Please wait a moment':
                                is_news_asked = True
                        
                        return (random.choice(i['responses']),is_news_asked)

            results.pop(0)


#define app routes
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/get")
#function for the bot response
def get_bot_response():
    userText = request.args.get('msg')
    print(userText)
    print(response(userText))
    
    resp, is_news_asked = response(userText)
    
    if is_news_asked:
        resp = ''
        print(iba.get_IBA_news())
        resp = iba.get_IBA_news()
        print(resp)
        return resp
    else:
        return resp
    
 # return str(response(userText))
if __name__ == "__main__":
    app.run(debug=True,threaded =False)
