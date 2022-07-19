import src.syp.g11.constants
import src.syp.g12.constants

from src.gnt.encode.constants import *

from openpyxl           import load_workbook
from src.cls.main       import Subject
from src.cls.main       import Category
from src.syp.g11.main   import G11
from src.syp.g12.main   import G12
from src.gnt.write.main import writer_agent
from src.cls.main       import Group
from src.cls.main       import Section
from src.cls.main       import Shift
from src.cls.main       import ParallelSession
from src.cls.main       import Capacity


class EncodeAgent:
    def subjects(self, path: str) -> None:
        '''Resets subjects, and then encodes'''
        self.__reset__()

        subjects   = dict[str, Subject]()
        categories = set[Category]()
        shifts     = dict[str, Shift]()

        cls = self.xlsx(path, CLASSIFICATION)
        for r in range(2, len(cls)):
            name  = cls[r][0]
            level = int() if not cls[r][1].isdigit() else int(cls[r][1])
            
            is_category = cls[r][2] == 'Y'
            if is_category:
                category = Category(name)
                categories.add(category)
            else:
                subject = Subject(name, level)
                subjects[subject.name] = subject
                for c in range(3, len(cls[r]), 2):
                    grade_level    = cls[1][c]
                    classification = cls[1][c + 1]
                    if 'Y' in cls[r][c:c + 1]:
                        match grade_level:
                            case src.syp.g11.constants.STR:
                                src.syp.g11.constants.RANKED[classification].append(subject)
                            case src.syp.g12.constants.STR:
                                src.syp.g12.constants.RANKED[classification].append(subject)

        prq = self.xlsx(path, PREREQUISITES)
        for r in range(1, len(prq)):
            name = prq[r][0]
            count = int(prq[r][1])
            for c in range(2, 2 + count):
                pre = tuple[Subject](
                    subjects[subject]
                        for subject in prq[r][c].split(DELIMITER)
                )
                subjects[name].add_prerequisite(pre)

        nas = self.xlsx(path, NOT_ALONGSIDE)
        for r in range(1, len(nas)):
            name = nas[r][0]
            count = int(nas[r][1])
            for c in range(2, 2 + count):
                subjects[name].add_not_alongside(subjects[nas[r][c]])

        sft = self.xlsx(path, SHIFTS)
        for r in range(1, len(sft)):
            name         = sft[r][0]
            shift        = Shift(name=name)
            shifts[name] = shift

            count = int(sft[r][1])
            for c in range(2, 2 + count):
                part = sft[r][c]
                shift.add_partition(part)

        scs = self.xlsx(path, SECTIONS)
        for r in range(2, len(scs)):
            name = scs[r][0]
            cont = int(scs[r][1])
            for c in range(2, 2 + cont * 6, 6):
                typ =     scs[r][c]
                ind = int(scs[r][c + 1]) if scs[r][c + 1] != 'None' else int()
                sft =     scs[r][c + 2]
                pss = ParallelSession(
                    shifts[sft],
                    typ,
                    ind
                )

                min = int(scs[r][c + 3])
                idl = int(scs[r][c + 4])
                max = int(scs[r][c + 5])
                cap = Capacity(min, idl, max)

                subjects[name].add_section(Section(
                    shifts[sft],
                    pss,
                    cap,
                    subjects[name]
                ))

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
            data.append(line)
        workbook.close()
        return data

    def g11(self, path: str) -> list[G11]:
        data     = self.xlsx(path, src.syp.g11.constants.STR)
        students = list()

        #  TODO: Encode grade 11 students' data
        raise NotImplementedError()

    def g12(self, path: str) -> list[G12]:
        groups = dict[str, Group]()
        for sheet in writer_agent.get_sheetnames(path):
            if sheet.find(src.syp.g12.constants.GRP) != -1:
                data = self.xlsx(path, sheet)
                
                #  TODO: Encode grade 12 students' groups
                raise NotImplementedError()

        data     = self.xlsx(path, src.syp.g12.constants.STR)
        students = list()

        #  TODO: Encode grade 12 students' data
        raise NotImplementedError()

    def __reset__(self, grade_level: int = None) -> None:
        match grade_level:
            case None:
                G11.__clear_subjects__()
                G12.__clear_subjects__()
            case 11:
                G11.__clear_subjects__()
            case 12:
                G12.__clear_subjects__()


encode_agent = EncodeAgent()