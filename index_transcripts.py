from langchain.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

TRANSCRIPTS_DIR = "data/transcripts"
METADATA_CSV = "data/episode_metadata.csv"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
SECONDS_PER_TOKEN = 0.25  # rough estimation for 4 tokens per second of speech


def load_metadata():
    df = pd.read_csv(METADATA_CSV)
    metadata_map = {}
    for _, row in df.iterrows():
        key = str(row["Episode Number"])
        metadata_map[key] = {
            "video_title": row["Episode Title"],
            "episode_description": row["Episode Description"],
            "video_url": row["Episode URL"],
            "episode_date": row["Episode Date"]
        }
    return metadata_map


def index_all_transcripts():
    documents = []
    metadata_map = load_metadata()

    for filename in os.listdir(TRANSCRIPTS_DIR):
        if filename.endswith(".docx"):
            episode_number = ''.join(filter(str.isdigit, filename))
            if episode_number not in metadata_map:
                continue  # skip transcripts with no metadata entry

            meta = metadata_map.get(episode_number, {})
            path = os.path.join(TRANSCRIPTS_DIR, filename)
            loader = Docx2txtLoader(path)
            docs = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
            splits = text_splitter.split_documents(docs)

            for i, doc in enumerate(splits):
                doc.metadata.update(meta)
                start_seconds = int(i * (CHUNK_SIZE - CHUNK_OVERLAP) * SECONDS_PER_TOKEN)
                doc.metadata['timestamp'] = start_seconds

            documents.extend(splits)

    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(documents, embeddings)
    db.save_local("video_index")
    print("Indexing complete.")

if __name__ == "__main__":
    index_all_transcripts()