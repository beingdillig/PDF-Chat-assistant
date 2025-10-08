"""Streamlit UI for PDF RAG system."""
import streamlit as st
import requests
import uuid

API_URL = "http://127.0.0.1:8000"

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("PDF Chat Assistant")

with st.sidebar:
    st.header("Settings")
    
    # Session management
    if st.button("New Session"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    
    st.text(f"Session: {st.session_state.session_id[:8]}...")
    
    # Upload PDFs
    st.header("Upload PDFs")
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if st.button(f"Process {uploaded_file.name}"):
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    files = {"file": uploaded_file.getvalue()}
                    response = requests.post(
                        f"{API_URL}/upload",
                        files={"file": (uploaded_file.name, uploaded_file, "application/pdf")},
                        params={"session_id": st.session_state.session_id}
                    )
                    if response.ok:
                        st.success(f"✓ {uploaded_file.name} processed!")
                    else:
                        st.error(f"Error: {response.text}")
    
    # Show documents
    st.header("Documents")
    try:
        docs_response = requests.get(
            f"{API_URL}/documents",
            params={"session_id": st.session_state.session_id}
        )
        if docs_response.ok:
            docs = docs_response.json()
            for doc in docs:
                st.text(f"📄 {doc['filename']}")
                st.caption(f"Pages: {doc['page_count']}, Status: {doc['status']}")
    except:
        st.caption("No documents yet")
    
    # Settings
    st.header("Query Settings")
    top_k = st.slider("Top K Results", 1, 10, 5)

# Chat interface
st.header("Chat")

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        # Show sources for assistant messages
        if message["role"] == "assistant" and "sources" in message:
            with st.expander("View Sources"):
                for i, source in enumerate(message["sources"], 1):
                    st.markdown(f"**Source {i}:** {source['filename']} (Page {source['page']})")
                    st.caption(source['text'])
                    st.divider()

# Chat input
if prompt := st.chat_input("Ask a question about your PDFs..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/query",
                    json={
                        "query": prompt,
                        "session_id": st.session_state.session_id,
                        "top_k": top_k
                    }
                )
                
                if response.ok:
                    data = response.json()
                    answer = data["answer"]
                    sources = data["sources"]
                    
                    st.write(answer)
                    
                    # Show sources
                    with st.expander("View Sources"):
                        for i, source in enumerate(sources, 1):
                            st.markdown(f"**Source {i}:** {source['filename']} (Page {source['page']})")
                            st.caption(source['text'])
                            st.divider()
                    
                    # Save to session
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Clear chat
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()