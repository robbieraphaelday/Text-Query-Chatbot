import os

# Set the OPENAI_API_KEY environment variable
os.environ['OPENAI_API_KEY'] = ''

import openai
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
import glob
import PyPDF2
import subprocess
import tkinter as tk


def add_to_history(messages, role, content):
    messages.append({"role": role, "content": content})
    return messages


def get_user_input():
    root = tk.Tk()
    root.title("Custom Value for Prompt Context")
    input_value = ['']  # Mutable container

    def submit():
        input_value[0] = text_widget.get("1.0", "end-1c")  # modify the content of the list
        root.destroy()

    text_widget = tk.Text(root, height=10, width=50)
    text_widget.pack()

    submit_button = tk.Button(root, text="Submit", command=submit)
    submit_button.pack()

    root.mainloop()

    return input_value[0]  # return the user input after the mainloop is over



def search_text_in_files(directory, text):
    file_paths = glob.glob(directory + '/*.txt')
    
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            content = file.read()
            if text in content:
                # Calculate the proportion through the text
                proportion = content.index(text) / len(content) * 100
                print(f"\nMatch found! Your excerpt is {proportion:.2f}% through the text.")
                
                # Open the corresponding PDF file
                pdf_file_name = os.path.basename(file_path).replace('.txt', '.pdf')
                pdf_file_path = os.path.join('pdfs', pdf_file_name)
                subprocess.run(['xdg-open', pdf_file_path])
                return
    
    print("\nNo exact match found.\n")


def get_text_content(path):
    with open(path, 'r') as f:
        content = f.read()
    return content

def taters(prompt, messages=None, docsearch=None):
    openai.api_key = os.getenv('OPENAI_API_KEY')

    if messages is None:
        messages = [{"role": "system", "content": "You are a helpful AI assistant."}]

    temp_messages = messages.copy()
    temp_messages.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", max_tokens=2000, temperature=0, messages=temp_messages)
    chat_response = response.choices[0]['message']['content'].strip()

    print("\n----------\nAI Response:", chat_response, "\n----------\n")

    # Ask user if they want to save the prompt and response
    save_chat = input("\nSave this prompt and chat to history? [y or n] ")
    if save_chat.lower() in ['y', 'yes']:
        messages.append({"role": "user", "content": prompt})
        messages.append({"role": "assistant", "content": chat_response})

    # Ask user if they want to make a new query
    new_query = input("\nDo you want to make a new query? [y or n] ")
    if new_query.lower() in ['y', 'yes']:
        while True:
            query = input("\nEnter your query or 'quit' to move on to prompting the AI Assistant: ")
            if query.lower() == 'quit':
                break

            docs = docsearch.similarity_search(query)
            print(f"\nFound {len(docs)} similar documents\n")

            for doc in docs:
                print("\nDocument:", doc.page_content, "\n")
                user_input = input("\nAdd this document to prompt context? [y, n, or find] ")
                if user_input.lower() in ['y', 'yes']:
                        messages = add_to_history(messages, "user", "Here is some context I've found, please consider when I prompt you in the future: " + doc.page_content)
                elif user_input.lower() == 'find':
                    search_text_in_files('text_docs', doc.page_content)

                    final_user_input = input("\nAdd this document to prompt context? [y or n or custom] ")
                    if final_user_input.lower() in ['y', 'yes']:
                        messages = add_to_history(messages, "user", "Here is some context I've found, please consider when I prompt you in the future: " + doc.page_content)
                    elif final_user_input.lower() in ['custom']:
                        a = get_user_input()
                        print("\nCustom value added to prompt context: " + a + "\n\n")
                        messages = add_to_history(messages, "user", "Here is some context I've found, please consider when I prompt you in the future: " + doc.page_content)

    return messages

def main():
    conversation_history = [{"role": "system", "content": ""}]
    
    try:

        # Get all text files in the 'text_docs' directory
        text_files = [f for f in os.listdir('text_docs') if f.endswith('.txt')]
        print(f"\nFound {len(text_files)} text files\n")

        # Concatenate the contents of all text files
        corpus = ""
        for text_file in text_files:
            corpus += get_text_content(os.path.join('text_docs', text_file))

        print("\nFinished processing all text files\n")

        # Splitting up the text into smaller chunks for indexing
        text_splitter = CharacterTextSplitter(        
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,  # striding over the text
            length_function=len,
        )

        texts = text_splitter.split_text(corpus)
        print(f"\n\nText split into {len(texts)} chunks\n")

        # Download embeddings from OpenAI
        print("\nDownloading embeddings from OpenAI\n")
        embeddings = OpenAIEmbeddings()

        docsearch = FAISS.from_texts(texts, embeddings)
        print("\nCreated FAISS index\n")
       
        while True:
            query = input("\nEnter your query or 'quit' to move on to prompting the AI Assistant: ")
            if query.lower() == 'quit':
                break

            docs = docsearch.similarity_search(query)
            print(f"\nFound {len(docs)} similar documents\n")

            for doc in docs:
                print("\nDocument:", doc.page_content, "\n")
                user_input = input("\nAdd this document to prompt context? [y, n, or find] ")
                if user_input.lower() in ['y', 'yes']:
                    conversation_history.append({"role": "user", "content": "Here is some context I've found, please consider when I prompt you in the future: " + doc.page_content + "\n"})
                elif user_input.lower() == 'find':
                    search_text_in_files('text_docs', doc.page_content)

                    final_user_input = input("\nAdd this document to prompt context? [y or n or custom] ")
                    if final_user_input.lower() in ['y', 'yes']:
                        conversation_history = add_to_history(conversation_history, "user", "Here is some context I've found, please consider when I prompt you in the future: " + doc.page_content)
                
                    elif final_user_input.lower() in ['custom']:
                        a = get_user_input()
                        print("\nCustom value added to prompt context: " + a + "\n\n")
                        conversation_history = add_to_history(conversation_history, "user", "Here is some context I've found, please consider when I prompt you in the future: " + a)



        while True:
            user_input = input("\nEnter your prompt or 'quit' to stop: ")
            if user_input.lower() == 'quit':
                print("\n\nExiting the chatbot.")
                break

            conversation_history = taters(user_input, messages=conversation_history, docsearch=docsearch)

    except KeyboardInterrupt:
        print("\n\nExiting the chatbot.")
        return

if __name__ == "__main__":
    main()

