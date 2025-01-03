import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001', google_api_key=GEMINI_API_KEY)
search = GoogleSearchAPIWrapper()

collection_name = 'sales'
persist_directory = './chroma_db'
vector_store = Chroma(collection_name=collection_name, embedding_function=embeddings, persist_directory=persist_directory)

while True:
    print('\n')
    question = input('Ask : ')
    if question.lower() == 'exit': break

    results = vector_store.similarity_search_with_score(question)
    for res, score in results:
        print(res.metadata, f'Score : {score:3f}')

    web_search = input('Do you want results from web? : ')
    if web_search.lower() == 'yes':
        results = search.results(question, num_results=4)
        for result in results:
            print(f"Title: {result['title']}")
            print(f"URL: {result['link']}")
            print(f"Snippet: {result['snippet']}\n")
    
'''
- Chat History
- Summary of each output doc
- Answer in PPT format
- 
'''