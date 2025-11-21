import os
import sys
import subprocess
import urllib.parse
import shutil
import stat
import errno

import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

from config import APP_LIBRARY # Import APP_LIBRARY from config.py


# --- CONFIGURATION ---
API_KEY = os.getenv("GEMINI_API_KEY")

# --- HELPER FUNCTIONS ---
def _run_command_os_agnostic(command_parts):
    """Helper to run commands based on OS."""
    try:
        if sys.platform == "win32":
            subprocess.Popen(command_parts)
        elif sys.platform == "darwin":  # macOS
            subprocess.Popen(["open"] + command_parts) # 'open' command expects list
        else:  # Linux
            subprocess.Popen(["xdg-open"] + command_parts) # 'xdg-open' expects list
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error running command: {e}") # Use print for now, could be logging later
        return False


# --- STEP 1: Define the Actual Python Function ---
def launch_application(app_name: str):
    """
    Launches an application or game on the user's PC.
    
    Args:
        app_name: The name of the application to launch (e.g., 'chrome', 'calculator', 'steam').
    """
    print(f"\n[System] Attempting to launch: {app_name}...")
    
    target = APP_LIBRARY.get(app_name.lower())

    if target:
        # Split target into parts for subprocess.Popen if it's a string with arguments
        if isinstance(target, str):
            command_parts = target.split()
        else:
            command_parts = [target] # Assume it's already a list or single command

        if _run_command_os_agnostic(command_parts):
            return f"Successfully launched {app_name}."
    
    # Try raw name as a system command or direct path if not in APP_LIBRARY or if it failed
    if _run_command_os_agnostic([app_name]): 
        return f"Successfully launched {app_name}."
    
    return f"Failed to launch {app_name}. Error: Application or command not found. Please check the name or path."


def searchOnYoutube(search: str):
    """
    Launches an youtube app and only search's things on youtube.
    
    Args:
        search: text that user wants to search (e.g., 'python new update', 'new jeans slowed remix', 'joenbuk national university vlogs').
    """
    # This part still hardcodes Brave. Consider making it configurable or using webbrowser module.
    proxy_exe = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\chrome_proxy.exe"
    APP_ID = "agimnkijcaahngcdmfeangaknmldooml"
    search = search.strip()
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(search)}"
    command = [
        proxy_exe,
        "--profile-directory=Default",
        f"--app-id={APP_ID}",
        f"--app-launch-url-for-shortcuts-menu-item={url}"
    ]
    try:
        subprocess.Popen(command)
        return f"Successfully searched YouTube for '{search}'."
    except FileNotFoundError:
        return f"Failed to launch Brave Browser to search YouTube. Please ensure Brave is installed or update the proxy_exe path."
    except Exception as e:
        return f"Failed to search YouTube for '{search}'. Error: {str(e)}"


def searchOnGoogle(search: str):
    """
    Launches a web browser and performs a Google search.

    Args:
        search: The text to search for on Google (e.g., 'latest AI news', 'recipe for pizza').
    """
    print(f"\n[System] Attempting to search Google for: {search}...")
    search = search.strip()
    url = f"https://www.google.com/search?q={urllib.parse.quote(search)}"
    
    if _run_command_os_agnostic([url]): # Try to open URL directly (default browser)
        return f"Successfully searched Google for '{search}'."
    else:
        # Fallback to a specific browser if the default method fails
        chrome_path = APP_LIBRARY.get("chrome", "chrome.exe") 
        if _run_command_os_agnostic([chrome_path, url]):
            return f"Successfully searched Google for '{search}' using Chrome as a fallback."
        else:
            return f"Failed to search Google for '{search}'. Error: Web browser or command not found. Please ensure a browser is installed and configured or update APP_LIBRARY 'chrome' path if needed."


def read_file(file_name: str):
    """
    Reads the content of a file from the user's PC so the AI can analyze code or text.
    """
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            content = f.read()
        return content

    except FileNotFoundError:
        return f"Error: The file '{file_name}' was not found."
    except Exception as e:
        return f"Error reading file: {str(e)}"
    
def write_file(file_name: str, context):
    """
    Ai should find if file already exists, if it does not exist it function can also create files, if it exists AI should read using read_file function first then write the changes
    writes the content to the user's PC so the AI can fix code or text.
    """
    try:
        # Ensure directory exists before writing
        dir_name = os.path.dirname(file_name)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(context)
        return f"Successfully wrote to {file_name}."
    except Exception as e:
        return f"Error writing file: {str(e)}"



