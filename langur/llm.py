# Basic prompting wrapper for now
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from textwrap import dedent

# from openai import OpenAI
# from anthropic import Anthropic


# def anthropic_structured_resp(self, messages, schema):

FAST_LLM = ChatOpenAI(model="gpt-4o-mini")
SMART_LLM = ChatAnthropic(model="claude-3-5-sonnet-20240620")



# PROMPT_GROW_NODE = '''

# '''
# def grow_node_prompt():
