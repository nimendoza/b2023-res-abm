from __future__        import annotations
from src.cls.constants import INF


class Capacity:
    def __init__(
        self,
        minimum: int,
        ideal  : int,
        maximum: int,
        filled : int = None
    ) -> None:
        self._minimum = minimum
        self._ideal   = ideal
        self._maximum = maximum
        self._filled  = filled or int()

    def __repr__(self) -> str:
        return f'{self.filled}/{self.maximum}'

    @property
    def minimum(self) -> int:
        return self._minimum

    @minimum.setter
    def minimum(self, value: int) -> None:
        if value < 0:
            raise Exception()
        else:
            self._minimum = value

    @property
    def ideal(self) -> int:
        return self._ideal

    @ideal.setter
    def ideal(self, value: int) -> None:
        if value < 0:
            raise Exception()
        elif value < self.minimum:
            raise Exception()
        else:
            self._ideal = value

    @property
    def maximum(self) -> int:
        return self._maximum

    @maximum.setter
    def maximum(self, value: int) -> None:
        if value < 0:
            raise Exception()
        elif value < self.ideal:
            raise Exception()
        else:
            self._maximum = value

    @property
    def filled(self) -> int:
        return self._filled

    @filled.setter
    def filled(self, value: int) -> int:
        if value > self.maximum:
            raise Exception()
        if value < 0:
            raise Exception()
        else:
            self._filled = value

    @property
    def available(self) -> int:
        return self.maximum - self.filled

    def increase(self, other: Capacity) -> None:
        self.minimum += other.minimum
        self.ideal   += other.ideal
        self.maximum += other.maximum
        self.filled  += other.filled


class Shift:
    def __init__(
        self,
        id        : str      = None,
        partitions: set[str] = None
    ) -> None:
        self._id         = id
        self._partitions = partitions or set()

    def __repr__(self) -> str:
        return self.id

    @property
    def id(self) -> str:
        return self._id

    @property
    def partitions(self) -> set[str]:
        return self._partitions

    def add(self, partition: str) -> None:
        if partition in self.partitions:
            raise Exception()
        else:
            self._partitions.add(partition)


class ParallelSession:
    def __init__(
        self,
        shift    : Shift,
        partition: str,
        name     : str = None,
        index    : int = None
    ) -> None:
        self._name      = name
        self._shift     = shift
        self._partition = partition
        self._index     = index

    def __repr__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return self._name or '{}{}'.format(self.partition, self.index or '')

    @property
    def shift(self) -> Shift:
        return self._shift

    @property
    def partition(self) -> str:
        return self._partition

    @property
    def index(self) -> int | None:
        return self._index


class Rank:
    def __init__(
        self,
        id   : str,
        types: set[str]
    ) -> None:
        self._id      = id
        self._types   = types
        self._ordered = dict((type, list[Subject]()) for type in self.types)
        self._present = dict((type, set[Subject]())  for type in self.types)
        self._reason  = dict((type, list[str]())     for type in self.types)
    
    def __repr__(self) -> str:
        return self.id

    @property
    def id(self) -> str:
        return self._id

    @property
    def types(self) -> set[str]:
        return self._types

    @property
    def ordered(self) -> dict[str, list[Subject]]:
        return self._ordered

    @property
    def present(self) -> dict[str, set[Subject]]:
        return self._present

    @property
    def reason(self) -> dict[str, list[str]]:
        return self._reason

    def all(self, type: str) -> list[Subject]:
        return self.ordered[type]

    def get(
        self,
        type : str,
        index: int = None
    ) -> Subject:
        return self.ordered[type][index or 0]

    def add(
        self,
        type   : str,
        subject: Subject
    ) -> None:
        if subject in self.present[type]:
            raise Exception()
        else:
            self._ordered[type].append(subject)
            self._present[type].add(subject)

    def reject(
        self,
        type  : str,
        reason: str,
        index : int = None
    ) -> None:
        subject = self.get(type, index)
        self._ordered[type].pop(index or 0)
        self._present[type].remove(subject)
        self._reason[type].append(f'{subject}: {reason}')

    def clear(self, type: str = None) -> None:
        if type is None:
            for key in self._ordered:
                self._ordered[key].clear()
                self._present[key].clear()
        else:
            self._ordered[type].clear()
            self._present[type].clear()


