# -*- coding: utf-8 -*-
"""FP1_Modelling.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NLAfLOnSNIOGevE8F52zMyexRuxfuUMW
"""
# Installing the required packages

#pip3 install yahoo_fin
#pip3 install yfinance
#pip3 install selenium
#pip3 install chrome
#pip3 install dateparser
#pip3 install sklearn

# Importaing the required packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import warnings
warnings.filterwarnings("ignore")
import yfinance as yf
import time
import re
import nltk
import dateparser
import datetime
import scipy.stats as stats

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
from dateutil import parser
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.metrics import accuracy_score, classification_report, cohen_kappa_score

# Download NLTK resources
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('vader_lexicon')

"""
Scrapes Google News for headlines related to a given query.

Args:
    query (str): The search query.
    scroll_count (int, optional): The number of times to scroll down the page to load more articles. 
        Defaults to 50.

Returns:
    list: A list of dictionaries containing the extracted headlines and timestamps.
        Each dictionary has the keys 'Headline' and 'Timestamp'.
"""

def scrape_google_news_headlines(query, scroll_count=50):
    # Initialize the Chrome driver
    driver = webdriver.Chrome()

    # Construct the URL
    url = f"https://news.google.com/search?q={query}&hl=en-IN&gl=IN&ceid=IN%3Aen"
    driver.get(url)

    # Scroll down the page to load more articles
    body_element = driver.find_element(By.TAG_NAME, 'body')

    for _ in range(scroll_count):
        body_element.send_keys(Keys.PAGE_DOWN)
        time.sleep(2)  # Add a 2-second delay after each scroll

    # Extract the headlines and timestamps
    data = []
    articles = driver.find_elements(By.XPATH, '//article')
    for article in articles:
        try:
            headline_element = article.find_element(By.XPATH, './/a[@class="JtKRv"]')
            timestamp_element = article.find_element(By.XPATH, './/time[@class="hvbAAd"]')

            headline = headline_element.text
            timestamp = timestamp_element.get_attribute('datetime')

            data.append({'Headline': headline, 'Timestamp': timestamp})
        except Exception as e:
            print(f"Error extracting headline or timestamp: {e}")

    driver.quit()
    return data

# Scrape and display articles with timestamps
query = "HDFCBANK"
data = scrape_google_news_headlines(query)
print(data)  # Check if there's data here
google = pd.DataFrame(data, columns=['Headline','Timestamp'])

google

"""
    Preprocesses the given text by removing URLs, special characters, numbers,
    converting to lowercase, tokenizing, removing stop words, lemmatizing, and
    joining the lemmatized tokens back into a single string.

    Args:
        text (str): The text to be preprocessed.

    Returns:
        str: The preprocessed text.
"""

# Instantiate the lemmatizer
lemmatizer = WordNetLemmatizer()

# Get the set of English stop words
stop_words = set(stopwords.words('english'))

# Assuming you have already imported the 'google' DataFrame

def preprocess_text(text):
    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)

    # Remove special characters and numbers
    text = re.sub(r"[^\w\s]", "", text)

    # Convert to lowercase
    text = text.lower()

    # Tokenize the text
    tokens = nltk.word_tokenize(text)

    # Remove stop words
    tokens = [word for word in tokens if word not in stop_words]

    # Lemmatize each word in the tokens list
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in tokens]

    # Join the lemmatized tokens back into a single string
    lemmatized_text = ' '.join(lemmatized_tokens)

    return lemmatized_text

# Apply the preprocessing function to the 'Headline' column
google['processed_headline'] = google['Headline'].apply(preprocess_text)

google

"""
    Analyzes the sentiment of the given text and returns a corresponding sentiment label.

    Parameters:
        text (str): The text to be analyzed.

    Returns:
        str: The sentiment label ('positive', 'negative', or 'neutral') based on the sentiment polarity of the text.
    """
# generate the Labels for the Model Building

def get_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity < 0:
        return 'negative'
    else:
        return 'neutral'

google['sentiment'] = google['processed_headline'].apply(get_sentiment)

google.head()

#google.sentiment.value_counts().plot(kind = "bar")

# Plot the sentiment distribution
plt.figure(figsize=(8, 6))
sns.histplot(data=google, x='sentiment', bins=25, kde=False)
plt.xlabel('Sentiment')
plt.ylabel('Count')
plt.title('Sentiment Distribution')
plt.show()

# Extract named entities using NLTK

