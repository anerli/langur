

from langur.connector import Connector, action


class Terminal(Connector):
    @action
    def ask_user(question: str) -> str:
        '''Ask the user a question in the terminal.'''
        answer = input(f"Langur asked: {question}\n")
        return f"Answer: {answer}"

    @action
    def output(content: str) -> str:
        '''Output some content in the terminal.'''
        print(f"[OUTPUT] {content}")
        return f"I sent output to terminal: {content}"