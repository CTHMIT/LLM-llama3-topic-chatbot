# LLM-Llama3-Topic-Chatbot

Build a topic-specific chatbot using LLM and run it on a website.
With memory, make the LLM check before chat history,
and use RAG to check the topic information.

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
## File Structure
- app.py: The main Flask application containing all routes and logic.
- templates/: Contains HTML templates for the web interface
- db/: The directory where Chroma stores the vectorized Wikipedia content.

## Customization
- Change the LLM:
  The chatbot uses the LLaMA 3 model by default. You can modify the model in app.py by changing the OllamaLLM(model="llama3") to another model.
- Adjust the Text Splitter:
  You can customize how the Wikipedia content is split into chunks for indexing by modifying the RecursiveCharacterTextSplitter parameters.
- Configure the Vector Store:
  The Chroma vector store can be configured to change the embedding model or persistence directory.
