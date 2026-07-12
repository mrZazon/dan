import asyncio

from dan.core.tool_registry import ToolRegistry


async def main():

    registry = ToolRegistry()

    registry.discover()

    print(registry.list())

    result = await registry.execute(
        "hour"
    )

    print(result)


asyncio.run(main())