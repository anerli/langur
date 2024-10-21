// class ActionInput {
//     @@dynamic
// }

// enum ActionType {
//     // THINK @description("Do purely cognitive processing.")
//     // FILE_WRITE @description("Read and subsequently overwrite a file's contents.")
//     // FILE_READ @description("Read a single file's contents.")
//     @@dynamic
// }

class Action {
    node_id string @description("A unique natural language ID in lower_snake_case which reflects the action use.")
    //action_type ActionType
    upstream_action_ids string[] @description("Define which other actions this one depends on")
    //action_input ActionInput @description("Provide inputs if known else null. Do not hallicinate values.")
    @@dynamic
}


function TaskToActions (goal: string, observables: string, task: string, action_definitions: string, upstream_actions: string) -> Action[] {
    client Default
    prompt #"
        You are a component of a graph-driven agentic LLM system.

        Your overall goal is: {{goal}}

        Relevant context:
        {{observables}}

        **upstream_action_ids**:
        {{upstream_actions}}
        These upstream actions have already been created, do not include them in your response.

        You are planning out the execution of specific actions to help accomplish the goal.
        Given a specific Task node, your job is to convert it into specific ActionUse nodes, representing distinct uses of various available actions.
        Create actions such that when executed, they will complete the task.

        When you provide action inputs, you have a choice whether to provide parameters or null.
        When the parameter is known right now as part of the plan, provide it.
        If its not known or depends on some other result, leave it as null.
        
        Your specific task to break down is: {{task}}

        {{ctx.output_format}}
    "#
}

// Doesn't work cus we can't define the @@dynamic action_input property for the test case in here
