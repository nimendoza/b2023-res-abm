from __future__        import annotations
from src.cls.constants import INF


class Capacity:
    def __init__(
        self,
        minimum: int,
        ideal:   int,
        maximum: int,
        filled:  int = None
    ) -> None:
        self.minimum = minimum
        self.ideal   = ideal
        self.maximum = maximum

        if filled is None:
            self.filled = int()
        else:
            self.filled = filled
    
    def __repr__(self) -> str:
        return '{}/{}'.format(self.filled, self.maximum)
        
    @property
    def available(self) -> int:
        return self.maximum - self.filled

    def accept(self, value: int) -> None:
        if self.filled + value <= self.maximum:
            raise Exception()
        else:
            self.filled += value

    def increase(self, other: Capacity) -> None:
        self.minimum += other.minimum
        self.ideal   += other.ideal
        self.maximum += other.maximum
        self.accept(other.filled)


class Shift:
    def __init__(
        self,
        id:         str      = None,
        partitions: set[str] = None
    ) -> None:
        self._id = id
        
        if partitions is None:
            self._partitions = set()
        else:
            self._partitions = partitions
    
    def __repr__(self) -> str:
        return self.id

    @property
    def id(self) -> str:
        if self._id is None:
            return ''.join(self.partitions)
        else:
            return self._id

    @property
    def partitions(self) -> set[str]:
        return self._partitions

    def add_partition(self, value: str) -> None:
        self._partitions.add(value)


class ParallelSession:
    def __init__(
        self,
        shift:     Shift,
        partition: str,
        index:     int   = None,
        id:        str   = None
    ) -> None:
        self._shift     = shift
        self._partition = partition
        assert self.partition in self.shift.partitions

        self._index = index
        self._id    = id
    
    def __repr__(self) -> str:
        raise NotImplementedError()

    @property
    def shift(self) -> Shift:
        return self._shift

    @property
    def partition(self) -> str:
        return self._partition

    @property
    def index(self) -> str:
        if self._index is None:
            return ''
        else:
            return str(self._index)

    @property
    def id(self) -> str:
        if self._id is None:
            return ''.join([self.partition, self.index])
        else:
            return self._id


class Rank:
    def __init__(
        self,
        id:    str,
        types: list[str]
    ) -> None:
        self._id    = 'RANK-{}'.format(id)
        self._types = set(types)

        self._lst = dict(
            (type, list[Subject]())
                for type in self.types
        )
        self._set = dict(
            (type, set[Subject]())
                for type in self.types
        )
        self._rsn = dict(
            (type, list[str]())
                for type in self.types
        )
    
    def __repr__(self) -> str:
        return self.id

    @property
    def id(self) -> str:
        return self._id

    @property
    def types(self) -> set[str]:
        return self._types

    def add(
        self,
        type:    str,
        subject: Subject
    ) -> None:
        if subject not in self._set[type]:
            self._lst[type].append(subject)
            self._set[type].add(subject)

    def get(
        self,
        type:  str,
        index: int
    ) -> Subject:
        return self._lst[type][index]

    def all(self, type: str) -> list[Subject]:
        return self._lst[type]

    def reject(
        self,
        type:    str,
        subject: Subject,
        reason:  str
    ) -> None:
        self._lst[type].remove(subject)
        self._set[type].remove(subject)
        self._rsn[type].append('{}: {}'.format(subject, reason))

    def clear(self, type: str) -> None:
        self._lst[type].clear()
        self._set[type].clear()


class Rankings:
    def __init__(
        self,
        id:      str,
        to_rank: list[str]
    ) -> None:
        self._id = 'RANKING-{}'.format(id)

        self.initial = Rank('{}I'.format(id), to_rank)
        self.final   = Rank('{}F'.format(id), to_rank)
    
    def __repr__(self) -> str:
        return self.id

    @property
    def id(self) -> str:
        return self._id


