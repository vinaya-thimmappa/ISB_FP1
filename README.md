# ISB_FP1
# Stock Price Prediction with Regression Model

This repository contains a machine learning project for predicting stock prices using a regression model. The project includes a Streamlit application for a user-friendly frontend interface.

## TODO
Data collection automation 
Model running should be part of ETL Pipeline, Currently it is manually running and generates CSV Files 
This csv file is given has input to frontend which reads and then display the needed graph 

## Project Overview

The goal of this project is to use historical stock price data to predict future prices by applying regression analysis. The machine learning model is trained on features like historical prices, volume, and possibly other financial indicators.
We have  used selenium for all scrapping and also headless chrome. This helps to get the data from new site and do  sentiment analysis on top it 

## Features

- Data processing and analysis using pandas.
- Implementation of a regression model for prediction.
- Interactive Streamlit frontend for visualizing predictions and historical data.
- Plotly for creating dynamic and responsive charts.

## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

- Python 3.6+
- Pip package manager

### Installation

1. Clone the repo
> git clone [[https://github.com/vinaya-thimmappa/ISB_FP1](https://github.com/vinaya-thimmappa/ISB_FP1) 
2. Install required packages
> pip3 install yahoo_fin
> pip3 install yfinance
> pip3 install selenium> pip3 install chrome
> pip3 install dateparser
> pip3 install sklearn

3. Run the Streamlit application locally:
> > streamlit run group_12_frontend.py

## Model

The regression model takes into account various features to predict stock prices. It can be trained on a daily, weekly, or monthly basis, and can predict next day's closing price or other future metrics.

### Description
This repository contains a Python script for predicting stock prices using a regression model. The model is designed to analyze historical price data and identify patterns that can be used to forecast future stock prices.

### How It Works
The `fp1-modelling.py` script processes historical stock data, applies a regression analysis algorithm, and outputs predictions for future stock prices. It includes data preprocessing, model training, evaluation, and prediction components.

### Requirements
- Python 3.7+
- pandas
- numpy
- scikit-learn
- matplotlib

Install all required packages using the following command:
```bash
pip install -r requirements.txt
```

> python fp1-modelling.py

### Features
- Data preprocessing and cleaning.
- Regression analysis for prediction.
- Evaluation of model performance.
- Visualization of historical data and predicted prices

## Frontend

The Streamlit application provides an interface for:

- Visualizing historical stock data.
- Displaying the predicted stock prices.
- Customizing the inputs for different stocks and timeframes.
- New Associated with Stock Price 




## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

## License
No License.. Use it , make it better, make your life better 




