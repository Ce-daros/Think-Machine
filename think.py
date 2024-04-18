from openai import OpenAI
import os, re

# Get the API key from environment variables
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")

# Initialize the OpenAI client with the provided API key and base URL
client = OpenAI(
    api_key="...",
    base_url="https://api.together.xyz/v1",
)

# Initialize the context and language variables
now_context = "(None)"
query = ""
lang = "English"


# A generator function to create a sequence of thinking dots
def thinking_dots_generator():
    while True:
        for i in range(1, 4):
            yield i


# Create an instance of the thinking dots generator
dot_generator = thinking_dots_generator()


# Function to print thinking dots while processing
def thinking(message):
    # Get the current number of dots from the generator
    dots = next(dot_generator)
    # Print the message with the corresponding number of dots
    print(f"\033[A\033[2K{message}{'.' * dots}")


# Function to call the language model with specified parameters
def call_LLM(messages, model="Qwen/Qwen1.5-7B-Chat"):
    global uo
    # Call the chat completion API with the provided messages and model
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=0.6,
        top_p=0.8,
        max_tokens=26000,
        presence_penalty=0.3,
        frequency_penalty=0.3,
    )
    # Return the content of the first choice's message
    return chat_completion.choices[0].message.content


# Function to speculate the user's purpose behind their message
def speculater(deeper=False, old_purpose=""):
    global now_context, query
    # Call the language model with the system role and user query
    returns = call_LLM(
        [
            {
                "role": "system",
                "content": f"""You are an AI assistant. This is the context between the user and you: \n{now_context}\n\nYour task is to speculate the user's purpose behind sending their newest message:\n{query}\n\nOutput in plain text. No any explations and other text. Just speculate their purpose like 'The user's purpose is ...' in detailed and highly perceptive thought (>100 words) and output it. Reply in {lang}""",
            },
            *(
                [
                    {"role": "user", "content": old_purpose},
                    {
                        "role": "system",
                        "content": "Please re-consider the user's message in deeper thinking. (len>100 words). Follow the same format, without any explations and other text. Start with 'Also, the user ...'",
                    },
                ]
                if deeper
                else []
            ),
        ]
    )
    return returns


# Function to split the user's purpose into questions
def splitter(purpose):
    global now_context, query
    # Call the language model with the system role, assistant's purpose, and system's instructions
    returns = call_LLM(
        [
            {
                "role": "system",
                "content": f"""You are an AI assistant. This is the context between the user and you: \n{now_context}\n\nYour task is to speculate the user's purpose behind sending their newest message sent to you:\n{query}\n\nOutput in plain text. No any explations and other text. Just speculate their purpose like 'The user's purpose is ...' in detailed and deep thought (>100 words) and output it. Reply in {lang}""",
            },
            {
                "role": "assistant",
                "content": purpose,
            },
            {
                "role": "system",
                "content": """Okay, now please go through the 'divide and conquer' strategy. The user's purpose you speculated is great, but you must have some questions about the user's purpose itself. Please organize your questions into three perceptive questions towards the user for self-reflection, which are important for better response but you don't know them now. Use of "the user" as a reference to the user in questions. Format:
                        1. ...
                        2. ...
                        3. ... For example: 'Why the user ...?' 'What will the user...?'. No any other explations and other stuff just 3 questions.""",
            },
        ]
    )
    # Split the returned string into a list of questions
    return returns.split("\n")


# Function to reflect on a given question
def reflecter(question):
    global now_context, query
    # Call the language model with the system role, current context, and user query
    returns = call_LLM(
        [
            {
                "role": "system",
                # Provide the context and instructions for reflection
                "content": f"""You are an AI assistant. This is the context between the user and you: \n{now_context}\n\nYour task is to speculate the user's purpose behind sending their newest message sent to you:\n{query}\n\nOutput in plain text. No any explations and other text. Just speculate their purpose like 'The user's purpose is ...' in detailed and deep thought (>100 words) and output it. Reply in {lang}""",
            },
            {
                "role": "assistant",
                # Provide the query for reflection
                "content": query,
            },
            {
                "role": "system",
                # Provide the question for the assistant to reflect upon
                "content": f"""Okay, now please ask this question to yourself and write down your thoughts like 'I think the user might ...'. '{question}'""",
            },
        ]
    )
    # Return the assistant's reflection
    return returns


def summarizer(thought):
    global now_context, query
    # Call the language model with the system role, current context, and thoughts
    returns = call_LLM(
        [
            {
                "role": "system",
                # Provide the context and instructions for summarizing thoughts
                "content": f"""You are an AI assistant. This is the context between the user and you: \n{now_context}\n\nYour task is to write down your thoughts toward the lastest message the user send to you:\n{query}\n\nOutput in plain text. No any explations and other text. Just think like 'I think the user might ...' in detailed and deep thought and output it. Reply in {lang}""",
            },
            {
                "role": "assistant",
                # Provide the assistant's thoughts
                "content": thought,
            },
            {
                "role": "system",
                # Provide the instructions for creating a detailed response based on the thoughts
                "content": f"""Okay, now please give the user a very long, natural, human-like and highly detailed perceptive answer to user's message, base on these thoughts. Use "You" to refer user. Mention the you guess the purpose of the user as prefix, like 'Hey, I have the ability to speculate on your purpose ...' or 'Hmm, I think you want to ..., huh?'. After that, you have to directly answer user's question '{query}' in detail and long text. Like 'So now I answer you, ... Length at least 3000 words. Give all answer in {lang}. 使用自然，随意的口语化语气。""",
            },
        ],
        model="Qwen/Qwen1.5-7B-Chat",  # Specify the model to be used for this call
    )
    # Return the detailed response generated by the assistant
    return returns


# Change the language for the response
lang = "中文！"


def think():
    global query

    # Get input from the user
    query = input("User: ")
    # Speculate on the user's purpose
    old = speculater()
    print()
    # Display thinking animation
    thinking("Analysising")
    # Split the speculated purpose into questions
    splitted = splitter(old)
    # Display thinking animation
    thinking("Analysising")
    print()
    # Initialize list to store reflections
    reflected = []
    # Initialize text to store reflections
    ref_text = ""
    # Iterate over the questions to reflect on each
    for i in splitted:
        reflect = reflecter(i)
        reflected.append(reflect)
        # Display thinking animation
        thinking("Self-reflect")
        # Append reflections to the text
        ref_text += f"{reflect}\n\n"
    # Display thinking animation
    thinking("Summarizing")
    # Print the summarized response from the assistant
    print(f"Think Machine: {summarizer(ref_text)}")


# Call the think function to start the process
think()
