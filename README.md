![](static/header.png)

Langur makes it simple to build consistent, observable, and portable LLM agents.

> ⚠️ Langur is early in development. Expect frequent breaking changes. Depending on how it's configured Langur may be able to access arbitrary files or run code - use at your own risk.

## Installation
```
pip install langur
```

## Example

Here's a simple task solved using a Langur agent:
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
```python
from langur import Signal

agent.run(until=Signal.PLAN_DONE)
```
Then to observe the agent's plan, we can look at the corresponding behavioral graph. This can be done like so:
```python
# In a Jupyter notebook
agent.show()
```
or
```python
# Outside of a Jupyter notebook
agent.save_graph_html("agent.html")
```
> This system for viewing the agent behavior graph is temporary and will be improved.

For this simple example, the behavior graph might look something like:

![](static/grading_graph.png)

But maybe this plan/execute behavior just doesn't work for your agent use case! Well don't worry, another key tenet of Langur's design is to have **modular behavior**. Learn more in [Customizing Behavior](#customizing-behavior).

## Building Connectors

## How it Works
Langur's behavior is driven entirely by various "metacognitive workers" operating on a shared "cognition graph". These workers might manipulate the graph itself, or they might be interacting with the real-world and relaying that information to the graph. Workers that interact with the real-world are also called [Connectors](#building-connectors), and Langur is designed to make these [Connectors](#building-connectors) easy to implement to define new modes of interaction with the world.

Why this approach?
1. Modular behavior - Agent behavior is driven by several workers instead of a centralized system. This makes it easier to add new behavior without accidentally affecting all other facets of behavior, and makes it possible for advanced users to design and include their own custom behavior.
2. Observability - Being able to see a graph representing the agent's behavior is incredibly useful for visually understanding the agent's intent, and promotes sanity as a developer designing systems that operate on the graph.
3. Parallelizability - Workers can potentially run in parallel (or concurrently really) - and since many of these workers are using LLMs to operate on the graph, we can speed up these I/O bound prompts.
4. Serializability - Since all behavior state is stored in the graph, we can save and load the graph in order to save and load agent behavior.

## Customizing Behavior


## Known Issues
- Does not properly support multiple connectors of the same type (will be implemented)
- Behaviors cannot yet be arbitrarily combined, different combinations may not work as expected