# Text-Query-Chatbot

This project is a chatbot that utilizes the Langchain and GPT models to allow users to query multiple PDF documents and engage in conversation with the chatbot.

## Features

- Query multiple PDF documents
- Engage in conversation with the chatbot
- Retrieve information from the loaded PDF documents

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/chatbot-project.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Add your OpenAI key to the `txt_langchain.py` file and `openai_api.txt` file. These keys are required for the operation of the chatbot.

## Usage

1. Add the PDF documents you want to query to the `docs` directory.

2. Start the chatbot by running the following command:
   ```
   python chatbot.py
   ```

3. Follow the instructions provided by the chatbot to query the PDF documents or engage in a conversation.

## PDF and Text Docs

txt_langchain.py is intended to work with text documents only. Since most data you encounter will be pdfs, there is ocr.py which can convert these files for you to text documents. In order to use the find feature, you will need pdfs and text docs in their respective directories with the same file names (sans the extension pdf or txt).

## Contributing

Contributions are welcome! If you have any suggestions or find any issues, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
