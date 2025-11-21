# Cumulus - PC Controller Chatbot

This project implements a chatbot that utilizes the Gemini API to interact with and control various functionalities of a user's PC. It allows the AI to perform tasks such as launching applications, searching the web, and managing files and folders.

## Features

The chatbot provides the following capabilities:

*   **Launch Applications**: Start applications or games on your PC (e.g., 'chrome', 'calculator', 'steam').
*   **Search YouTube**: Perform searches directly on YouTube.
*   **Search Google**: Conduct Google searches using a web browser.
*   **Read Files**: Read the content of files from your PC.
*   **Write Files**: Create new files or modify existing ones.
*   **Remove Paths**: Safely delete files or directories.
*   **Create Folders**: Create new folders for project management.
*   **Check Paths**: List the contents (files and folders) of a specified directory.
*   **Move Paths**: Move files or folders from one location to another.
*   **Rename Files/Folders**: Change the name of files or folders.

## Usage

To interact with the chatbot, simply run `main.py` and type your commands. For example:

*   "Open Calculator"
*   "Launch Steam"
*   "Search YouTube for new music"
*   "What is the latest AI news?"
*   "Read the file my_document.txt"
*   "Create a folder named 'my_new_project'"

Type 'quit' or 'exit' to end the chat session.

## Configuration

This project requires a `GEMINI_API_KEY` to be set as an environment variable. Additionally, it uses an `APP_LIBRARY` defined in `config.py` to map application names to their executable paths. Please ensure these are configured correctly for optimal functionality.