def remove_path(path: str):
    """
    Safely deletes a file or directory, handling Windows permission issues
    """
    path = path.strip('"\'')  # remove quotes if copied from explorer
    
    if not os.path.exists(path):
        return "Path not found"

    try:
        # Case 1: It's a file (or symlink to file)
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
            return f"File deleted: {path}"

        # Case 2: It's a directory
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return f"Folder deleted: {path}"

    except PermissionError as e:
        # Most common on Windows: file/folder is read-only or in use
        # Fix read-only flags on everything inside
        def make_writable(action, name, exc):
            # Change permission to allow deletion
            os.chmod(name, stat.S_IWRITE)
            return action(name)  # retry the action

        shutil.rmtree(path, onerror=make_writable)
        return f"Deleted (after fixing permissions): {path}"

    except OSError as e:
        if e.errno == errno.EACCES:  # Still access denied
            return ("Access denied. Possible causes:\n"
                    "• File/folder is open in another program (close it!)\n"
                    "• Antivirus is locking it\n"
                    "• You need to run Python/script as Administrator\n"
                    "• It's a system/protected folder")
        else:
            return f"Error: {e}"

    return "Deleted successfully"


def movePath(path: str, destonation: str):
    try:
        shutil.move(path, destonation)
        return f"Successfully moved {path} to {destonation}."
    except FileNotFoundError:
        return f"Error: Source path '{path}' not found."
    except PermissionError:
        def make_writable(action, name, exc):
            os.chmod(name, stat.S_IWRITE)
            return action(name)
        try:
            shutil.rmtree(path, onerror=make_writable)
            shutil.move(path, destonation)
            return f"Moved {path} to {destonation} (after fixing permissions)."
        except Exception as e_retry:
            return f"Permission denied and failed to move {path} to {destonation} after retrying: {e_retry}"
    except Exception as e:
        return f"Error moving path: {str(e)}"


def renameFile(oldFileName, newFileName):
    """
    oldFileName can be Path(e.g. oldFileName=project\\main.py, newFileName=project\\bot.py) or file name if already in project folder e.g. just "main.py" to "bot.py"
    it can also be used to rename folders
    """
    try:
        os.rename(oldFileName, newFileName)
        return f"Successfully renamed {oldFileName} to {newFileName}."
    except FileNotFoundError:
        return f"Error: File or folder '{oldFileName}' not found."
    except Exception as e:
        return f"Error renaming file/folder: {str(e)}"


def create_folder(folderName: str):
    """
    creates molder on user's Pc to help with project managing
    """
    try:
        os.mkdir(folderName)
        return f"Successfully created folder '{folderName}'."
    except FileExistsError:
        return f"Error: Folder '{folderName}' already exists."
    except Exception as e:
        return f"Error creating folder: {str(e)}"

def check_path(directory: str = "."):
    """
    Lists items (files and folders) in the specified directory. Defaults to the current working directory.
    
    Args:
        directory: The path to the directory to list. Defaults to '.' (current directory).
    """
    try:
        if not os.path.isdir(directory):
            return f"Error: '{directory}' is not a valid directory."
            
        items = os.listdir(directory)
        if not items:
            return f"The directory '{directory}' is empty."
            
        output = f"Contents of '{directory}':\n"
        for item in items:
            full_path = os.path.join(directory, item)
            if os.path.isdir(full_path):
                output += f"[DIR] {item}\n"
            else:
                output += f"[FILE] {item}\n"
        return output
    except FileNotFoundError:
        return f"Error: Directory '{directory}' not found."
    except Exception as e:
        return f"Error checking path: {str(e)}"




# --- STEP 2: Configure Gemini with Tools ---
genai.configure(api_key=API_KEY)

# Create the tool dictionary for Gemini 
tools_list = [launch_application, searchOnYoutube, searchOnGoogle, read_file, write_file, remove_path, create_folder, check_path, movePath, renameFile]

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash', # Flash is fast and cheap for tools
    tools=tools_list,
)

# Start a chat session with automatic function calling enabled
chat = model.start_chat(enable_automatic_function_calling=True)

# --- STEP 3: Main Chat Loop ---
def main():
    print("--- PC Controller Chatbot (Type 'quit' to exit) ---")
    print("Try asking: 'Open Calculator' or 'Launch TF2'")

    while True:
        try:
            user_input = input("\nYou: ")
        except KeyboardInterrupt:
            break
        if user_input.lower() in ['quit', 'exit']:
            break

        try:
            # Send message to Gemini
            # It will automatically detect if it needs to run launch_application(),
            # execute it, and generate a natural language response based on the result.
            response = chat.send_message(user_input)
            print(f"Bot: {response.text}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()