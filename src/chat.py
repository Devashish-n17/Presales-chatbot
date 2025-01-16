import os, json
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain.schema import Document, HumanMessage, AIMessage
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_google_community import GoogleSearchAPIWrapper
from db.db_conversations import store_conversation, get_last_conversations
from rich import print

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
embeddings = GoogleGenerativeAIEmbeddings(model='models/text-embedding-004', google_api_key=GEMINI_API_KEY)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)
vector_store = Chroma(collection_name='sales', embedding_function=embeddings, persist_directory='./chroma_db')
search = GoogleSearchAPIWrapper()


entities = None
prompt = None
def initialize_entities_and_prompt():
    global entities, prompt
    if entities is None:
        entities = load_entities()
    if prompt is None:
        prompt = create_prompt_template(entities)

    return prompt


def process_user_query(vector_store, user_query, chat_history, k=5):
    retriever = vector_store.as_retriever(search_kwargs={"k": k})

    docs = retriever.invoke(user_query)
    relevant_chunks = [doc.page_content for doc in docs[:k]]
    source_list = [doc.metadata["file_path"] for doc in docs[:k]]
    sources = list(set(source_list))
    print(f"Source: {sources}")

    chunks_text = "\n\n".join([f"Chunk {i+1}:\n{chunk}" for i, chunk in enumerate(relevant_chunks)])

    formatted_prompt = prompt.format_prompt(
        input=user_query,
        chat_history=chat_history,
        chunks=chunks_text,
        entities=json.dumps(entities, indent=2)
    )
    response = llm.invoke(formatted_prompt)
    return response.content, sources


def format_chat_history(past_conversations):
    chat_history = []
    for conv in past_conversations:
        chat_history.extend([HumanMessage(content=conv[0]), AIMessage(content=conv[1])])
    return chat_history


def load_entities():
    with open('d:/prod/fastapi/Metadata.json', 'r') as file:
        return json.load(file)


def create_prompt_template(entities):
    template = f"""
        YOU ARE AN AI DEDICATED TO PROVIDE DETAILS REGARDING SPECIFIC DOCUMENTS, 
        ALWAYS OUTPUT FILE NAME AND FILE PATH FIRST OF MATCHED DOCUMENTS FROM METADATA.
        ADD THE DETAILS OF THE FILES MENTIONED BELOW IN 4 TO 5 LINES REGARDING THE TOPIC.
        
        GENERATE YOUR ANSWER AND WRITE IT IN A PROFESSIONAL MANNER
        
        Strictly write the answer in this format.
        - FORMAT -
        
        **Entities: {entities}**
        - File 1:
        - File Name: <file_name from Metadata>
        - File Path: <resource_url from Metadata>

        - File 2:
        - File Name: <file_name from Metadata>
        - File Path: <resource_url from Metadata>
        
        and so on
        
        LIST ALL ENTIIES POSSIBLE AND If the entities do not exist, STRICTLY REPLY: "Match Not Found."
        
        ---
        Additional Context:
        - Current Question: {input}
        
    """
    return ChatPromptTemplate.from_messages([
        ("system", template),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])


def web_search(prompt):
    results = search.results(prompt, num_results=4)
    web_results = []
    for result in results:
        web_results.append({"Title": result['title'], "Link":result['link']})

    return json.dumps(web_results)
 

def main(last_prompt):
    prompt = initialize_entities_and_prompt()

    user_query = last_prompt

    past_conversations = get_last_conversations()
    chat_history = format_chat_history(past_conversations)

    answer, sources = process_user_query(vector_store, user_query, chat_history)
    # print(f"\nAnswer: {sources}")
    # print(f"\nAnswer: {answer}")
    store_conversation(user_query, answer)

    return answer, sources

if __name__ == "__main__":
    while True:
        que = input('Ask: ')
        if que =='exit': break
        ans, source = main(que)
        print(f'\n{ans}, {source}\n')
