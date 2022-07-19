from src.gnt.parse.constants import *

from src.gnt.encode.main import encode_agent


class ParseAgent:
    def terminal(self) -> None:
        subjects_encoded = False

        def encode_subjects() -> None:
            with open(PATHS[SUBJECT_DESC], 'r') as file:
                for line in file.readlines():
                    print(line, end='')
            subject_path = input('Subject data file path: ')
            encode_agent.subjects(subject_path)
            subjects_encoded = True

        def check_subjects() -> None:
            if subjects_encoded:
                reencode = input('Re-encode subjects? (Y/N): ').upper() == 'Y'
                if reencode:
                    encode_subjects()
            else:
                encode_subjects()

        def validate() -> None:
            check_subjects()

            runs = int(input('Number of files to validate: '))
            for run in range(runs):
                input_path = input('File path #{}: '.format(run + 1))
                #  TODO: Complete this
                raise NotImplementedError()

        def main() -> None:
            with open(PATHS[REQUEST], 'r') as file:
                for line in file.readlines():
                    print(line, end='')
            match input('Request: ').upper():
                case 'GENERATE':
                    #  TODO: Complete this
                    raise NotImplementedError()
                case 'VALIDATE':
                    validate()

        run_again = True
        while run_again:
            main()
            run_again = input('Run program again? (Y/N): ').upper() == 'Y'
    

if __name__ == '__main__':
    parse_agent = ParseAgent()
    if TERMINAL:
        parse_agent.terminal()