class Section:
    def __init__(
        self,
        shift:            Shift,
        parallel_session: ParallelSession,
        capacity:         Capacity,
        parent:           Subject | Category,
        name:             str                 = None,
        students:         set[Student]        = None
    ) -> None:
        self._shift            = shift
        self._parallel_session = parallel_session
        assert self.parallel_session.shift in self.shift.partitions

        self._name     = name
        self._parent   = parent

        if students is None:
            self._students = set()
        else:
            self._students = students

        self.capacity = capacity
    
    def __repr__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        if self._name is None:
            return '{} {}'.format(self.parent, self.parallel_session)
        else:
            return self._name

    @property
    def parallel_session(self) -> ParallelSession:
        return self._parallel_session

    @property
    def shift(self) -> Shift:
        return self._shift

    @property
    def parent(self) -> Subject | Category:
        return self._parent

    @property
    def students(self) -> set[Student]:
        return self._students

    def add_student(self, student: Student) -> tuple[bool, str | None]:
        def ok_groupmates(student: Student) -> bool:
            for group in student.groups:
                if group.required:
                    if group.parent == self.parent:
                        for member in group.students:
                            if self.parent in member.attends and member.sections[self.parent] not in {self, None}:
                                return False
                    for member in group.students:
                        if member.shift not in {self.shift, None}:
                            return False

        if self.capacity.available <= 0:
            return False, 'Full'
        elif student.shift not in {self.shift, None}:
            return False, 'Incompatible shift'
        elif student.sessions[self.parallel_session.partition] is not None:
            return False, 'Already attending a parallel session'
        elif len(self._students.intersection(student.not_alongside)) > 0:
            return False, 'Incompatible classmate/s'
        elif not self._students.issuperset(student.prerequisites):
            return False, 'Prerequisite classmate/s not present'
        elif not ok_groupmates(student):
            return False, 'Incompatible with groupmates'
        else:
            self._students.add(student)
            self.capacity.accept(1)

            student.add_section(self.parent, self)
            return True, None


class Category:
    def __init__(
        self,
        name:              str,
        capacity:          Capacity                = None,
        prerequisites:     set[Subject | Category] = None,
        not_alongside:     set[Subject | Category] = None,
        max_group_members: int                     = None,
        students:          set[Student]            = None
    ) -> None:
        self._name              = name

        if max_group_members is None:
            self._max_group_members = int()
        else:
            self._max_group_members = max_group_members
        
        if students is None:
            self._students = set()
        else:
            self._students = students

        if prerequisites is None:
            self._prerequisites = set()
        else:
            self._prerequisites = prerequisites
        
        if not_alongside is None:
            self._not_alongside = set()
        else:
            self._not_alongside = not_alongside

        if capacity is None:
            self.capacity = Capacity(0, INF, INF)
        else:
            self.capacity = capacity
    
    def __repr__(self) -> str:
        return self.name

    @property
    def prerequisites(self) -> set[tuple[Subject | Category]]:
        return self._prerequisites

    def add_prerequisites(self, objects: tuple[Subject | Category]) -> None:
        if self in objects:
            raise Exception()
        elif len(set(objects).intersection(self.not_alongside)) > 0:
            raise Exception()
        else:
            self._prerequisites.add(objects)

    @property
    def not_alongside(self) -> set[Subject | Category]:
        return self._not_alongside

    def add_not_alongside(self, object: Subject | Category) -> None:
        if self == object:
            raise Exception()
        else:
            self._not_alongside.add(object)

    @property
    def name(self) -> str:
        return self._name

    @property
    def max_group_members(self) -> int:
        return self._max_group_members

    @property
    def students(self) -> set[Student]:
        return self._students

    def add_student(self, student: Student) -> tuple[bool, str | None]:
        '''Returns whether the student was added and any reason why the student wasn't added, if applicable'''
        def ok_prerequisites(student: Student) -> bool:
            for prerequisites in self.prerequsites:
                if len(student.taken.intersection(set(prerequisites))) == 0:
                    return False
            return True

        if self.capacity.available <= 0:
            return False, 'Full'
        elif not ok_prerequisites(student):
            return False, 'Prerequisites not met'
        elif len(student.attends.intersection(self.not_alongside)) > 0:
            return False, 'Incompatible with subject'
        else:
            self._students.add(student)
            self.capacity.accept(1)

            student.add_category(str(self), self)
            return True, None


