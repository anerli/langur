from typing import Any, Dict, Optional
from baml_py import ClientRegistry
from pydantic import BaseModel

class LLMConfig(BaseModel):
    # Basically params for ClientRegistry
    # https://docs.boundaryml.com/docs/snippets/clients/overview
    # https://docs.boundaryml.com/docs/calling-baml/client-registry
    provider: str
    options: Dict[str, Any]
    retry_policy: Optional[str] = None

    def to_registry(self) -> ClientRegistry:
        cr = ClientRegistry()
        cr.add_llm_client(
            name="Primary",
            provider=self.provider,
            options=self.options,
            retry_policy=self.retry_policy
        )
        cr.set_primary("Primary")
        return cr
