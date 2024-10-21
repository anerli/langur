
class ActionInput {
    file_path string?
    new_content string?
}

class ActionTest {
    node_id string @description("UNIQUE node ID. DO NOT reuse any IDs you have seen before.")
    action_type string
    upstream_action_ids string[]
    action_input ActionInput @description("Provide inputs if known else null. Do not hallicinate values.")
}

function TaskToActionsTest (goal: string, observables: string, task: string, action_definitions: string, upstream_actions: string) -> ActionTest[] {
    client Default
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

// Doesn't work cus we can't define the @@dynamic action_input property for the test case in here
// hacked by creating a dupe test, jank
test write_grades {
    functions [TaskToActionsTest]
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

test Circularchipmunk {
  functions [TaskToActionsTest]
  args {
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
    task #"write_grades: Write the grades and feedback for each student into the grades.csv file. ['file_write']"#
    action_definitions #"
      - think: Do purely cognitive processing.
      - file_write: Read and subsequently overwrite a file's contents.
      - file_read: Read a single file's contents.
    "#
    goal #"Grade student papers"#
    upstream_actions #"
      - read_student_b_paper
      - read_rubric_file
      - read_student_c_paper
      - read_student_e_paper
      - grade_student_c_paper
      - read_student_a_paper
      - grade_student_a_paper
      - grade_student_e_paper
      - read_student_d_paper
      - grade_student_b_paper
      - grade_student_d_paper
    "#
  }
}