from flask import Flask, render_template, request, redirect, url_for, session
from langchain.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document  
import wikipedia
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
CHAT_HISTORY_FILE = None
retriever_store = {}
BASE_DIR = os.getcwd()

def save_chat_history(chat_history, file_path):
    with open(file_path, "a") as file:
        file.write(chat_history + "\n")

def load_chat_history(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return file.read()
    return ""

def create_chroma_index(document_text, topic):
    persist_directory = os.path.join(BASE_DIR, 'db')
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model_kwargs = {'device': 'cpu'}
    embedding = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)

    document = Document(page_content=document_text, metadata={"source": "Wikipedia"})

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=5)
    all_splits = text_splitter.split_documents([document])

    vectorstore = Chroma.from_documents(documents=all_splits, embedding=embedding, persist_directory=persist_directory)
    
    retriever_store[topic] = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})


def find_best_matching_topic(user_input):
    wiki_wiki = wikipedia.Wikipedia(
        user_agent='chatbot',
        language='en',
        extract_format=wikipedia.ExtractFormat.WIKI

    )

    search_results = wiki_wiki.search(user_input, results=5)
    if search_results:
        best_match = search_results[0]
        page = wiki_wiki.page(best_match)
        if page.exists():
            return best_match, page.text
    return None, None

@app.route("/", methods=["GET", "POST"])
def select_topic():
    global CHAT_HISTORY_FILE  
    if request.method == "POST":
        user_input = request.form["topic"]
        session["user_input"] = user_input

        CHAT_HISTORY_FILE = os.path.join(os.getcwd(), f"{user_input}_chat_history.txt")

        search_results = wikipedia.search(user_input, results=5)  

        if search_results:
            best_match = search_results[0]
            try:
                page = wikipedia.page(best_match)
                session["topic"] = best_match
                session["summary"] = page.summary
                create_chroma_index(page.content, best_match)
                return redirect(url_for("chat"))
            except wikipedia.exceptions.DisambiguationError as e:
                suggestions = e.options
                return render_template("select_topic.html", suggestions=suggestions)
            except wikipedia.exceptions.PageError:
                session["summary"] = "Please confirm whether there is any error in your input and please re-enter it."
                session["topic"] = "No valid topic found"
                return render_template("select_topic.html", error=session["summary"])
        else:
            session["summary"] = "No matching results found, please re-enter."
            session["topic"] = "No valid topic found"
            return render_template("select_topic.html", error=session["summary"])

    return render_template("select_topic.html")

@app.route("/chat", methods=["GET", "POST"])
def chat():
    global CHAT_HISTORY_FILE  
    response = None
    topic = session.get("topic", "No topic selected")
    summary = session.get("summary", "No information available.")
    persona_description = f"A Q&A Anwerer with a deep understanding of {topic}."

    if CHAT_HISTORY_FILE is None:
        CHAT_HISTORY_FILE = os.path.join(BASE_DIR, f"{topic}_chat_history.txt")

    chat_history = load_chat_history(CHAT_HISTORY_FILE)  

    retriever = retriever_store.get(topic)

    chat_information = "No conversation yet."

    if request.method == "POST":
        if "change_topic" in request.form:
            return redirect(url_for("select_topic"))

        question = request.form["question"]

        if retriever:
            retriever_results = retriever.invoke(question)
            retriever_texts = " ".join([doc.page_content for doc in retriever_results])
        else:
            retriever_texts = "No additional information retrieved."

        template = """        
        Chat Topic : {topic} with Chat History: {chat_history}.
        Your Persona: {persona_description} and use the following information: {retriever_texts} to answer the final question.
        Answers should be accurate and concise.
        Question: {question}.
        Answer:
        """

        prompt = ChatPromptTemplate.from_template(template)
        model = OllamaLLM(model="llama3")
        chain = prompt | model

        response = chain.invoke({"topic": topic, 
                                 "chat_history": chat_history, 
                                 "retriever_texts": retriever_texts,
                                 "persona_description": persona_description, 
                                 "question": question})

        chat_entry = f"Question: {question}\nAnswer: {response}" 
        chat_information = f"You: {question}\n\nChatbot: {response}"     
        chat_history += "\n" + chat_entry
        save_chat_history(chat_entry, CHAT_HISTORY_FILE)  

    return render_template("chat.html", response=chat_information, topic=topic, chat_history=chat_history)

@app.route("/end_session")
def end_session():
    session.clear()
    return redirect(url_for("select_topic"))

if __name__ == "__main__":
    app.run(debug=True)
