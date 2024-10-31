class Assumption {
    assumption_id string @description("Unique natural language ID in lower_snake_case")
    assumption string @description("The assumption being made")
}

function CreateAssumptions(task: string, observables: string) -> Assumption[] {
    client Fallback
    prompt #"
        You are a component of a graph-driven agentic LLM system.

        Relevant context:
        {{observables}}

        ---

        Given the following task, create assumptions about how to complete the task.
        Task: {{task}}

        {{ctx.output_format}}
    "#
}