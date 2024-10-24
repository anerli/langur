// Learn more about clients at https://docs.boundaryml.com/docs/snippets/clients/overview

client<llm> Default {
    provider openai
    options {
        model "gpt-4o-mini"
        api_key env.OPENAI_API_KEY
        temperature 0.0
    }
}

client<llm> Fast {
    provider openai
    options {
        model "gpt-4o-mini"
        api_key env.OPENAI_API_KEY
        temperature 0.0
    }
}

client<llm> Smart {
    provider anthropic
    options {
        model "claude-3-5-sonnet-20241022"
        api_key env.ANTHROPIC_API_KEY
        temperature 0.0
    }
}
