
function Think(context: string, description: string) -> string {
    client Fallback
    prompt #"
        You are a component of a graph-driven agentic LLM system.

        Relevant context:
        {{context}}

        ---
        
        Your job is to consider the context and do the following: {{description}}
    "#
}