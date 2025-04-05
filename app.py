import streamlit as st
from query_module import query_transcripts
from urllib.parse import urlparse, parse_qs

st.set_page_config(page_title="CRL Pod Lookup", layout="wide")
st.title("CRL Podcast Lookup")

query = st.text_input("Ask a question based on our video content:")

if query:
    with st.spinner("Searching transcripts..."):
        answer, related_videos = query_transcripts(query)

    st.subheader("Lookup results")
    for title, url, desc, date, timestamps, reason in related_videos:
        st.markdown(f"### [{title}]({url})")
        st.markdown(f"🔍 **Why this episode:** {reason}")

        # Determine base video link format
        if "youtu.be" in url:
            base_link = url.split("?")[0]
            video_id = base_link.split("/")[-1]
        elif "watch?v=" in url:
            video_id = url.split("v=")[-1].split("&")[0]
            base_link = f"https://youtu.be/{video_id}"
        else:
            base_link = url  # fallback
            video_id = ""

        # Format and display inline timestamps
        if timestamps:
            formatted_links = []
            for t in timestamps:
                mins, secs = divmod(t, 60)
                label = f"{mins}:{secs:02d}"
                timestamp_link = f"{base_link}?t={t}"
                formatted_link = f"[{label}]({timestamp_link})"

                if formatted_link not in formatted_links:
                    formatted_links.append(formatted_link)

            st.markdown("⏱️ <span style='color:#f39c12;'>[BETA]</span> Jump to: " + " • ".join(formatted_links),
                        unsafe_allow_html=True)

        # Embed the video
        if video_id:
            st.video(f"https://www.youtube.com/embed/{video_id}?start={timestamps[0]}")
