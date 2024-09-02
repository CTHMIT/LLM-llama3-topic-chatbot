# LLM-Llama3-Topic-Chatbot

Build a topic-specific chatbot using LLM and run it on a website.

## Prerequisites

- **Environment**: Anaconda
- **Python Version**: >= 3.10
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
   After installing Ollama, select the model you want to use. For example, to use Llama 3, run:
   ```bash
   ollama pull llama3
   ```
4. Setting Up the Environment
   To install the necessary software packages, use the provided environment.yml file:
   ```bash
   conda env create -f environment.yml
   ```
