import openai
import pyttsx3
import speech_recognition as sr

# Set your OpenAI API key and model ID
openai.api_key = "<YOUR OPENAI KEY>"
model_id = 'gpt-3.5-turbo'

# Initialize the text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 280)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

interaction_counter = 0

# Function to transcribe audio to text using Google's Speech Recognition
def transcribe_audio_to_text(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio)
        except:
            print("")

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

# Starting conversation with ChatGPT
conversation = []
roleplay_text = read_roleplay_text()
if roleplay_text:
    conversation.append({'role': 'user', 'content': roleplay_text})
else:
    print("Roleplay text not found. Please create 'roleplay.txt' with the desired roleplay content.")
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