class Rankings:
    def __init__(
        self,
        id     : str,
        to_rank: set[str]
    ) -> None:
        self._id      = f'RANKING-{id}'
        self._to_rank = to_rank
        self._initial = Rank(f'{id}I', self.to_rank)
        self._final   = Rank(f'{id}F', self.to_rank)
    
    def __repr__(self) -> str:
        return self.id

    @property
    def id(self) -> str:
        return self._id

    @property
    def to_rank(self) -> set[str]:
        return self._to_rank

    @property
    def initial(self) -> Rank:
        return self._initial

    @property
    def final(self) -> Rank:
        return self._final

    def add(
        self,
        type: str,
        subject: Subject
    ) -> None:
        self.initial.add(type, subject)
        self.final.add(type, subject)


class GradeLevel:
    def __init__(
        self,
        grade_level   : int,
        to_rank       : set[str],
        category_types: set[str],
        subject_types : set[str],
    ) -> None:
        self._grade_level    = grade_level
        self._to_rank        = to_rank
        self._category_types = category_types
        self._subject_types  = subject_types
    
    def __repr__(self) -> str:
        return self.name

    @property
    def grade_level(self) -> int:
        return self._grade_level

    @property
    def to_rank(self) -> set[str]:
        return self._to_rank

    @property
    def category_types(self) -> set[str]:
        return self._category_types

    @property
    def subject_types(self) -> set[str]:
        return self.subject_types

    
class Student:
    def __init__(
        self,
        id           : str,
        grade_level  : GradeLevel,
        shift        : Shift        = None,
        prerequisites: set[Student] = None,
        not_alongside: set[Student] = None,
        previous     : Student      = None
    ) -> None:
        self._id             = id
        self._grade_level    = grade_level
        self._shift          = shift
        self._prerequisites  = prerequisites or set()
        self._not_alongside  = not_alongside or set()
        self._previous       = previous

        self._attends    = set[Subject | Category]()
        self._groups     = dict[Subject | Category, Group]()
        self._sections   = dict[Subject | Category, Section]()
        self._sessions   = dict[str, Section | None]()
        self._rankings   = Rankings(self.id, self.grade_level.to_rank)
        self._categories = dict[str, Category | None](
            (type, None) 
                for type in self.grade_level.categry_types
        )
        self._subjects   = dict[str, Subject | None](
            (type, None)
                for type in self.grade_level.subject_types
        )
    
    def __repr__(self) -> str:
        return self.id

    @property
    def id(self) -> str:
        return self._id

    @property
    def grade_level(self) -> GradeLevel:
        return self._grade_level

    @property
    def shift(self) -> Shift:
        return self._shift

    @property
    def prerequisites(self) -> set[Student]:
        return self._prerequisites

    @property
    def not_alongside(self) -> set[Student]:
        return self._not_alongside

    @property
    def previous(self) -> Student | None:
        return self._previous

    @previous.setter
    def previous(self, student: Student) -> None:
        if student.grade_level.grade_level >= self.grade_level.grade_level:
            raise Exception()
        else:
            self._previous = student

    @property
    def attends(self) -> set[Subject | Category]:
        return self._attends

    @property
    def groups(self) -> dict[Subject | Category, Group]:
        return self._groups

    @property
    def sections(self) -> dict[Subject | Category, Group]:
        return self._sections

    @property
    def sessions(self) -> dict[str, Section | None]:
        return self._sessions

    @property
    def rankings(self) -> Rankings:
        return self._rankings

    @property
    def categories(self) -> dict[str, Category | None]:
        return self._categories

    @property
    def subjects(self) -> dict[str, Subject | None]:
        return self.subjects

    @property
    def taken(self) -> set[Subject | Category] | None:
        if isinstance(self.previous, Student):
            return self.previous.attends

    def add_subject(
        self,
        type   : str,
        subject: Subject
    ) -> None:
        if type not in self.grade_level.category_types:
            raise Exception()
        elif self.subjects[type] is not None:
            raise Exception()
        elif subject.add_student[0]:
            self.subjects[type] = subject
            self.add_section(subject)
            self.attends.add(subject)

    def add_category(
        self,
        type    : str,
        category: Category
    ) -> None:
        if type not in self.grade_level.subject_types:
            raise Exception()
        elif self.categories[type] is not None:
            raise Exception()
        elif category.add_student(self)[0]:
            self.categories[type] = category
            self.add_section(category)
            self.attends.add(category)

    def add_section(
        self,
        parent : Subject | Category,
        section: Section = None
    ) -> None:
        if section is not None:
            if parent not in self.attends:
                raise Exception()
            elif self.shift not in {None, section.shift}:
                raise Exception()
            elif not self.ok_groupmates(section):
                raise Exception()
            elif not self.ok_classmates(section):
                raise Exception()
            elif section.add_student[0]:
                self.sections[parent] = section
                self.sessions[section.parallel_session.partition] = section
        else:
            self.sections[parent] = section

    def add_prerequisite(self, student: Student) -> None:
        if student == self:
            raise Exception()
        elif student in self.not_alongside:
            raise Exception()
        else:
            self.prerequisites.add(student)

    def add_not_alongside(self, student: Student) -> None:
        if student == self:
            raise Exception()
        elif student in self.prerequisites:
            raise Exception()
        else:
            self.not_alongside.add(student)

    def add_group(
        self,
        parent: Subject | Category,
        group : Group
    ) -> None:
        if parent not in self.attends:
            raise Exception()
        elif any(
            groupmate.shift not in {None, self.shift}
                for groupmate in group.students
        ):
            raise Exception()
        else:
            self.groups[parent] = group

    def has_enlisted_level(self, level: int) -> bool:
        for type in self.grade_level.to_rank:
            for subject in self.rankings.final.all(type):
                if subject.level == level:
                    return True
        return False

    def has_level(self, level: int) -> bool:
        for object in self.taken + self.attends:
            if isinstance(object, Subject):
                if object.level == level:
                    return True
        return False

    def propose(
        self,
        type : str,
        index: int = 0
    ) -> None:
        subject           = self.rankings.final.get(type, index)
        qualified, reason = subject.add_student(self)
        if not qualified:
            self.rankings.final.reject(type, reason, index)
        else:
            self.add_subject(type, subject)

    def default_ranking(
        self,
        type    : str,
        subjects: list[Subject]
    ) -> None:
        self.rankings.final.clear(type)
        for subject in subjects:
            self.rankings.final.add(type, subject)

    def ok_groupmates(self, section: Section) -> bool:
        for object, group in self.groups.items():
            if group.required:
                if object == section.parent:
                    for groupmate in group.students:
                        if groupmate.sections[object] not in {None, section}:
                            return False
                else:
                    return False
                if any(
                    groupmate.shift not in {None, section.shift}
                        for groupmate in group.students
                ):
                    return False
        return True

    def ok_classmates(self, object: Section | Group) -> bool:
        if not object.students.issuperset(self.prerequisites):
            return False
        elif object.students.intersection(self.not_alongside):
            return False
        else:
            return True


