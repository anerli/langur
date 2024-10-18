# Basic prompting wrapper for now
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from textwrap import dedent

# from openai import OpenAI
# from anthropic import Anthropic


# def anthropic_structured_resp(self, messages, schema):

#FAST_LLM = ChatGroq(model="llama-3.2-90b-vision-preview", temperature=0.0)
#FAST_LLM = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0)
#FAST_LLM = ChatGroq(model="llama-3.2-11b-vision-preview", temperature=0.0)
#FAST_LLM = ChatGroq(model="llama-3.2-3b-preview", temperature=0.0)
FAST_LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0.0) #, top_p=1.0
SMART_LLM = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0.0)
#GROQ_LLM = ChatGroq(model="llama-3.1-8b-instant")


# PROMPT_GROW_NODE = '''

# '''
# def grow_node_prompt():
