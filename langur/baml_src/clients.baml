// In Langur, clients are defined with a ClientRegistry programatically - so these are just for testing.
// Learn more about clients at https://docs.boundaryml.com/docs/snippets/clients/overview

client<llm> Fallback {
    provider anthropic
    options {
        model "claude-3-5-sonnet-20241022"
        api_key env.ANTHROPIC_API_KEY
        temperature 0.0
    }
}
