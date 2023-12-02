
import pandas as pd
import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy import text

from dotenv import load_dotenv
import openai
import os
import json


def create_table_definition(df):
    prompt = """### sqlite SQL table, with it properties:
    #
    # Tesla_Stock({})
    #
    """.format(",".join(str(col) for col in df.columns))
    return prompt

def prompt_input():
    nlp_text = input('Enter the question you want: ')
    return nlp_text


def combine_prompts(df, query_prompt):
    definition = create_table_definition(df)
    query_init_string = f'### A query to answer: {query_prompt}\nSELECT'
    return definition+query_init_string

def handle_response(response):
    query = response['choices'][0]['text']
    #print(response)
    if query.startswith(" "):
        query = "SELECT"+query
    return query

######################
##call the openai completion calls

###load ENV VARS
load_dotenv()
openai.api_key = os.getenv("OPEN_AI_KEY")
openai.organization = os.getenv("OPEN_AI_ORG")

##setup sql sqlalchemy
df = pd.read_csv('Tesla_Stock.csv')
tmp_db = create_engine('sqlite:///:memory:', echo=True)
data = df.to_sql(name='Tesla_Stock', con=tmp_db)
with tmp_db.connect() as conn:
    results = conn.execute(text('select max(Volume) from Tesla_Stock'))
    print("////////////////////////", results.all())
nlp_text = prompt_input()
#print(combine_prompts(df, nlp_text))

response = openai.Completion.create(
    model = "davinci-002",
    prompt = combine_prompts(df, nlp_text),
    temperature = 0,
    max_tokens = 150,
    top_p = 1.0,
    frequency_penalty=0,
    presence_penalty=0,
    stop= ['#',';']
)
res = handle_response(response)
print("query --> \n",res)
with tmp_db.connect() as conn:
    results = conn.execute(text(handle_response(response)))
    print("results -->\n", results.all())
