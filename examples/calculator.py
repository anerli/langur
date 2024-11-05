from langur import Langur, Connector, action
from langur.connectors import Terminal

'''
Simple example demonstrating how to build a custom connector.
'''

class Calculator(Connector):
    @action
    def add(self, x: int, y: int):
        '''Add two numbers'''
        return x + y

    @action
    def multiply(self, x: int, y: int):
        '''Multiply two numbers'''
        return x * y

agent = Langur("What is (1494242 + 12482489284) * 24?")
agent.use(
    Calculator(),
    Terminal().disable("input")
)
agent.run()
