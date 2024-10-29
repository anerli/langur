class FilledParams {
    @@dynamic
}

function FillParams(context: string, action_desc: string, filled_inputs: string, needed_inputs: string) -> FilledParams {
    client Fallback
    prompt #"
        You are a component of a graph-driven agentic LLM system.

        Relevant context:
        {{context}}

        ---
        
        Your job is to fill in missing inputs for a certain action.

        The action is:
        {{action_desc}}

        These inputs are already filled:
        {{filled_inputs}}

        You need to provide:
        {{needed_inputs}}

        {{ctx.output_format}}
    "#
}