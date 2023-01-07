import json
import sys

from trackit import api


def main(value: str, *args):
    print(json.dumps(api.trackit(value), ensure_ascii=False, indent=2, default=lambda x: str(x)))


if __name__ == '__main__':
    main(*sys.argv[1:])
