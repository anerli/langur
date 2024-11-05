from langur import Langur
from langur.connectors import Workspace, LLM

agent = Langur("Grade quizzes")
agent.use(
    Workspace(path="./workspace")
)
agent.run()
