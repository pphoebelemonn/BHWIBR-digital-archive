#!/usr/bin/env python
# coding: utf-8

# # Workshop #4: Sentiment Analysis as a Critical Prototype
# 
# This notebook introduces Natural Language Processing (NLP) through the lens of moderation.
# You’ll use a pre-trained model to classify Reddit data for sentiment and toxicity, and reflect on how automated moderation systems embed assumptions and bias.
# 
# ⚠️ This is a critical prototype: the goal is not perfect classification, but to reveal how these tools function, misfire, and shape online discourse.

from transformers import pipeline
import pandas as pd
import re
import string
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import json 
from transformers import AutoModelForSequenceClassification, AutoTokenizer


def get_sentiment_classifier():
    model_name = "cardiffnlp/twitter-roberta-base-sentiment"
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    return pipeline('sentiment-analysis', model=model, tokenizer = tokenizer)

def get_toxicity_classifier():
    #uncoment this to get all labels 
    # return pipeline('text-classification', model='unitary/toxic-bert', return_all_scores=True)
    return pipeline('text-classification', model='unitary/toxic-bert')

def analyze_sentiment_toxicity(text): 
    LABELS = {"LABEL_0": "NEGATIVE",
    "LABEL_1": "NEUTRAL",
    "LABEL_2": "POSITIVE",
    "LABEL_3": "MIXED",
    }

    try:
        sentiment_classifier = get_sentiment_classifier()
        output = sentiment_classifier(text)
        print("Sentiment raw output:", output )
        sentiment = LABELS[sentiment_classifier(text)[0]['label']]

    except Exception as e:
        print(e)
        sentiment = 'error'

    try:
        toxicity_classifier = get_toxicity_classifier()
        output = toxicity_classifier(text)
        print("Toxicity raw output:", output)
        label = output[0]['label']
        score = output[0]['score']

        # Example mapping - adjust based on your model
        if label == "toxic" and score > 0.7:
            toxicity = "TOXIC"
        else:
            toxicity = "NON_TOXIC"
    except Exception as e:
        print("Toxicity error:", e) 
        toxicity = 'error'

    return {'sentiment': sentiment, 'toxicity': toxicity}

def flag_keywords(text):
    try:
        moderation_list = []
        with open('./moderation_list.txt', 'r') as file:
            for line in file:
                moderation_list.append(line.rstrip())
    except Exception as e: 
        print(e)
        return []

    text_lower = text.lower()
    text_lower = clean(text) 
    text_list = text_lower.split(' ')
    flagged_keywords = []
    # for word in moderation_list:
    #     if word in text_lower:
    #         flagged_keywords.append(word)
    
    for word in text_list:
        if word in moderation_list: 
            flagged_keywords.append(word) 
            
    return flagged_keywords

def clean(text): 
    if not isinstance(text, str):
        return ""
    #convert to lowercase and remove 
    text = text.lower() 
    regex_pattern = f"[{re.escape(string.punctuation)}]"
    text = re.sub(regex_pattern, "", text)
    text = re.sub(r'\s+', ' ', text).strip()   
    tokens = [word for word in text.split() if word not in ENGLISH_STOP_WORDS]
    print("Cleaned Text: \n", tokens)
    return ' '.join(tokens)

input_file = "content_log.json"
output_file = "content_log_cleaned.json"

# with open(input_file, "r") as infile, open(output_file, "w") as outfile:
#     for line in infile:
#         try:
#             entry = json.loads(line)
#             raw_text = entry.get("raw_text") or entry.get("text") or ""
#             entry["cleaned_text"] = clean(raw_text)
#             outfile.write(json.dumps(entry) + "\n")
#         except json.JSONDecodeError as e:
#             print("Error in cleaning, skipping malformed line:", e)

# if __name__ == "__main__":
#     print('hello')
#     clean("/Users/phoebelemon/anaconda3/lib/python3.11/site-packages/transformers/utils/generic.py:260: UserWarning: torch.utils._pytree._register_pytree_node is deprecated. Please use torch.utils._pytree.register_pytree_node instead.torch.utils._pytree._register_pytree_node(")
    