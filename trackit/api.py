from trackit.config import Config
from trackit.patterns import configure

rebulk = configure(Config())


def trackit(string: str):
    matches = rebulk.matches(string)

    return matches.to_dict()
