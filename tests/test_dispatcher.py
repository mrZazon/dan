from dan.core.dispatcher import Dispatcher
from dan.core.tool_registry import ToolRegistry
import asyncio

async def main():
    dispatcher = Dispatcher()
    registry = ToolRegistry()
    registry.discover()

    tool = dispatcher.dispatch(input("Enter a message: "))

    result = await registry.execute(tool)

    print(result)


asyncio.run(main())