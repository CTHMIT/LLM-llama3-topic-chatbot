# LLM-Llama3-Topic-Chatbot

Build a topic-specific chatbot using LLM and run it on a website.
With memory, make the LLM check before chat history,
and use RAG to check the topic information.

## Usage
- Select a Topic: On the homepage, enter a topic you're interested in. The application will search Wikipedia and return the most relevant result.
![image](https://github.com/user-attachments/assets/e18518be-9584-46c0-a355-57fe8b5c2cca)
- Chroma Vector Store: The content from Wikipedia is indexed using Chroma and stored as vectors for efficient retrieval.
- LLM-Powered Responses: The chatbot leverages the Ollama LLM (specifically the LLaMA 3 model) to generate responses based on the retrieved Wikipedia content.
- Chat with the Bot: After selecting a topic, you can start asking questions. The bot will use Wikipedia content and the LLaMA 3 model to generate responses.
![image](https://github.com/user-attachments/assets/f1cf1a69-54f8-409f-b100-14272b80adcb)
- Review Chat History: The chat history is displayed during your conversation and stored locally for later reference.
- End Session: You can clear the session and select a new topic at any time.
## If there is no match to the topic or search information, there will be suggested options for the user to choose from.
![image](https://github.com/user-attachments/assets/b0bb3fff-1f0f-445a-bf5c-30737dadd08f)

## Prerequisites

- **Environment**: Anaconda
- **Python** >= 3.10
- **Search API**: Wikipedia
- **Libraries**: LangChain
- **LLM**: Ollama

## Installation

### Download Ollama

To get started, you'll need to download Ollama. You have two options:

1. **Visit the [Ollama website](https://ollama.com/)** and download the installer.

2. **Linux/Ubuntu Installation**:
   Open your terminal and run the following command:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
3. Choose and Download a Model
   After you install Ollama, please select the model you want to use.
   For example, to use Llama 3, run:
   ```bash
   ollama pull llama3
   ```
5. Setting Up the Environment
   To install the necessary software packages, use the provided environment.yml file:
   ```bash
   conda env create -f environment.yml
   ```
6. Run the python file to Serving Flask app
   ```bash
   python app.py
   ```
   
## File Structure
- app.py: The main Flask application containing all routes and logic.
- templates/: Contains HTML templates for the web interface
- db/: The directory where Chroma stores the vectorized Wikipedia content.

## Customization
- Change the LLM:
  The chatbot uses the LLaMA 3 model by default.
  You can modify the model in app.py by changing the OllamaLLM(model="llama3") to another model.
- Adjust the Text Splitter:
  You can customize how the Wikipedia content is split into chunks for indexing by modifying the RecursiveCharacterTextSplitter parameters.
- Configure the Vector Store:
  The Chroma vector store can be configured to change the embedding model or persistence directory.

## Troubleshooting
Wikipedia Page Errors: If the application encounters a disambiguation page or the page doesn’t exist, the user is prompted to choose another topic or re-enter the query.
Session Errors: Ensure that the secret_key is set in the Flask app to avoid session-related errors.

## License
This project is licensed under the MIT License. See the [LICENSE](https://github.com/CTHMIT/LLM-llama3-topic-chatbot/blob/main/LICENSE) file for more details.

Acknowledgments
- Flask
- LangChain
- Chroma
- Wikipedia
