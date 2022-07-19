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


class EncodeAgent:
    def subjects(self, path: str) -> None:
        '''Resets subjects, and then encodes'''
        self.__reset__()

        subjects   = dict[str, Subject]()
        categories = set[Category]()

        #  TODO: Encode subjects and categories
        raise NotImplementedError()

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