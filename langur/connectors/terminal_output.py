from langur.connector import Connector


TerminalOutput = Connector("TerminalOutput")

@TerminalOutput.action
def output(content: str) -> str:
    '''Output some content in the terminal.'''
    print(f"[OUTPUT] {content}")
    return f"I sent output to terminal: {content}"