class Student:
    def __init__(
        self,
        id:            str,
        level:         int,
        to_rank:       list[str],
        shift:         Shift                                    = None,
        subjects:      dict[str, Subject | None]                = None,
        categories:    dict[str, Category | None]               = None,
        sections:      dict[Subject | Category, Section | None] = None,
        groups:        dict[Subject | Category, Group]          = None,
        prerequisites: set[Student]                             = None,
        not_alongside: set[Student]                             = None,
        previous:      Student                                  = None
    ) -> None:
        self._id            = id
        self._level         = level
        self._shift         = shift
        self._to_rank       = to_rank

        if subjects is None:
            self._subjects = dict()
        else:
            self._subjects = subjects

        if categories is None:
            self._categories = dict()
        else:
            self._categories = categories

        if sections is None:
            self._sections = dict()
        else:
            self._sections = sections

        if groups is None:
            self._groups = dict()
        else:
            self._groups = groups

        if prerequisites is None:
            self._prerequisites = set()
        else:
            self._prerequisites = prerequisites

        if not_alongside is None:
            self._not_alongside = set()
        else:
            self._not_alongside = not_alongside

        self._previous      = previous

        self.rankings = Rankings(self.id, self.to_rank)
    
    def __repr__(self) -> str:
        return self.id

    @property
    def id(self) -> str:
        return self._id

    @property
    def to_rank(self) -> list[str]:
        return self._to_rank

    @property
    def shift(self) -> Shift | None:
        return self._shift

    @shift.setter
    def shift(self, shift: Shift) -> None:
        self._shift = shift

    @property
    def to_rank(self) -> list[str]:
        return self._to_rank

    @property
    def subjects(self) -> dict[str, Subject]:
        return self._subjects

    def add_subject(
        self,
        type:    str,
        subject: Subject = None
    ) -> None:
        self._subjects[type] = subject
        if subject is not None:
            self.add_section(subject)
            self.add_attends(subject)

    @property
    def categories(self) -> dict[str, Category]:
        return self._categories

    def add_category(
        self,
        type: str,
        category: Category = None
    ) -> None:
        self._categories[type] = category
        if category is not None:
            self.add_section(category)
            self.add_attends(category)

    @property
    def sections(self) -> dict[Subject | Category, Section]:
        return self._sections

    def add_section(
        self, 
        parent: Subject | Category, 
        section: Section = None
    ) -> None:
        self._sections[parent] = section
        if self.shift is None:
            self.shift = section.shift
        else:
            raise Exception()

    @property
    def groups(self) -> dict[Subject | Category, Group]:
        return self._groups

    def add_group(self, parent: Subject | Category, group: Group) -> None:
        self._groups[parent] = group

    @property
    def prerequisites(self) -> set[Student]:
        return self._prerequisites

    def add_prerequisite(self, student: Student) -> None:
        if student == self:
            raise Exception()
        elif student in self.not_alongside:
            raise Exception()
        else:
            self._prerequisites.add(student)

    @property
    def not_alongside(self) -> set[Student]:
        return self._not_alongside

    def add_not_alongside(self, student: Student) -> None:
        if student == self:
            raise Exception()
        elif student in self.prerequisites:
            raise Exception()
        else:
            self._not_alongside.add(student)

    @property
    def attends(self) -> set[Subject | Category]:
        return self._attends

    def add_attends(self, value: Subject | Category) -> None:
        self._attends.add(value)
        self.add_section(value)

    @property
    def taken(self) -> set[Subject | Category]:
        return self._previous.attends

    def add_taken(self, object: Subject | Category) -> None:
        self._previous.add_attends(object)

    @property
    def has_enlisted_level(self, level: int) -> bool:
        for type in self.to_rank:
            for subject in self.rankings.final.all(type):
                if subject.level == level:
                    return True
        return False

    @property
    def has_level(self, level: int) -> bool:
        for object in self.taken:
            if object.level == level:
                return True
        for object in self.attends:
            if object.level == level:
                return True
        return False

    def propose(
        self,
        type:  str,
        index: int = 0
    ) -> None:
        qualified, reason = self.rankings.final.get(type, index).add_student(self)
        if not qualified:
            self.rankings.final.reject(
                self.rankings.final.get(type, index),
                reason
            )
        else:
            self.add_subject(type, self.rankings.final.get(type, index))
            self.add_attends(self.rankings.final.get(type, index))


