from trakit.config import Config
from trakit.patterns import configure

rebulk = configure(Config())


def trakit(string: str):
    matches = rebulk.matches(string)

    return matches.to_dict()
