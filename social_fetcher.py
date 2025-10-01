import random
from typing import Dict


class MockFetcher:
    def __init__(self):
        self.state: Dict[str, int] = {}

    def register(self, handle: str, initial: int = None):
        if handle in self.state:
            return
        if initial is None:
            initial = random.randint(50, 2000)
        self.state[handle] = initial

    def fetch(self, handle: str) -> int:
        if handle not in self.state:
            self.register(handle)
        cur = self.state[handle]
        if random.random() < 0.1:
            cur += random.randint(-300, 800)
        else:
            cur += random.randint(-10, 20)
        cur = max(0, cur)
        self.state[handle] = cur
        return cur


mock_fetcher = MockFetcher()
