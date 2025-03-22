from langchain import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# API Key
api_key = os.getenv("GOOGLE_API_KEY")

model = ChatGoogleGenerativeAI(api_key=api_key,model='gemini-1.5-flash')

def generate_content(company_name,rating,sentiment_score,advice,pros,cons):
    prompt_content = '''the average sentiment score of {company_name} company reviews (pros - cons) is {sentiment_score}, average rating is {rating}, {advice} these are the advices people give,
                {pros} these are the pros people mentioned and {cons} these are the cons people mentioned.
                write inference of this. write it in a good structured format and return nothing else'''
    template = PromptTemplate(input_variables = ['company_name','sentiment_score','rating','pros','cons'],
                          template=prompt_content)
    
    prompt = template.format(company_name=company_name,rating=rating,sentiment_score=sentiment_score,advice=advice,pros=pros,cons=cons)
    content = model.predict(text=prompt)
    return content