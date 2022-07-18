from src.syp.g11.constants import *

from src.cls.main import Student
from src.cls.main import Shift


class G11(Student):
    def __init__(
        self,
        id:    str,
        shift: Shift
    ) -> None:
        super(G11, self).__init__(
            id,
            INT,
            shift,
            list(RANKED.keys())
        )
    
    def default_ranking(self, type: str) -> None:
        self.frank.clear(type)
        for subject in RANKED[type]:
            self.frank.add(type, subject)

    def has_taken(
        self,
        type:    str,
        subject: Subject
    ) -> None:
        self.subjects[type] = subject