"""
    Extracts named entities from the given text.

    Args:
        text (str): The input text.

    Returns:
        list: A list of named entities found in the text.
    """
def extract_named_entities(text):
    sentences = nltk.sent_tokenize(text)
    tokenized_sentences = [nltk.word_tokenize(sent) for sent in sentences]
    tagged_sentences = [nltk.pos_tag(tokens) for tokens in tokenized_sentences]
    named_entities = []
    for tagged_sentence in tagged_sentences:
        chunked_sentence = nltk.ne_chunk(tagged_sentence)
        for chunk in chunked_sentence:
            if hasattr(chunk, 'label'):
                named_entities.append(' '.join(c[0] for c in chunk))
    return named_entities

google['NE_Headline'] = google['Headline'].apply(extract_named_entities)

google.head()

filtered = google[google.NE_Headline.apply(lambda x: len(x)>0)]

filtered.shape

# Lets remove the list from the NER Tags

def remove_list(text):
    return(' '.join(text))

filtered["NE_Headline"] = filtered.NE_Headline.apply(remove_list)

filtered.head()

filtered.NE_Headline.unique()

date_list = []
month_list = []
year_list = []

list_dates = list(filtered.Timestamp)

for item in filtered.Timestamp:
    if isinstance(item, datetime.date):
        date_list.append(item.day)
        month_list.append(item.month)
        year_list.append(item.year)
    elif isinstance(item, str):
        date_obj = dateparser.parse(item)
        if date_obj and date_obj.year:
            date_list.append(date_obj.day)
            month_list.append(date_obj.month)
            year_list.append(date_obj.year)
        else:
            date_list.append(None)
            month_list.append(None)
            year_list.append(None)

filtered["Date"] = pd.Series(date_list)
filtered["Month"] = pd.Series(month_list)
filtered["Year"] = pd.Series(year_list)

filtered.head(10)

filtered.isnull().sum()

# Imputting Missing Values using FFill()
final = filtered.ffill()

final.tail()

# Get subjectivity

def Subjectivity(x):
    return(TextBlob(x).sentiment.subjectivity)

def Polarity(x):
    return(TextBlob(x).sentiment.polarity)

final["Subjectivity"] = final.processed_headline.apply(Subjectivity)

final["Polarity"] = final.processed_headline.apply(Polarity)

final.processed_headline.value_counts()[:5]

final.to_csv("FinalHeadlines.csv", index = False)

modelling_data = final.drop(['Headline', "Timestamp", "processed_headline"], axis = 1)

modelling_data.head()

# Split the Data in train and test

features = modelling_data.drop(["sentiment"],axis = 1)

labels = modelling_data['sentiment']
X_train, X_test, y_train, y_test = train_test_split(pd.get_dummies(features,drop_first = True),
                                                    labels,
                                                    test_size=0.2, random_state=42)

# Random Forest Report
rf = RandomForestClassifier()

rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print("Accuracy: RF", accuracy)
print("Classification Report: RF")
print(report)

# GBM Model

gbm = GradientBoostingClassifier()

gbm.fit(X_train, y_train)
y_pred = gbm.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print("Accuracy: GB", accuracy)
print("Classification Report: GB")
print(report)

lg = LogisticRegression()

lg.fit(X_train, y_train)
y_pred = lg.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print("Accuracy: LR", accuracy)
print("Classification Report: LR")
print(report)

# Define the ticker symbol for HDFC Bank (HDFCBANK.NS for NSE)
ticker_symbol = "HDFCBANK.NS"

# Define the start and end dates for the data
start_date = "2020-01-01"
end_date = "2024-01-14"

# Fetch historical stock data using yfinance
hdfc_data = yf.download(ticker_symbol, start=start_date, end=end_date)

# Check the structure of the DataFrame
print(hdfc_data.head())

# Extract the year from the index and create a 'Year' column
hdfc_data['Year'] = hdfc_data.index.year

# Print the modified DataFrame
print(hdfc_data.head())

# year...

def sentiments(text):
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)
    return(sentiment)


# Create the SentimentIntensityAnalyzer instance
sia = SentimentIntensityAnalyzer()

# Test the sentiment analysis
scores = sia.polarity_scores("The book is lying under the shelf")
print(scores)

# get Sentiment

def get_sentiments(text):
    sia = SentimentIntensityAnalyzer()
    scores = sia.polarity_scores(text)
    return scores

neutral = []
negative = []
positive = []

