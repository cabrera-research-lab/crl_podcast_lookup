import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()


# Load vector store
def load_qa():
    db = FAISS.load_local("video_index", OpenAIEmbeddings(), allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_type="similarity", k=3)
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

    return retriever, llm


@st.cache_data(show_spinner=False)
def query_transcripts(query):
    retriever, llm = load_qa()
    docs = retriever.get_relevant_documents(query)

    context = "".join([doc.page_content for doc in docs])
    prompt = PromptTemplate.from_template(
        """
        Use the following video transcript context to answer the user's question.

        Context:
        {context}

        Question: {question}
        Answer:
        """
    )

    final_prompt = prompt.format(context=context, question=query)
    response = llm.invoke(final_prompt)

    from collections import defaultdict

    video_map = defaultdict(lambda: {"title": "", "url": "", "desc": "", "date": "", "timestamps": []})

    for doc in docs:
        url = doc.metadata.get('video_url', '')
        title = doc.metadata.get('video_title', 'Unknown Title')
        desc = doc.metadata.get('episode_description', '')
        date = doc.metadata.get('episode_date', '')
        timestamp = doc.metadata.get('timestamp', 0)

        video_map[url]["title"] = title
        video_map[url]["url"] = url
        video_map[url]["desc"] = desc
        video_map[url]["date"] = date
        video_map[url]["timestamps"].append(timestamp)
        
    related_videos = []
    for video in video_map.values():
        video["timestamps"].sort()
        related_videos.append((video["title"], video["url"], video["desc"], video["date"], video["timestamps"]))

    return response.content, related_videos
