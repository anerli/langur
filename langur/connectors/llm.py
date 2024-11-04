from langur.actions import ActionContext
from langur.connector import Connector, action
import langur.baml_client as baml

class LLM(Connector):
    @action
    async def think(self, ctx: ActionContext) -> str:
        '''Do purely cognitive processing'''
        return await baml.b.Think(
            context=ctx.ctx,
            description=ctx.purpose,
            baml_options={"client_registry": ctx.cg.get_client_registry()}
        )