class Group:
    def __init__(
        self,
        id      : str,
        parent  : Subject | Category,
        required: bool         = None,
        students: set[Student] = None
    ) -> None:
        self._id       = id
        self._parent   = parent
        self._required = required or bool()
        self._students = students or set()

        self._capacity = Capacity(0, 0, self.parent.max_group_members, len(self.students))
    
    def __repr__(self) -> str:
        return self.id

    @property
    def id(self) -> str:
        return self._id

    @property
    def parent(self) -> Subject | Category:
        return self._parent

    @property
    def required(self) -> bool:
        return self._required

    @property
    def students(self) -> set[Student]:
        return self._students

    @property
    def capacity(self) -> Capacity:
        return self._capacity

    def add_student(self, student: Student) -> None:
        if student in self.students:
            raise Exception()
        elif self.capacity.available <= 0:
            raise Exception()
        elif not student.ok_classmates(self):
            raise Exception()
        else:
            self.students.add(student)
            self.capacity.filled += 1
            
            student.add_group(self.parent, self)


class Section:
    def __init__(
        self,
        parent          : Subject | Category,
        shift           : Shift,
        parallel_session: ParallelSession,
        capacity        : Capacity,
        name            : str          = None,
        students        : set[Student] = None
    ) -> None:
        self._name             = name
        self._parent           = parent
        self._shift            = shift
        self._parallel_session = parallel_session
        self._capacity         = capacity
        self._students         = students
    
    def __repr__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        if self._name is None:
            return f'{self.parent} {self.parallel_session}'
        else:
            return self._name

    @property
    def parent(self) -> Subject | Category:
        return self._parent

    @property
    def shift(self) -> Shift:
        return self._shift

    @property
    def parallel_session(self) -> ParallelSession:
        return self._parallel_session

    @property
    def capacity(self) -> Capacity:
        return self._capacity

    @property
    def students(self) -> set[Student]:
        return self._students

    def add_student(self, student: Student) -> tuple[bool, str | None]:
        if self.capacity.available <= 0:
            return False, 'Full'
        elif student.shift not in {None, self.shift}:
            return False, 'Incompatible shift'
        elif student.sessions[self.parallel_session.partition] is not None:
            return False, 'Already attending a parallel session'
        elif not student.ok_classmates(self):
            return False, 'Incompatible classmate/s'
        elif not student.ok_groupmates(self):
            return False, 'Incompatible with groupmate/s'
        else:
            self.students.add(student)
            self.capacity += 1
            try:
                student.add_section(self.parent, self)
                return True, None
            except Exception:
                ...


