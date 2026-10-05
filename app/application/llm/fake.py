class FakeLLMClient:
    def __init__(self, response: str = "fake response") -> None:
        self.response = response
        self.prompts: list[str] = []

    async def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.response
