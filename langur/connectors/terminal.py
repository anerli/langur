

from langur.connector import Connector, action


class Terminal(Connector):
    @action(tags=["input"])
    def ask_user(self, question: str) -> str:
        '''Ask the user a question in the terminal.'''
        answer = input(f"Langur asked: {question}\n")
        return f"Answer: {answer}"

    @action(tags=["output"])
    def output(self, content: str) -> str:
        '''Output some content in the terminal.'''
        print(f"[OUTPUT] {content}")
        return f"I sent output to terminal: {content}"