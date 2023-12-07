import openai
import speech_recognition as sr
import threading
from rich.console import Console
import requests
from pydub import AudioSegment
from pydub.playback import play

# Set your OpenAI API key and model ID
openai.api_key = "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"

model_id= "gpt-4-1106-preview"

# model_id = "ft:gpt-3.5-turbo-0613:personal::7wxvMtKW"



# Default voice_ID for Girlfriend
voice_ID = "EXAVITQu4vr4xnSDxMaL"

# Function to play the Eleven Labs voice
def speek(text):
    global voice_ID  # Access the global voice_ID variable

    CHUNK_SIZE = 1024
    if voice_ID == "girlfriend":
        voice_URL = "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL/stream"
    elif voice_ID == "doctor":
        voice_URL = "https://api.elevenlabs.io/v1/text-to-speech/Uij9kJMnlsYIk0iiRIUx/stream"
    else:
        print("Invalid voice ID selected")
        return

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": "0c300f0ff3e0754065480afa3f822a09",
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5},
    }

    response = requests.post(voice_URL, json=data, headers=headers, stream=True)

    with open("output.mp3", "wb") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)



# Function to read the roleplay text based on the selected profile
def read_roleplay_text(selected_profile):
    try:
        profile_file = "Girlfriend profile.txt" if selected_profile == "girlfriend" else "Doctor profile.txt"
        with open(profile_file, "r") as file:
            roleplay_text = file.read()
        return roleplay_text
    except FileNotFoundError:
        print(f"The '{profile_file}' file was not found.")
        return ""

# Function to let the user choose profile
def choose_profile():
    global voice_ID  # Access the global voice_ID variable

    while True:
        print("Please choose who you want to talk to:")
        print("1. Girlfriend")
        print("2. Doctor")
        choice = input("Enter your choice (1/2): ")

        if choice == "1":
            voice_ID = "girlfriend"
            return "girlfriend"
        elif choice == "2":
            voice_ID = "doctor"
            return "doctor"
        else:
            print("Invalid choice. Please enter either 1 or 2.")


# Initialize the conversation profile based on user choice
selected_profile = choose_profile()
roleplay_text = read_roleplay_text(selected_profile)

# Function to append text to a log file
def append_to_log(text):
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n")


# Function to read the entire conversation history from the chat log
def read_conversation_history(file_path, selected_profile):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        conversation = []
        current_role = None
        current_message = []

        for line in lines:
            if line.startswith("User: "):
                current_role = "user"
                current_message.append(line[5:].strip())
            elif line.startswith("Ai: "):  # Include assistant's messages
                current_role = "assistant"
                current_message.append(line[11:].strip())
            else:
                # If the line doesn't start with "User:" or "Ai:", it's a continuation of the current message
                current_message.append(line.strip())

            if not line.strip():
                # Empty line separates messages in the log
                if current_role and current_message:
                    conversation.append(
                        {"role": current_role, "content": " ".join(current_message)}
                    )
                current_role = None
                current_message = []

        # Update the system message based on the selected profile
        system_message = {"role": "system", "content": roleplay_text}
        if selected_profile == "doctor":
            system_message = {"role": "system", "content": f"Doctor: {roleplay_text}"}

        conversation.append(system_message)
        return conversation

    except FileNotFoundError:
        print("The 'chat_log.txt' file was not found.")
        return []


# Initialize an empty conversation
conversation = []

# Initialize the rich console for the "Listening..." animation
console = Console()
listening_animation_visible = (
    True  # Variable to control the visibilityroleplay_text = read_roleplay_text() of the animation
)

# Function to read exit phrases from "exit_phrases.txt" file
def read_exit_phrases():
    try:
        with open("exit_phrases.txt", "r") as file:
            exit_phrases = [line.strip() for line in file.readlines()]
        return exit_phrases
    except FileNotFoundError:
        print("The 'exit_phrases.txt' file was not found.")
        return []


exit_phrases = read_exit_phrases()


# Function to display the "Listening..." animation
def listen_animation(status):
    while True:
        with console.status(status):
            while listening_animation_visible:
                pass  # Animation remains visible while the variable is True
            console.clear()  # Clear the console to make the animation invisible


# Function to display the status
def display_status(status):
    print(status, end="", flush=True)


# Initialize the recognizer
recognizer = sr.Recognizer()

# Variable to store the speech transcript
transcript = []

# Main loop for speech recognition and ChatGPT interaction
        # Create a thread to run the "Listening..." animation
animation_thread = threading.Thread(
            target=listen_animation, args=("Working on it...",)
        )
animation_thread.daemon = (
            True  # Set as a daemon thread to exit when the main program exits
        )
animation_thread.start()
while True:
    while True:

        try:
            with sr.Microphone() as source:
                print("Listening...")
                recognizer.adjust_for_ambient_noise(source)
                audio_data = recognizer.listen(source, timeout=5)  # Adjust the timeout as needed

            text = recognizer.recognize_google(audio_data)

            if text:
                print(f"\rYou Said: {text}  ", end="", flush=True)
                append_to_log(f"User: {text}\n")
                display_status("Answering...   ")

                # Define a system message to provide context to the user
                system_message = {"role": "system", "content": roleplay_text}

                # Read the entire conversation history from chat_log.txt
                previous_conversation = read_conversation_history("chat_log.txt", selected_profile)

                # Append the system message to the conversation
                previous_conversation.append(system_message)

                # Add the user's latest message to the conversation
                previous_conversation.append({"role": "user", "content": text})

                # Generate response using ChatGPT with the entire conversation history
                response = openai.ChatCompletion.create(
                    model=model_id, messages=previous_conversation
                )

                # Extract the assistant's response
                ai_response = response.choices[0].message.content.strip()
                
                previous_conversation.append(
                    {"role": "assistant", "content": ai_response}
                )
                append_to_log(f"Ai: {ai_response}\n")

                print(
                    f"\rAi: {ai_response}  ", end="", flush=True
                )  # Overwrite "Answering..."

                speek(ai_response)
                # Load the audio file
                audio_file = AudioSegment.from_file(
                    "output.mp3", format="mp3"
                )  # Replace with the path to your audio file

                # Play the audio
                play(audio_file)

        except sr.UnknownValueError:
            print("\rListening...   ", end="", flush=True)
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except sr.WaitTimeoutError:
            print("\rListening timeout. Please speak again.")
        except sr.UnknownValueError:
            print("\rCould not understand audio.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

        # Clear the status message
        print("\r", end="", flush=True)