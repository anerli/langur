

from langur.connector import Connector, action
import requests

class Web(Connector):
    def get(self, url: str) -> str:
        '''Make a GET request for a particular URL and observe the response'''
        answer = input(f"Langur asked: {question}\n")
        return f"Answer: {answer}"

