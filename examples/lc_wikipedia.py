from langur import Langur, Signal, Connector, action
from langur.connectors import Workspace, Terminal, LLM
from langur.util.schema import schema_from_lc_tool
from langur.util.registries import action_node_type_registry

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

api_wrapper = WikipediaAPIWrapper(top_k_results=1)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

agent = Langur("Find me some interesting monkey facts")
# You can pass langchain tools directly into use()
agent.use(
    wiki_tool,
    Terminal().disable("input")
)
agent.run()
