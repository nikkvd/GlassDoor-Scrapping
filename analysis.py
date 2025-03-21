import streamlit as st
import pandas as pd
import numpy as np
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('vader_lexicon')
from nltk.tokenize import word_tokenize

def process_df(df):
    df['date'] = pd.to_datetime(df['date'])
    
    def cleaning(text):
        text = text.lower()
        return text.replace("\n"," ").replace("\r","").replace('-',"")
    
    df['pros_clean'] = df['pros'].apply(cleaning)
    df['cons_clean'] = df['cons'].apply(cleaning)
    
    def tokenize(text):
        text = word_tokenize(text)
        text = ' '.join(text)
        return text
    
    df['pros_clean'] = df['pros_clean'].apply(tokenize)
    df['cons_clean'] = df['cons_clean'].apply(tokenize)
    
    
    analyzer = SentimentIntensityAnalyzer()
    df['pros_score'] = df['pros_clean'].apply(analyzer.polarity_scores)
    df['cons_score'] = df['cons_clean'].apply(analyzer.polarity_scores)
    
    df['pros_score'] = df['pros_score'].apply(lambda x: x['compound'])
    df['cons_score'] = df['cons_score'].apply(lambda x: x['compound'])

    
    avg_pros = round(df['pros_score'].mean(),3)
    avg_cons = round(df['cons_score'].mean(),3)
    
    avg_total = round((df['pros_score']-df['cons_score']).mean(),3)
    
    advice = df['advice'].to_list()
    text = ''
    for sent in advice:
        text += '//' + str(sent)
    text = text.replace('//nan','')
    
    
    return avg_pros,avg_cons,avg_total,text


def three_circles_in_row(value1, value2, value3,name1,name2,name3):
    # Ensure values are between -1 and 1
    value1 = max(-1, min(1, value1))
    value2 = max(-1, min(1, value2))
    value3 = max(-1, min(1, value3))
    
    # Calculate percentages (-1 to 1 mapped to 0-100%)
    percentage1 = ((value1 + 1) / 2) * 100
    percentage2 = ((value2 + 1) / 2) * 100
    percentage3 = ((value3 + 1) / 2) * 100
    
    # Colors for circles (red to yellow to green)
    def get_color(value):
        if value <= 0:
            red = 255
            green = int(255 * (value + 1) / 1)
        else:
            red = int(255 * (1 - value) / 1)
            green = 255
        return f'#{red:02x}{green:02x}00'
    
    color1 = get_color(value1)
    color2 = get_color(value2)
    color3 = get_color(value3)
    
    html_code = f"""
    <div style="
        display: flex;
        justify-content: center;
        gap: 40px;
        margin: 20px 0;">
        
        <!-- Circle 1 -->
        <div style="position: relative; width: 100px; height: 140px; text-align: center;">
            <div style="position: relative; width: 100px; height: 100px;">
                <svg width="100" height="100">
                    <circle r="45" cx="50" cy="50" fill="transparent" stroke="#e0e0e0" stroke-width="10"/>
                    <circle r="45" cx="50" cy="50" fill="transparent" stroke="{color1}" 
                            stroke-width="10" stroke-dasharray="{percentage1 * 2.83} 283" 
                            transform="rotate(-90 50 50)"/>
                </svg>
                <div style="
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-size: 24px;
                    font-weight: bold;
                    color: white;">
                    {value1:+.2f}
                </div>
            </div>
            <div style="margin-top: 5px; font-size: 16px; color: white;">{name1}</div>
        </div>
        
        <!-- Circle 2 -->
        <div style="position: relative; width: 100px; height: 140px; text-align: center;">
            <div style="position: relative; width: 100px; height: 100px;">
                <svg width="100" height="100">
                    <circle r="45" cx="50" cy="50" fill="transparent" stroke="#e0e0e0" stroke-width="10"/>
                    <circle r="45" cx="50" cy="50" fill="transparent" stroke="{color2}" 
                            stroke-width="10" stroke-dasharray="{percentage2 * 2.83} 283" 
                            transform="rotate(-90 50 50)"/>
                </svg>
                <div style="
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-size: 24px;
                    font-weight: bold;
                    color: white;">
                    {value2:+.2f}
                </div>
            </div>
            <div style="margin-top: 5px; font-size: 16px; color: white;">{name2}</div>
        </div>
        
        <!-- Circle 3 -->
        <div style="position: relative; width: 100px; height: 140px; text-align: center;">
            <div style="position: relative; width: 100px; height: 100px;">
                <svg width="100" height="100">
                    <circle r="45" cx="50" cy="50" fill="transparent" stroke="#e0e0e0" stroke-width="10"/>
                    <circle r="45" cx="50" cy="50" fill="transparent" stroke="{color3}" 
                            stroke-width="10" stroke-dasharray="{percentage3 * 2.83} 283" 
                            transform="rotate(-90 50 50)"/>
                </svg>
                <div style="
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-size: 24px;
                    font-weight: bold;
                    color: white;">
                    {value3:+.2f}
                </div>
            </div>
            <div style="margin-top: 5px; font-size: 16px; color: white;">{name3}</div>
        </div>
    </div>
    """
    
    st.components.v1.html(html_code, height=190)
    
    
def circular_progress_bar(value,name):
    # Ensure value is between 1 and 5
    value = max(1, min(5, value))
    
    # Calculate percentage (1-5 mapped to 0-100%)
    percentage = ((value - 1) / 4) * 100
    
    # Calculate color gradient from red (#FF0000) to green (#00FF00)
    red = int(255 * (1 - (value - 1) / 4))
    green = int(255 * ((value - 1) / 4))
    color = f'#{red:02x}{green:02x}00'
    
    html_code = f"""
    <div style="
        position: relative;
        width: 100px;
        height: 100px;
        margin: 20px auto;">
        <svg width="100" height="100">
            <circle
                r="45"
                cx="50"
                cy="50"
                fill="transparent"
                stroke="#e0e0e0"
                stroke-width="10"/>
            <circle
                r="45"
                cx="50"
                cy="50"
                fill="transparent"
                stroke="{color}"
                stroke-width="10"
                stroke-dasharray="{percentage * 2.83} 283"
                transform="rotate(-90 50 50)"/>
        </svg>
        <div style="
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 24px;
            font-weight: bold; color: white;">
            {value:+.2f}
        </div>
        <div style="margin-top: 5px; font-size: 16px; color: white;">{name}</div>
    </div>
    """
    
    st.components.v1.html(html_code, height=150)