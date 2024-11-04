from langur import Langur, Signal
from langur.connectors import Workspace, LLM, Terminal



def run():
    agent = Langur("Compare speed for two methods of prime number generation")
    agent.use(
        Workspace(path="./workspace").enable("exec"),
        LLM(),
        Terminal().disable("input")
    )
    agent.run(until=Signal.PLAN_DONE)
    agent.save_graph_html("./workspace/plan.html")
    agent.run()
    agent.save("./workspace/agent.json")
    agent.save_graph_html("./workspace/final.html")