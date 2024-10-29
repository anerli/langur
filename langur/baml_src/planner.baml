// class Node {
//     id string
//     content string
//     action_types string[]
// }

// Action
class ActionNode {
    id string @description("A unique natural language ID in lower_snake_case which reflects the action use.")
    description string @description("Description of what this action is for.")
    //upstream_action_ids string[] @description("Define which other actions this one depends on")
    //action_input ActionInput @description("Provide inputs if known else null. Do not hallicinate values.")
    @@dynamic
}

class Edge {
    from_id string
    to_id string
}

class Graph {
    nodes ActionNode[]
    edges Edge[]
}

function PlanActions (goal: string, observables: string, action_types: string) -> Graph {
    client Fallback
    prompt #"
        You are a component of a graph-driven agentic LLM system.

        Your overall goal is: {{goal}}

        Relevant context:
        {{observables}}

        ---

        Your job is to plan out the execution of the given task by designing a graph of actions with dependency relations.
        You can do this by creating nodes, each of which defines an action, and edges, which represent a dependency relation.
        In an edge dependency relation, you should choose the direction such that the FROM node should be completed before the TO node.
        Please capture all relevant dependency relations with edges.
        Design each action by observing the available action types and resources in the graph, and be as specific as possible.

        When you provide action inputs, you have a choice whether to provide parameters or null.
        When the parameter is known right now as part of the plan, provide it.
        If its not known or depends on some other result, leave it as null.

        For each node, provide also the action type from the following:
        {{action_types}}

        {{ctx.output_format}}
    "#
}
