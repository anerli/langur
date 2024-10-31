'''
UserChat connector using the high level interface
'''

from langur.connector import Connector


UserChat = Connector("UserChat")

@UserChat.action
def ask_user(question: str) -> str:
    '''Ask the user a question in the terminal.'''
    answer = input(f"Langur asked: {question}\n")
    return f"Question to User: {question}\nUser Answer: {answer}"

