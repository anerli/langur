// class ActionInput {
//     @@dynamic
// }

class Action {
    node_id string @description("UNIQUE node ID. DO NOT reuse any IDs you have seen before.")
    action_type string
    //action_input ActionInput @description("Input for the action. For each parameter, include it if known right now, otherwise omit it completely.")
    upstream_action_ids string[]
    @@dynamic
}

function TaskToActions (goal: string, observables: string, task: string, action_definitions: string, upstream_actions: string) -> Action[] {
    client Fast
    prompt #"
        You are a component of a graph-driven agentic LLM system.

        Your overall goal is: {{goal}}

        Relevant context:
        {{observables}}

        You are planning out the execution of specific actions to help accomplish the goal.
        Given a specific Task node, your job is to convert it into specific ActionUse nodes, representing distinct uses of various available actions.
        Create actions such that when executed, they will complete the task.

        When you create an action you must include:

        **node_id**: a unique natural language ID in lower_snake_case describing the action use

        **action_type**: The type identifier for the action being used, from these available types:
        {{action_definitions}}

        **action_input**: For each input parameter, either provide the input value if known, or do not include at all if it depends on another result.

        **upstream_action_ids**: Define which actions the action depends on, from these upstream actions OR from other ones you generate:
        {{upstream_actions}}

        These upstream actions have already been created, do not include them in your response.

        Your specific task to break down is: {{task}}

        {{ctx.output_format}}
    "#
}

test write_grades {
  functions [TaskToActions]
  args {
    upstream_actions #""#
    observables #"
      The current working directory is `.`, which contains these files/subdirectories:
      ./grades.csv
      ./rubric.txt
      ./papers/Student A_test.txt
      ./papers/Student B_test.txt
      ./papers/Student C_test.txt
      ./papers/Student D_test.txt
      ./papers/Student E_test.txt
    "#
    task #"write_grades: Write the assigned grades to grades.csv. ['file_write']"#
    goal #"Grade student papers"#
    action_definitions #"
      - think: Do purely cognitive processing.
      - file_write: Read and subsequently overwrite a file's contents.
      - file_read: Read a single file's contents.
    "#
  }
}