from extraction import scrape_glassdoor_reviews
from dotenv import load_dotenv
import os
import streamlit as st
import pandas as pd
from analysis import circular_progress_bar,three_circles_in_row,process_df
from generative_model import generate_content

load_dotenv() # Load environment variables from .env file

email = os.getenv("GLASSDOOR_EMAIL")
password = os.getenv("GLASSDOOR_PASSWORD")

st.title("GlassDoor Company Review Extraction & Sentiment Analysis")

company_name = st.text_input("Enter Company name",placeholder="Eg: Google")
name = company_name

max_page = st.text_input("Enter maximum number of pages to be extracted",placeholder="Default 5 pages",value='')

if max_page:
    if max_page.isdigit() and int(max_page) > 0:
        max_page = int(max_page)
    else:
        max_page = max_page
print(max_page)
# Create a submit button
if st.button("Extract"):
    if company_name:
        if isinstance(max_page,int):
            with st.spinner("Extracting. Please Wait..."):
                df = scrape_glassdoor_reviews(email=email,password=password,company_name=company_name,max_page=max_page)
            with st.spinner("Analysing the Review...."):
                df['rating'] = df['rating'].astype('float')
                rating = round(df['rating'].mean(),3)
                avg_pros,avg_cons,avg_total,advice,pros,cons = process_df(df)
                text = generate_content(company_name=name,rating=rating,sentiment_score=avg_total,advice=advice,pros=pros,cons=cons)
        
        
            st.success(f"{df.shape[0]} Reviews Extracted.")
            
            st.subheader("Result:")
            st.dataframe(df.head())
            


            csv = df.to_csv(index=False)
            
            st.download_button(label="Download Dataset as CSV",
                file_name=f"{company_name}_glassdoor_reviews.csv",
                mime="text/csv",data=csv )
            
            st.write("Average Rating")
            # combined_circles(value_left=rating,value_right1=avg_total,value_right2=avg_pros,value_right3=avg_cons,name2="Pros",name3="Cons",left_name="Rating",name1="Total Score")
            circular_progress_bar(value=rating,name="Rating")
            
            st.write("Average Sentiment Scores")
            three_circles_in_row(value1=avg_pros,name1="Pros",value2=avg_cons,name2="Cons",value3=avg_total,name3="Total Score")
            
            st.write(text)
            
        else:
            if max_page == "":
                with st.spinner("Extracting. Please Wait..."):
                    df = scrape_glassdoor_reviews(email=email,password=password,company_name=company_name)
                with st.spinner("Analysing the Review...."):
                    df['rating'] = df['rating'].astype('float')
                    rating = round(df['rating'].mean(),3)
                    avg_pros,avg_cons,avg_total,advice,pros,cons = process_df(df)
                    text = generate_content(company_name=name,rating=rating,sentiment_score=avg_total,advice=advice,pros=pros,cons=cons)
            
            
                st.success(f"{df.shape[0]} Reviews Extracted.")
                
                st.subheader("Result:")
                st.dataframe(df.head())
                


                csv = df.to_csv(index=False)
                
                st.download_button(label="Download Dataset as CSV",
                    file_name=f"{company_name}_glassdoor_reviews.csv",
                    mime="text/csv",data=csv )
                
                st.write("Average Rating")
                # combined_circles(value_left=rating,value_right1=avg_total,value_right2=avg_pros,value_right3=avg_cons,name2="Pros",name3="Cons",left_name="Rating",name1="Total Score")
                circular_progress_bar(value=rating,name="Rating")
                
                st.write("Average Sentiment Scores")
                three_circles_in_row(value1=avg_pros,name1="Pros",value2=avg_cons,name2="Cons",value3=avg_total,name3="Total Score")
                
                st.write(text)
            else:
                print(max_page)
                st.warning("Enter a valid Number")
            
        
        
        
       
    else:
        st.warning("Please enter some text before submitting.")
else:
    st.write("Enter text and click Submit to proceed.")