class Category:
    def __init__(
        self,
        name             : str,
        type             : str,
        capacity         : Capacity                = None,
        sections         : set[Section]            = None,
        prerequisites    : set[Subject | Category] = None,
        not_alongside    : set[Subject | Category] = None,
        max_group_members: int                     = None,
        students         : set[Student]            = None
    ) -> None:
        self._name              = name
        self._type              = type
        self._capacity          = capacity or Capacity(0, 0, INF, 0)
        self._sections          = sections
        self._prerequisites     = prerequisites or set()
        self._not_alongside     = not_alongside or set()
        self._max_group_members = max_group_members or int()
        self._students          = students or set()
    
    def __repr__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._type

    @property
    def capacity(self) -> Capacity:
        return self._capacity

    @property
    def sections(self) -> set[Section]:
        return self._sections

    @property
    def prerequisites(self) -> set[Subject | Category]:
        return self._prerequisites

    @property
    def not_alongside(self) -> set[Subject | Category]:
        return self._not_alongside

    @property
    def max_group_members(self) -> int:
        return self._max_group_members

    @property
    def students(self) -> set[Student]:
        return self._students

    def add_section(self, section: Section) -> None:
        if section.parent != self:
            raise Exception()
        if section in self.sections:
            raise Exception()
        else:
            self.sections.add(section)
            self.capacity.increase(section.capacity)

    def add_prerequisites(self, objects: tuple[Subject | Category]) -> None:
        if self in objects:
            raise Exception()
        elif set(objects).intersection(self.not_alongside):
            raise Exception()
        else:
            self.prerequisites.add(objects)

    def add_not_alongside(self, object: Subject | Category) -> None:
        if self == object:
            raise Exception()
        else:
            self.not_alongside.add(object)

    def add_student(self, student: Student) -> tuple[bool, str | None]:
        if self.capacity.available <= 0:
            return False, 'Full'
        elif not self.ok_student(student):
            return False, 'Incompatible with category'
        elif self.sections:
            for section in self.sections:
                qualified, reason = section.add_student(student)
                if qualified:
                    self.students.add(student)
                    self.capacity.filled += 1
                    try:
                        student.add_category(self.type, self)
                        return True, None
                    except Exception:
                        ...
            return False, 'Incompatible with sections'
        else:
            self.students.add(student)
            self.capacity.filled += 1
            try:
                student.add_category(self.type, self)
                return True, None
            except Exception:
                ...

    def ok_student(self, student: Student) -> bool:
        for prerequisites in self.prerequisites:
            if not student.taken.intersection(set(prerequisites)):
                return False
        return len(student.attends.intersection(self.not_alongside)) > 0


class Subject(Category):
    def __init__(
        self,
        name             : str,
        type             : str,
        level            : int                     = None,
        repeatable       : bool                    = None,
        capacity         : Capacity                = None,
        sections         : set[Section]            = None,
        prerequisites    : set[Subject | Category] = None,
        not_alongside    : set[Subject | Category] = None,
        max_group_members: int                     = None,
        teaches          : set[GradeLevel]         = None,
        students         : set[Student]            = None
    ) -> None:
        super(Subject, self).__init__(
            name,
            type,
            capacity,
            sections,
            prerequisites,
            not_alongside,
            max_group_members,
            students
        )

        self._level = level
        self._repeatable = repeatable or bool()
        self._teaches = teaches or set()
    
    def __repr__(self) -> str:
        return '{}{}'.format(
            self.name,
            f' Level{self.level}'
                if self.level
                else ''
        )

    @property
    def level(self) -> int | None:
        return self._level

    @property
    def repeatable(self) -> bool:
        return self._repeatable

    @property
    def teaches(self) -> set[GradeLevel]:
        return self._teaches

    def add_student(self, student: Student) -> tuple[bool, str | None]:
        if self.capacity.available <= 0:
            return False, 'Full'
        elif student.grade_level not in self.teaches:
            return False, 'Grade level incompatible'
        elif not self.ok_student(student):
            return False, 'Incompatible with subject'
        else:
            for section in self.sections:
                qualified, reason = section.add_student(student)
                if qualified:
                    self.students.add(student)
                    self.capacity.filled += 1
                    try:
                        student.add_subject(self.type, self)
                        return True, None
                    except Exception:
                        ...
            return False, 'Incompatible with sections'

    def add_taught(self, grade_level: GradeLevel) -> None:
        self.teaches.add(grade_level)