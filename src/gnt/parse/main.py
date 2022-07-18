from src.gnt.parse.constants import *

from src.gnt.encode.main import EncodeAgent


class ParseAgent:
    def __init__(self) -> None:
        print('Encoding subject test data at \'{}\''.format(SUBJECTS_PATH))
        self.encode_agent = EncodeAgent(SUBJECTS_PATH)

    def reset(self, grade_level: int = None) -> None:
        self.encode_agent.reset(grade_level)
        self.__init__()

    def terminal(self) -> None:
        #  TODO: Complete terminal input/output
        raise NotImplementedError()


if __name__ == '__main__':
    parse_agent = ParseAgent()
    if TERMINAL:
        parse_agent.terminal()