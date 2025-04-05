from langchain_community.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
import streamlit as st
from collections import defaultdict


# Load vector store
def load_qa():
    db = FAISS.load_local("video_index", OpenAIEmbeddings(openai_api_key=st.secrets["openai_api_key"]),
                          allow_dangerous_deserialization=True)
    retriever = db.as_retriever(search_type="similarity", k=3)
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", openai_api_key=st.secrets["openai_api_key"])
    return retriever, llm


@st.cache_data(show_spinner=False)
def query_transcripts(query):
    retriever, llm = load_qa()
    docs = retriever.get_relevant_documents(query)

    context = "\n\n".join([doc.page_content for doc in docs])
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

    video_map = defaultdict(lambda: {"title": "", "url": "", "desc": "", "date": "", "timestamps": [], "reasons": []})

    for doc in docs:
        meta = doc.metadata
        url = meta.get("video_url", "")
        video_map[url]["title"] = meta.get("video_title", "Unknown Title")
        video_map[url]["url"] = url
        video_map[url]["desc"] = meta.get("episode_description", "")
        video_map[url]["date"] = meta.get("episode_date", "")
        video_map[url]["timestamps"].append(meta.get("timestamp", 0))

        # Add a snippet as the reason
        snippet = doc.page_content.strip().split("\n")[0][:160] + "..."
        video_map[url]["reasons"].append(snippet)

    related_videos = []
    for v in video_map.values():
        reason_summary = v["reasons"][0] if v["reasons"] else "Matched based on relevant transcript content."
        v["timestamps"].sort()
        related_videos.append((v["title"], v["url"], v["desc"], v["date"], v["timestamps"], reason_summary))

    return response.content, related_videos
