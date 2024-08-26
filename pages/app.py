import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import pandas as pd  # Import pandas for spreadsheet processing
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from langchain.llms import HuggingFaceHub

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_spreadsheet_text(spreadsheet_files):
    text = ""
    for file in spreadsheet_files:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        text += df.to_string(index=False)  # Convert dataframe to string without index
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.write(response)
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
    
st.set_page_config(page_title="EduBOT - Chatbot for Educational Institutions", page_icon="🧠")

def main():
    st.header("EduBOT - Chatbot for Educational Institutions 🧠")
    load_dotenv()
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "query_history" not in st.session_state:
        st.session_state.query_history = []

    user_question = st.text_input("Ask your questions:")
    if user_question:
        st.session_state.query_history.append(user_question)
        handle_userinput(user_question)
        
    with st.sidebar:
        st.subheader("Your documents")
        uploaded_files = st.file_uploader(
            "Upload your PDFs, Excel, or CSV files here and click on 'Process'", 
            accept_multiple_files=True,
            type=["pdf", "csv", "xlsx", "xls"]  # Allow these file types
        )
        
        if st.button("Process"):
            with st.spinner("Processing"):
                raw_text = ""
                
                # Separate files into PDF and spreadsheets
                pdf_files = [f for f in uploaded_files if f.name.endswith('.pdf')]
                spreadsheet_files = [f for f in uploaded_files if f.name.endswith(('.csv', '.xlsx', '.xls'))]
                
                # Extract text from PDFs
                if pdf_files:
                    raw_text += get_pdf_text(pdf_files)
                
                # Extract text from spreadsheets
                if spreadsheet_files:
                    raw_text += get_spreadsheet_text(spreadsheet_files)
                
                # Get the text chunks
                text_chunks = get_text_chunks(raw_text)
                st.write(text_chunks)
                
                # Create vector store
                vectorstore = get_vectorstore(text_chunks)

                # Create conversation chain
                st.session_state.conversation = get_conversation_chain(vectorstore)
                
    st.subheader("Query History 🔍")
    for idx, query in enumerate(st.session_state.query_history):
        st.write(f"{idx + 1}. {query}")

if __name__ == "__main__":
    main()
