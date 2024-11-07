from langur import Langur
from langur.connectors import Terminal
from langchain_community.agent_toolkits import FileManagementToolkit

'''
Basic example showing how you can directly pass a toolkit to Langur to access all the respective tools.
'''

agent = Langur("Summarize one of the files in this directory")
fs_toolkit = FileManagementToolkit(
    root_dir=".",
    selected_tools=["read_file", "list_directory"],
)
agent.use(
    fs_toolkit,
    Terminal().disable("input")
)
agent.run()