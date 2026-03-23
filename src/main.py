import os
import asyncio
import logging
from dacn.core import Agent, CoordinationProtocol
from dacn.utils import configure_logger

CONFIG_PATH = os.getenv("DACN_CONFIG_PATH", "config.yaml")

async def main():
    configure_logger(logging.INFO)
    protocol = CoordinationProtocol.from_config(CONFIG_PATH)
    agent = Agent(protocol)
    await agent.start()

if __name__ == "__main__":
    asyncio.run(main())