class Group:
    def __init__(
        self,
        id:       str,
        parent:   Subject | Category,
        students: set[Student]       = set(),
        required: bool               = bool()
    ) -> None:
        self._students = students
        self._required = required

        self.id       = id
        self.parent   = parent
        self.capacity = Capacity(0, 0, self.parent.max_group_members, len(students))
    
    def __repr__(self) -> str:
        return self.id

    @property
    def students(self) -> set[Student]:
        return self._students

    def add_students(self, student: Student) -> bool:
        def ok_groupmates(student: Student):
            for member in self.students:
                if member.shift not in {None, student.shift}:
                    return False
            return True

        if student in self.students:
            return False
        elif self.capacity.available <= 0:
            return False
        elif self.required and not ok_groupmates(student):
            return False
        else:
            self._students.add(student)
            self.capacity.accept(1)
            student.add_group(self.parent, self)


class Subject:
    def __init__(
        self,
        name:              str,
        level:             int                            = None,
        capacity:          Capacity                       = None,
        repeatable:        bool                           = None,
        sections:          set[Section]                   = None,
        prerequisites:     set[tuple[Subject | Category]] = None,
        not_alongside:     set[Subject | Category]        = None,
        max_group_members: int                            = None,
        teaches:           set[int]                       = None
    ) -> None:
        self._name              = name
        self._level             = level

        if repeatable is None:
            self._repeatable = bool()
        else:
            self._repeatable = repeatable

        if sections is None:
            self._sections = set()
        else:
            self._sections = sections

        if prerequisites is None:
            self._prerequisites = set()
        else:
            self._prerequisites = prerequisites

        if not_alongside is None:
            self._not_alongside = set()
        else:
            self._not_alongside = not_alongside

        self._max_group_members = max_group_members

        if teaches is None:
            self._teaches = set()
        else:
            self._teaches = teaches

        if capacity is None:
            self.capacity = Capacity(0, 0, 0)
        else:
            self.capacity = capacity
    
    def __repr__(self) -> str:
        return '{}{}'.format(
            self.name, 
            ''
                if self.level == int()
                else ' Level {}'.format(self.level)
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def level(self) -> int:
        if self._level is None:
            return int()
        else:
            return self._level

    @property
    def repeatable(self) -> bool:
        return self._repeatable

    @property
    def sections(self) -> set[Section]:
        return self._sections

    def add_section(self, section: Section) -> None:
        '''Add a section'''
        if section.parent != self:
            raise Exception()
        else:
            self._sections.add(section)
            self.capacity.increase(section.capacity)

    @property
    def prerequisites(self) -> set[tuple[Subject | Category]]:
        return self._prerequisites

    def add_prerequisites(self, objects: tuple[Subject | Category]) -> None:
        if self in objects:
            raise Exception()
        elif len(set(objects).intersection(self.not_alongside)) > 0:
            raise Exception()
        else:
            self._prerequisites.add(objects)

    @property
    def not_alongside(self) -> set[Subject | Category]:
        return self._not_alongside

    def add_not_alongside(self, object: Subject | Category) -> None:
        if self == object:
            raise Exception()
        else:
            self._not_alongside.add(object)

    def add_student(self, student: Student) -> tuple[bool, str | None]:
        def ok_prerequisites(student: Student) -> bool:
            for prerequisites in self.prerequsites:
                if len(student.taken.intersection(set(prerequisites))) == 0:
                    return False
            return True

        if self.capacity.available <= 0:
            return False, 'Full'
        elif not ok_prerequisites(student):
            return False, 'Prerequisites not met'
        elif len(student.attends.intersection(self.not_alongside)) > 0:
            return False, 'Incompatible with subject'
        else:
            for section in self.sections:
                qualified, reason = section.add_student(student)
                if qualified:
                    self.capacity.accept(1)
                    return True, None
            return False, 'Incompatible with sections'

    @property
    def teaches(self) -> set[int]:
        return self._teaches
    
    def add_teaches(self, grade_level: int) -> None:
        self._teaches.add(grade_level)