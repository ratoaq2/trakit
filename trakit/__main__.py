import json
import sys

from trakit import api


def main(value: str, *args):
    print(json.dumps(api.trakit(value), ensure_ascii=False, indent=2, default=lambda x: str(x)))


if __name__ == '__main__':
    main(*sys.argv[1:])
