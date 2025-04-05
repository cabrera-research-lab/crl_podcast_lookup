import streamlit as st
from query_module import query_transcripts
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="CRL Pod Lookup", layout="wide")
st.title("CRL Podcast Lookup")

query = st.text_input("Ask a question based on our video content:")

if query:
    with st.spinner("Searching transcripts..."):
        answer, related_videos = query_transcripts(query)

    st.subheader("Answer")
    st.write(answer)

    st.subheader("Related Videos")
    for title, url, desc, date, timestamps in related_videos:
        st.markdown(f"### [{title}]({url})")
        st.markdown(f"📅 **Date:** {date}")
        st.markdown(f"📝 {desc}")

        video_id = url.split("v=")[-1].split("&")[0]

        for timestamp in timestamps:
            url_with_time = f"{url}&t={timestamp}s" if "&" in url else f"{url}?t={timestamp}s"
            st.markdown(f"⏱️ Jump to [timestamp]({url_with_time}) → `{timestamp}` seconds")

        if timestamps:
            st.video(f"https://www.youtube.com/embed/{video_id}?start={timestamps[0]}")
        else:
            st.video(f"https://www.youtube.com/embed/{video_id}")