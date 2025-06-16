import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import pandas as pd
import os
import json 
import numpy as np
import string
import re  

from collections import Counter
from wordcloud import WordCloud, STOPWORDS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from sklearn.decomposition import NMF
from time import time
from sentimental_analysis import clean 

def load_data(filepath): 
    try:
        df = pd.read_json(filepath)
        return df
    except Exception as e:
        print(f"Error loading file: {e}")
        return pd.DataFrame()

def create_wordcloud(df, reason_filter=None, output_name = "wordcloud.png", title = "wordcloud"):
    if reason_filter:
        df = df[df['reason'].str.contains(reason_filter, case=False, na=False)]
    
    #combining all data into a string for word clouding 
    text = ''. join(df['cleaned_text'].dropna().tolist())
    stop_words = set(STOPWORDS)

    #handling if string is empty 
    if not text.strip(): 
        print(f"[!] No text found for reason: {reason_filter}")
        return
    
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        stopwords=stop_words,
        max_words=100,
        max_font_size=60
    ).generate(text)

    plt.figure(figsize=(10, 5))
    plt.title(title)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')

    #save as image
    path = "../public/static"
    os.makedirs(path, exist_ok = True)
    output_path = os.path.join(path, output_name)
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")

def topic_model(df, output_name = "topic_model.png", title = "Top 10 Topics"):
    df['content'] = df['title'].fillna('') + ' ' + df['text'].fillna('')
    df['cleaned_content'] = df['content'].apply(clean)

    n_samples = 2000
    n_features = 1000
    n_topics = 8
    n_top_words = 5

    #creating vectors 
    t0 = time()
    tokens = df['cleaned_content'] #corpus ? 
    vectorizer = TfidfVectorizer()
    vectorizer = TfidfVectorizer(max_features = n_features, ngram_range=(1,2))

    X = vectorizer.fit_transform(tokens)

    #create TFIDF matrix 
    features = vectorizer.get_feature_names_out()
    tfidf_df = pd.DataFrame(X.toarray(), columns = features)

    print("Showing TFIDF matrix... ")
    tfidf_df.head()
    print("Fitting the NMF model with n_samples=%d and n_features=%d..."
        % (n_samples, n_features))
    

    #perform modeling
    nmf = NMF(n_components = n_topics, random_state = 1).fit(tfidf_df)
    print("done in %0.3fs." % (time() - t0))

    #list out topics 
    for topic_idx, topic in enumerate(nmf.components_):
        print("Topic #%d:" % topic_idx)
        print(" ".join([features[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
        print()
    
    #Create a bar chart of top 10 topics 
    plot_topics(nmf, features, n_top_words, output_name, title)

def plot_topics(nmf_model, features, n_top_words, output_name, title):
    n_topics = nmf_model.components_.shape[0]
    cols = 2
    rows = (n_topics + 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(14, rows * 3))
    axes = axes.flatten()

    for topic_idx, topic in enumerate(nmf_model.components_):
        top_indices = topic.argsort()[:-n_top_words - 1:-1]
        top_features = [features[i] for i in top_indices]
        weights = topic[top_indices]

        ax = axes[topic_idx]
        ax.barh(top_features[::-1], weights[::-1], color='skyblue')
        ax.set_title(f"Topic #{topic_idx}")
        ax.set_xlabel("Weight")

    # Hide any extra subplots
    for i in range(n_topics, len(axes)):
        fig.delaxes(axes[i])

    plt.tight_layout()
    path = "../public/static"
    os.makedirs(path, exist_ok=True)
    output_path = os.path.join(path, output_name)
    plt.savefig(output_path)
    plt.close()

def chart_distribution(df, filter = None, output_name = "sentiment_chart.png", title = "sentiment_chart"): 
    counts = df.groupby([filter]).size()
    # Let's visualize the sentiments
    fig = plt.figure(figsize=(6,6), dpi=100)
    ax = plt.subplot(111)
    counts.plot.pie(
        ax=ax, 
        autopct='%1.1f%%', 
        startangle=270, 
        fontsize=12, label=""
        )
    
    plt.title(title)
    path = "../public/static"
    output_path = os.path.join(path, output_name)
    plt.savefig(output_path)
    plt.close()

    print(f"[✔] Saved chart to: {output_path}")

def chart_flag_reasons(df, output_name='flag_reason_chart.png'):
    # select reason column and remove null values 
    reasons_series = df['reason'].dropna()
    reasons_series = reasons_series[reasons_series != "NOT FLAGGED"]

    all_reasons = []
    for reason in reasons_series:
        if isinstance(reason, list):
            # Shouldn't happen if reason was stored correctly, but just in case
            flag_labels = reason
        else:
            flag_labels = [r.strip() for r in str(reason).split(';')]

        for i in flag_labels:
            if i.startswith("KEYWORD"):
                all_reasons.append("KEYWORD")
            elif i:  # skip empty strings
                all_reasons.append(i)

    #count occurences 
    reason_counts = Counter(all_reasons)

    # Convert to DataFrame for plotting
    reasons_df = pd.DataFrame.from_dict(reason_counts, orient='index', columns=['count'])
    reasons_df = reasons_df.sort_values('count', ascending=False)

    # Plot as horizontal bar chart
    plt.figure(figsize=(10, 6))
    reasons_df.plot(kind='barh', legend=False, color='salmon')
    plt.title("Distribution of Flagging Reasons")
    plt.xlabel("Number of Entries")
    plt.ylabel("Reason")
    plt.gca().invert_yaxis()  # Most frequent at top
    plt.tight_layout()

    # Save the chart
    path = "../public/static"
    os.makedirs(path, exist_ok=True)
    output_path = os.path.join(path, output_name)
    plt.savefig(output_path)
    plt.close()

    print(f"[✔] Saved flag reason chart to: {output_path}")

def chart_keywords(df, output_name="top_flagged_keywords.png", title="Most Frequent Flagged Keywords"):
    flagged_df = df[df['flagged'] == True] #get only flagged items and put them into a dataframe

    # flatten and convert to a list 
    keyword_list = flagged_df['keywords'].explode().dropna().tolist()
    keyword_counts = Counter(keyword_list) #count occurences
    most_common = keyword_counts.most_common(10)   # Get most common keywords
    keywords, counts = [], []

    for i in most_common: 
        keywords.append(i[0])
        counts.append(i[1])

    # Plot
    plt.figure(figsize=(10, 6))
    plt.barh(keywords[::-1], counts[::-1], color='salmon')
    plt.title(title)
    plt.xlabel("Frequency")
    plt.tight_layout()

    # Save
    output_path = os.path.join("../public/static", output_name)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    plt.close() 

def run_analysis(): 
    df = load_data("content_log_cleaned.json")
    print(df) 
    create_wordcloud(df, reason_filter = None, output_name = 'all_inclusive_cloud.png', title = "all_inclusive_cloud")
    chart_distribution(df, filter = "sentiment", output_name = "sentiment_distribution.png", title = "Sentiment Distribution of All Entries")
    chart_distribution(df, filter = "flagged", output_name = "flagging_distribution.png", title = "Flagged vs. Non-Flagged of All Entries")
    chart_flag_reasons(df, output_name = 'flag_reason_chart.png')
    chart_keywords(df, output_name="top_flagged_keywords.png", title="Most Frequent Flagged Keywords")
    topic_model(df)

# if __name__ == "__main__":
#    run_analysis() 