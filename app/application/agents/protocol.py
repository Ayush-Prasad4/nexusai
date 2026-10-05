from typing import Protocol, TypeVar


InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class Agent(Protocol[InputT, OutputT]):
    async def run(self, input: InputT) -> OutputT:
        ...
