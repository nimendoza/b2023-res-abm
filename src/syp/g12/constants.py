from src.cls.constants import *

from src.cls.main import Subject

STR = 'Grade 12'
INT = 12

CORES = list[Subject]()
ELECS = list[Subject]()
MATHS = list[Subject]()
CATEG = list[Subject]()

RANKED = {
    COR: CORES,
    ELC: ELECS,
    MTH: MATHS
}
NANKED = {
    ASA: list[Subject](),
    BLK: list[Subject](),
    RES: list[Subject]()
}