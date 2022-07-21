from src.gnt.encode.constants import *

from src.cls.main import Subject
from src.cls.main import Category
from src.cls.main import Shift
from src.cls.main import Section
from src.cls.main import ParallelSession
from src.cls.main import Capacity
from openpyxl import load_workbook

class EncodeAgent:
    def __init__(self) -> None:
        self.subjects   = dict[str, list[list[tuple[int, bool, str]] | Subject]]()
        self.categories = dict[str, Category]()
        self.shifts     = dict[str, Shift]()

        self.sorted_subjects = dict[int, dict[bool, dict[str, list[Subject]]]]()

    def reset(self, grade_level: int = None) -> None:
        if grade_level is None:
            self.subjects.clear()
            self.categories.clear()
        else:
            self.subjects[grade_level].clear()
            self.categories[grade_level].clear()
        self.sorted_subjects.clear()
        self.shifts.clear()

    def sort(self) -> None:
        for data, subject in self.subjects.values():
            grade_level, ranked, type = data
            if grade_level not in self.sorted_subjects:
                self.sorted_subjects[grade_level] = dict[bool, dict[str, list[Subject]]]()
            if ranked not in self.sorted_subjects[grade_level]:
                self.sorted_subjects[grade_level][ranked] = dict[str, list[Subject]]()
            if type not in self.sorted_subjects[grade_level][ranked]:
                self.sorted_subjects[grade_level][ranked][type] = list[Subject]()
            self.sorted_subjects[grade_level][ranked][type].append(subject)
        
    def xlsx(
        self,
        path:  str,
        sheet: str
    ) -> list[list[str]]:
        workbook  = load_workbook(
            filename=path,
            data_only=True
        )
        worksheet = workbook[sheet]
        data      = list()
        for row in worksheet.rows:
            line = list()
            for cell in row:
                if isinstance(cell.value, float):
                    line.append(str(int(cell.value)))
                else:
                    line.append(str(cell.value))
            if not all(
                cell == 'None'
                    for cell in line
            ):
                data.append(line)
        workbook.close()
        return data

    def find(self, name: str) -> Subject | Category:
        if name in self.categories:
            return self.categories[name]
        else:
            return self.subjects[name][1]

    def encode_subjects(self, path: str, reset: bool = True) -> None:
        if reset:
            self.reset()

        data = self.xlsx(path, SHIFTS)
        for r in range(1, len(data)):
            name  = data[r][0]
            shift = Shift(name)
            for c in range(2, 2 + int(data[r][1])):
                shift.add_partition(data[r][c])
            self.shifts[name] = shift

        data = self.xlsx(path, CLASSIFICATION)
        for r in range(2, len(data)):
            name              = data[r][0]
            max_group_members = None if not data[r][2].isdigit() else int(data[r][2])
            if data[r][3].upper() == 'Y':
                category = Category(
                    name=name,
                    max_group_members=max_group_members
                )
                self.categories[name] = category
            else:
                level   = None if not data[r][1].isdigit() else int(data[r][1])
                subject = Subject(
                    name=name,
                    level=level,
                    max_group_members=max_group_members
                )
                for c in range(4, len(data[r]), 3):
                    grade_level = data[1][c]
                    ranked      = data[1][c + 1].upper() == 'Y'
                    type        = data[1][c + 2]
                    is_type     = any(
                        item.upper() == 'Y'
                            for item in data[r][c:c + 3]
                    )
                    if is_type:
                        subject.add_teaches(GRADE_LEVELS[grade_level])
                        if str(subject) not in self.subjects:
                            self.subjects[str(subject)] = [[(GRADE_LEVELS[grade_level], ranked, type)], subject]
                        else:
                            self.subjects[str(subject)][0].append((GRADE_LEVELS[grade_level], ranked, type))
        
        data = self.xlsx(path, PREREQUISITES)
        for r in range(1, len(data)):
            object = self.find(data[r][0])
            for c in range(2, 2 + int(data[r][1])):
                prerequisite = tuple(
                    self.find(name)
                        for name in data[r][c].split(DELIMITER)
                )
                object.add_prerequisites(prerequisite)

        data = self.xlsx(path, NOT_ALONGSIDE)
        for r in range(1, len(data)):
            object = self.find(data[r][0])
            for c in range(2, 2 + int(data[r][1])):
                not_alongside = self.find(data[r][c])
                object.add_not_alongside(not_alongside)

        data = self.xlsx(path, SECTIONS)
        for r in range(2, len(data)):
            object = self.find(data[r][0])
            for c in range(2, 2 + int(data[r][1]), 6):
                shift = self.shifts[data[r][c + 2]]
                index = None if not data[r][c + 1].isdigit() else int(data[r][c + 1])
                object.add_section(Section(
                    shift=shift,
                    parallel_session=ParallelSession(
                        shift=shift,
                        partition=data[r][c],
                        index=index
                    ),
                    capacity=Capacity(
                        minimum=int(data[r][c + 3]),
                        ideal=int(data[r][c + 4]),
                        maximum=int(data[r][c + 5])
                    ),
                    parent=object
                ))

        self.sort()


encode_agent = EncodeAgent()