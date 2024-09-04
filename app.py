from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
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
CHAT_HISTORY_PATH = os.path.join(BASE_DIR, 'chat_history')
if not os.path.exists(CHAT_HISTORY_PATH):
    os.makedirs(CHAT_HISTORY_PATH)

def save_chat_history(chat_history, file_path):
    with open(file_path, "w") as file:
        file.write(chat_history + "\n")

def load_chat_history(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return file.read()
    return ""

def create_chroma_index(document_text, topic):
    persist_directory = os.path.join(BASE_DIR, 'db')
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embedding = HuggingFaceEmbeddings(model_name=model_name, model_kwargs={'device': 'cpu'})

    document = Document(page_content=document_text, metadata={"source": "Wikipedia"})
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=5)
    all_splits = text_splitter.split_documents([document])

    vectorstore = Chroma.from_documents(documents=all_splits, embedding=embedding, persist_directory=persist_directory)
    retriever_store[topic] = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

def find_best_matching_topic(user_input):
    search_results = wikipedia.search(user_input, results=5)
    if search_results:
        best_match = search_results[0]
        page = wikipedia.page(best_match)
        if page:
            return best_match, page.summary, page.url
    return None, None, None

@app.route("/", methods=["GET", "POST"])
def select_topic():
    global CHAT_HISTORY_FILE
    
    saved_topics = [filename.replace("_chat_history.txt", "") 
                    for filename in os.listdir(CHAT_HISTORY_PATH) 
                    if filename.endswith("_chat_history.txt")]
    
    if request.method == "POST":
        user_input = request.form.get("topic").strip().lower()

        if "'s disease" in user_input:
            base_topic = user_input.replace("'s disease", "").lower()
        elif " disease" in user_input:
            base_topic = user_input.replace(" disease", "").lower()
        else:
            base_topic = user_input
        
        CHAT_HISTORY_FILE = os.path.join(CHAT_HISTORY_PATH, f"{base_topic}_chat_history.txt")

        best_match, summary, link = find_best_matching_topic(user_input)
        
        if best_match:
            session["topic"] = best_match  
            session["summary"] = summary
            session["link"] = link
            if base_topic  in saved_topics:         
                session["history"] = load_chat_history(CHAT_HISTORY_FILE)            
            return redirect(url_for("chat"))
            page = wikipedia.page(best_match)
            create_chroma_index(page.content, best_match)
            return redirect(url_for("chat"))
        else:
            return render_template("select_topic.html", error="No valid topic found", saved_topics=saved_topics)

    return render_template("select_topic.html", saved_topics=saved_topics, show_diseases=False)

@app.route("/fetch_diseases", methods=["GET"])
def fetch_diseases():
    search_results = wikipedia.search("disease", results=25)
    diseases = []
    for result in search_results:
        if "disease" in result.lower() or any(term in result.lower() for term in ["syndrome", "disorder", "condition"]):
            diseases.append(result)
    
    return jsonify(diseases)

@app.route("/chat", methods=["GET", "POST"])
def chat():
    global CHAT_HISTORY_FILE
    
    topic = session.get("topic", "No topic selected")
    summary = session.get("summary", "No information available.")
    link = session.get("link", "No information link")
    chat_history = session.get("history", "No chat history")

    persona_description = f"A Q&A Anwerer with a deep understanding of {topic}."
    
    retriever = retriever_store.get(topic)
    chat_information = f"Asked any questions you want to know about {topic}."

    if request.method == "POST":
        if "change_topic" in request.form:
            return redirect(url_for("select_topic"))

        question = request.form["question"]
        retriever_texts = " ".join([doc.page_content for doc in retriever.invoke(question)]) if retriever else "No additional information retrieved."

        template = f"""
        Chat Topic is {topic}.
        {topic} the summary : {summary}.
        Chat History: {chat_history}.
        Your Persona: {persona_description}.
        Use the following information: {retriever_texts} to answer the final question.
        Answers should be accurate and concise.
        Question: {question}.
        Answer:
        """

        prompt = ChatPromptTemplate.from_template(template)
        model = OllamaLLM(model="llama3")
        chain = prompt | model

        response = chain.invoke({
            "topic": topic,
            "summary": summary,
            "chat_history": chat_history,            
            "persona_description": persona_description,
            "retriever_texts": retriever_texts,
            "question": question
        })

        chat_entry = f"User Question: {question}\nThe Answer: {response}"
        chat_information = f"You: {question}\n\nChatbot: {response}"
        chat_history += "\n" + chat_entry
        save_chat_history(chat_history, CHAT_HISTORY_FILE)

    return render_template("chat.html", response=chat_information, topic=topic, chat_history=chat_history, link=link)

@app.route("/view_record")
def view_record():
    global CHAT_HISTORY_FILE
    if CHAT_HISTORY_FILE and os.path.exists(CHAT_HISTORY_FILE):
        return send_file(CHAT_HISTORY_FILE, as_attachment=True, download_name=os.path.basename(CHAT_HISTORY_FILE))
    return "No record file found", 404

@app.route("/end_session")
def end_session():
    session.clear()
    return redirect(url_for("select_topic"))

if __name__ == "__main__":
    app.run(debug=True)
