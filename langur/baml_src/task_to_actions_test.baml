
class ActionInput {
    file_path string?
    new_content string?
}


enum ActionTypeTest {
    THINK @description("Do purely cognitive processing.")
    FILE_WRITE @description("Read and subsequently overwrite a file's contents.")
    FILE_READ @description("Read a single file's contents.")
}

class ActionTest {
    node_id string @description("A unique natural language ID in lower_snake_case which reflects the action use.")
    action_type ActionTypeTest
    upstream_action_ids string[] @description("Define which other actions this one depends on")
    action_input ActionInput @description("Provide inputs if known else null. Do not hallicinate values.")
}


function TaskToActionsTest (goal: string, observables: string, task: string, action_definitions: string, upstream_actions: string) -> ActionTest[] {
    client Fallback
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