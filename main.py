import openai
import pyttsx3
import speech_recognition as sr
import random


# Set your OpenAI API key and model ID
openai.api_key = "<Your OpenAI API Key>"
model_id = 'gpt-3.5-turbo'

# Initialize the text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 280)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)


# Function to transcribe audio to text using Google's Speech Recognition
def transcribe_audio_to_text(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio)
        except:
            print("")

def load_character_profile(character_name):
    profile_file = f"characters/{character_name}/profile.txt"
    try:
        with open(profile_file, "r") as file:
            character_profile = file.read()
        return character_profile
    except FileNotFoundError:
        print(f"The profile file for {character_name} was not found.")
        return ""



# Function to interact with ChatGPT and store the conversation
def ChatGPT_conversation(conversation):
    response = openai.ChatCompletion.create(
        model=model_id,
        messages=conversation
    )

    api_usage = response['usage']
    print('Total tokens consumed: {0}'.format(api_usage['total_tokens']))
    conversation.append({'role': response.choices[0].message.role, 'content': response.choices[0].message.content})
    return conversation

# Function to convert text to speech
def speak_text(text):
    engine.say(text)
    engine.runAndWait()

# Function to read roleplay text from "roleplay.txt" file
def read_roleplay_text():
    try:
        with open("roleplay.txt", "r") as file:
            roleplay_text = file.read()
        return roleplay_text
    except FileNotFoundError:
        print("The 'roleplay.txt' file was not found.")
        return ""

# Function to load character profiles from profile.txt files
def load_character_profile(character_name):
    profile_file = f"characters/{character_name}/profile.txt"
    try:
        with open(profile_file, "r") as file:
            profile_lines = file.readlines()
        character_description = ""
        exit_phrases = []

        # Parse the profile file
        is_exit_phrase_section = False
        for line in profile_lines:
            if line.startswith("[Exit Phrases]"):
                is_exit_phrase_section = True
                continue
            if not is_exit_phrase_section:
                character_description += line
            elif line.strip():  # Avoid empty lines
                exit_phrases.append(line.strip())

        return character_description, exit_phrases
    except FileNotFoundError:
        print(f"The profile file for {character_name} was not found.")
        return "", []

# Function to choose a character and set the voice
def choose_character():
    character_profiles = {
        "1": {"name": "Best Friend", "voice_index": 0},
        "2": {"name": "Father", "voice_index": 0},
        "3": {"name": "Girlfriend", "voice_index": 1},
        "4": {"name": "Mother", "voice_index": 1},
        "5": {"name": "Sister", "voice_index": 1},
        "6": {"name": "Roleplay", "voice_index": 1}
    }

    while True:
        print("Choose a character:")
        for key, character in character_profiles.items():
            print(f"{key}. {character['name']}")
        
        choice = input("Enter the number of the character you want to use (1-6): ")

        if choice in character_profiles:
            character = character_profiles[choice]
            if character['name'] == "Roleplay":
                roleplay_text = read_roleplay_text()
                if roleplay_text:
                    return character['name'], roleplay_text, voices[character['voice_index']]
                else:
                    print("Roleplay text not found. Please create 'roleplay.txt' with the desired roleplay content.")
                    exit()
            else:
                character_profile = load_character_profile(character['name'])
                if character_profile:
                    return character['name'], character_profile, voices[character['voice_index']]
                else:
                    print(f"Character profile not found for {character['name']}.")
                    exit()
        else:
            print("Invalid choice. Please enter a valid character number.")

# Initialize the character, profile, voice, and exit phrases
character_name, character_description, character_voice = choose_character()
character_profile, exit_phrases = load_character_profile(character_name)

# Set the voice based on the chosen character
engine.setProperty('voice', character_voice.id)

# Starting conversation with ChatGPT
conversation = []
conversation.append({'role': 'user', 'content': character_profile})

# Function to randomly select an exit phrase from the character's list
def choose_exit_phrase():
    return random.choice(exit_phrases)

# Function to end the conversation
def end_conversation(exit_phrase):
    print(exit_phrase)  # You can replace this with your desired response
    exit()

# Function to append text to a log file
def append_to_log(text):
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        f.write(text + "\n")

# Initialize the speech recognizer
recognizer = sr.Recognizer()

# Function to print conversation to console
def print_conversation(conversation):
    for message in conversation:
        role = message['role'].strip()
        content = message['content']

        try:
            # Attempt to print with encoding 'utf-8'
            print('{0}: {1}\n'.format(role, content))
        except UnicodeEncodeError:
            # Handle encoding error by ignoring or replacing the character
            content = content.encode('utf-8', errors='ignore').decode('utf-8')
            print('{0}: {1}\n'.format(role, content))

# Main loop to listen for user input and interact with ChatGPT
while True:
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        audio = recognizer.listen(source, phrase_time_limit=10)
        
        try:
            transcription = recognizer.recognize_google(audio).lower()  # Convert to lowercase

            # Transcribe audio to text
            text = transcription

            if text:
                print(f"You Said: {text}")
                append_to_log(f"You: {text}\n")

                # Generate response using ChatGPT
                print(f"Summer Said : {conversation}")

                # Append the user's message to the conversation history
                conversation.append({'role': 'user', 'content': text})

                # Ensure the conversation history doesn't exceed the model's token limit
                while len(conversation) > 20:
                    conversation.pop(0)  # Remove the oldest message

                # Generate a response using the entire conversation history
                response = openai.ChatCompletion.create(
                    model=model_id,
                    messages=[
                        {'role': 'system', 'content': 'You are a helpful assistant.'},
                        {'role': 'user', 'content': 'Hello, my name is Sam.'},  # Specify the user's name
                    ] + conversation  # Include the entire conversation history
                )

                # Append the AI's response to the conversation history
                ai_response = response.choices[0].message.content.strip()
                conversation.append({'role': 'assistant', 'content': ai_response})
                append_to_log(f"Summer: {ai_response}\n")

                # Print the AI's response using utf-8 encoding
                ai_response_utf8 = ai_response.encode('utf-8', errors='ignore').decode('utf-8')
                print('{0}: {1}\n'.format(conversation[-1]['role'].strip(), ai_response_utf8))

                # Read response using text-to-speech
                speak_text(ai_response_utf8)

        except sr.UnknownValueError:
            print("Sorry, could not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
