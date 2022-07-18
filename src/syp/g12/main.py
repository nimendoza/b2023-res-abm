from src.syp.g12.constants import *

from src.syp.g11.main import G11
from src.cls.main     import Student
from src.cls.main     import Shift
from src.cls.main     import Subject

class G12(Student):
    def __init__(
        self,
        id:    str,
        shift: Shift
    ) -> None:
        super(G12, self).__init__(
            id,
            INT,
            shift,
            list(RANKED.keys())
        )

        self.g11 = G11('12-{}'.format(self.id))

    def default_ranking(self, type: str) -> None:
        self.frank.clear(type)
        for subject in RANKED[type]:
            self.frank.add(type, subject)

    def took(
        self,
        type:    str,
        subject: Subject
    ) -> None:
        self.g11.has_taken(type, subject)

    def taken(self) -> list[Subject]:
        return self.g11.takes()