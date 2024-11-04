![](static/header.png)

Langur makes it simple to build consistent, observable, and portable LLM agents.

Like this:
```python
from langur import Langur
from langur.connectors import Workspace

agent = Langur("Grade quizzes")
agent.use(
    Workspace(path="./workspace")
)
agent.run()
```
This is an example that automatically identifies quizzes in the provided filesystem, grades them, and puts them into an empty `grades.csv` file.

The agent will:
1. Plan out how to "Grade quizzes" based on what we told it to `.use()` (just `Workspace` in this case).
2. Execute those actions

But maybe instead of executing the plan right way, we might want to observe it first. We can do this by passing a signal name to the `until` keyword when running the agent.
```
agent.run(until="plan")
```

### Current Issues
- Does not properly support multiple connectors of the same type (will be implemented)
- Behaviors cannot yet be arbitrarily combined, different combinations may not work as expected