for sentiment in modelling_data["sentiment"]:
    SIA = get_sentiments(sentiment)
    neutral.append(SIA['neu'])
    negative.append(SIA['neg'])
    positive.append(SIA['pos'])

modelling_data["Positive"] = positive
modelling_data["Negative"] = negative
modelling_data["Neutral"] = neutral

modelling_data.head()

hdfc_data.drop(['Adj Close', 'Volume'], axis = 1, inplace = True)

new = pd.merge(left = modelling_data, right = hdfc_data, on = "Year", how = "left").dropna()

hdfc_data.head()

new = hdfc_data[~(hdfc_data.duplicated())]

new['diff']=new['Close']-new['Open']

new.head()

new['target'] = np.where(new['diff'] > 0, 1, 0)

print((modelling_data['sentiment'] == "positive"))
print(len(new['diff'] > 0))
print((modelling_data['sentiment'] == "negative"))
print(len(new['diff'] < 0))

# Convert the "Date" column in 'modelling_data' to datetime format
modelling_data['Date'] = pd.to_datetime(modelling_data['Date'])

# Merge the dataframes on the 'Date' column
new = pd.merge(new, modelling_data[['Date', 'sentiment']], on='Date', how='left')

# Add conditions as boolean values to existing columns
new['positive_condition'] = modelling_data['sentiment'] == "positive"
new['negative_condition'] = modelling_data['sentiment'] == "negative"
new['neutral_condition']=modelling_data['sentiment']=="neutral"

# Display the updated 'new' dataframe
print(new)

new.head()

# Set "target" column based on conditions
new.loc[(new['positive_condition']) & (new['diff'] > 0), "target"] = 1
new.loc[(new['negative_condition']) & (new['diff'] < 0), "target"] = 0

# Display the updated 'new' dataframe
print(new)

# Create a new DataFrame with only the 'target' column
target_df = new[['target'].head(100)]

# Save the DataFrame with only the 'target' column to a CSV file
target_file_path = 'target_column.csv'
target_df.to_csv(target_file_path, index=False, header=['target'])  # header=['target'] adds a header to the CSV file

print(f"Target column saved to {target_file_path}")

final = new[new.target.notnull()]

final.head()

tbl = pd.crosstab(modelling_data.NE_Headline, final.target)
teststats, pvalue, dof, exp_freq = stats.chi2_contingency(tbl)

print(pvalue)

tbl

tbl = pd.crosstab(modelling_data.NE_Headline, final.target)
teststats, pvalue, dof, exp_freq = stats.chi2_contingency(tbl)

print(pvalue)

target_column = 'target'

# Drop any rows with missing values in the target column
final = final.dropna(subset=[target_column])

# Select features (X) and target variable (y)
X = final[['Open', 'High', 'Low', 'Close', 'Year', 'diff', 'positive_condition', 'negative_condition', 'neutral_condition']]
y = final[target_column]

# Handle missing values in features
X = X.fillna(0)  # You might need a more sophisticated imputation strategy

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a logistic regression model
lg = LogisticRegression()

# Fit the model on the training data
lg.fit(X_train, y_train)

# Make predictions on the test data
y_pred = lg.predict(X_test)

# Evaluate the model
print("Accuracy Score: LR", accuracy_score(y_test, y_pred))
print("Classification Report: LR")
print(classification_report(y_test, y_pred))
print("Cohen's Kappa Score: LR", cohen_kappa_score(y_test, y_pred))

#Creating the y-test file
target_df = new[['target']]
target_df_100 = target_df.head(100)
# Save the DataFrame with only the 'target' column to a CSV file
target_file_path = 'data/ytest.csv'
target_df_100.to_csv(target_file_path, index=False, header=['target'])  # header=['target'] adds a header to the CSV file

print(f"Target column saved to {target_file_path}")


google['sentiment'] = google['processed_headline'].apply(get_sentiment)

# Create a new DataFrame with only the 'sentiment' column
sentiment_df = google[['sentiment']]

# Map sentiment values to binary values
sentiment_df['sentiment'] = sentiment_df['sentiment'].map({'neutral': 0, 'positive': 1, 'negative': -1})

# Save the DataFrame with only the 'sentiment' column to a CSV file
sentiment_file_path = 'data/labels.csv'
sentiment_df.to_csv(sentiment_file_path, index=False, header=['sentiment'])  # header=['sentiment'] adds a header to the CSV file

print(f"Sentiment column saved to {sentiment_file_path}")
