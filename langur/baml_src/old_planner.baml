class OldNode {
    id string
    content string
    action_types string[]
}

class OldEdge {
    from_id string
    to_id string
}

class SubtaskSubgraph {
    nodes OldNode[]
    edges OldEdge[]
}

function PlanSubtasks (goal: string, graph_context: string, action_types: string) -> SubtaskSubgraph {
    client Fallback
    prompt #"
        You are a component of a graph-driven agentic LLM system.

        Your overall goal is: {{goal}}

        For reference, here is the current graph:
        {{graph_context}}

        ---

        Your job is to design a subgraph which decomposes the final goal into a dependency chain of subtasks.
        You can do this by creating nodes, each of which defines a subtasks, and edges, which represent a dependency relation.
        In an edge dependency relation, you should choose the direction such that the FROM node should be completed before the TO node.
        Please capture all relevant dependency relations with edges.
        Design each subtask by observing the available actions and resources in the graph, and be as specific as possible.
        When you create a node, give each a natural language ID in lower_snake_case, as well as the content of the subtask itself.
        For each node, provide also the action types required to execute the subtask from the following:
        {{action_types}}

        {{ctx.output_format}}
    "#
}

test grade_papers {
    functions [PlanSubtasks]
    args {
        goal "Grade Papers"
        graph_context #"
            Node ID: file_read
            Node Edges:
            Node Content:
            Action ID: file_read
            Action Description: Read a single file's contents.
            Action Input Schema:
            {"file_path": {"type": "string"}}

            Node ID: file_write
            Node Edges:
            Node Content:
            Action ID: file_write
            Action Description: Read and subsequently overwrite a file's contents.
            Action Input Schema:
            {"file_path": {"type": "string"}, "new_content": {"type": "string"}}

            Node ID: final_goal
            Node Edges:
            Node Content:
            Grade student papers []

            Node ID: think
            Node Edges:
            Node Content:
            Action ID: think
            Action Description: Do purely cognitive processing.
            Action Input Schema:
            {}

            Node ID: workspace
            Node Edges:
            Node Content:
            The current working directory is `.`, which contains these files/subdirectories:
            ./grades.csv
            ./rubric.txt
            ./papers/Student A_test.txt
            ./papers/Student B_test.txt
            ./papers/Student C_test.txt
            ./papers/Student D_test.txt
            ./papers/Student E_test.txt
        "#
        action_types #"
            - file_read
            - file_write
            - think
        "#
    }
}