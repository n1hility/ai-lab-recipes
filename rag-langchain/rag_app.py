from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma

from chromadb import HttpClient
from chromadb.config import Settings
import chromadb.utils.embedding_functions as embedding_functions

import streamlit as st

import uuid
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--docs", default="data/fake_meeting.txt")
parser.add_argument("-c", "--chunk_size", default=150)
parser.add_argument("-e", "--embedding_model", default="BAAI/bge-base-en-v1.5")
parser.add_argument("-H", "--vdb_host", default="0.0.0.0")
parser.add_argument("-p", "--vdb_port", default="8000")
parser.add_argument("-n", "--name", default="test_collection")
parser.add_argument("-m", "--model_url", default="http://0.0.0.0:8001/v1")
args = parser.parse_args()

### populate the DB ####
os.environ["TOKENIZERS_PARALLELISM"] = "false"

embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=args.embedding_model)
e = SentenceTransformerEmbeddings(model_name=args.embedding_model)
client = HttpClient(host=args.vdb_host,
                             port=args.vdb_port,
                             settings=Settings(allow_reset=True,))
collection = client.get_or_create_collection(args.name,
                                      embedding_function=embedding_func)

if collection.count() < 1:
    print("populating db")
    raw_documents = TextLoader(args.docs).load()
    text_splitter = CharacterTextSplitter(separator = ".",
                                          chunk_size=int(args.chunk_size),
                                          chunk_overlap=0)
    docs = text_splitter.split_documents(raw_documents) 
    for doc in docs:
        collection.add(
            ids=[str(uuid.uuid1())],
            metadatas=doc.metadata, 
            documents=doc.page_content
            )
else:
    print("DB already populated")
########################
    
#### Define RAG App ####

st.title("📚 RAG DEMO")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", 
                                     "content": "How can I help you?"}]
    
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

db = Chroma(client=client,
            collection_name=args.name,
            embedding_function=e
    )
retriever = db.as_retriever(threshold=0.75)

llm = ChatOpenAI(base_url=args.model_url, 
                 api_key="EMPTY",
                 streaming=True,
                 callbacks=[StreamlitCallbackHandler(st.container(),
                                                     collapse_completed_thoughts=True)])

prompt = ChatPromptTemplate.from_template("""Answer the question based only on the following context:
{context}

Question: {input}
"""
)

chain = (
    {"context": retriever, "input": RunnablePassthrough()}
    | prompt
    | llm
)

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    response = chain.invoke(prompt)
    st.chat_message("assistant").markdown(response.content)    
    st.session_state.messages.append({"role": "assistant", "content": response.content})
    st.rerun()
