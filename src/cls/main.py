from __future__ import annotations

#  GLOBALS
INF = int(1e9)
#  -------


class Subject:
    def __init__(
        self,
        name:              str,
        level:             int,
        capacity:          Capacity,
        repeatable:        bool                = bool(),
        sections:          set[Section]        = set(),
        prerequisites:     set[tuple[Subject]] = set(),
        not_alongside:     set[Subject]        = set(),
        max_group_members: int                 = int()
    ) -> None:
        self.name              = name
        self.level             = level
        self.capacity          = capacity
        self.sections          = sections
        self.repeatable        = repeatable
        self.prerequisites     = prerequisites
        self.not_alongside     = not_alongside
        self.max_group_members = max_group_members
    
    def __repr__(self) -> str:
        return '{}{}'.format(
            self.name,
            ' Level {}'.format(self.level)
                if self.level != int()
                else ''
        )

    def add_prerequisite(self, subjects: tuple[Subject]) -> None:
        if self not in subjects:
            self.prerequisites.add(subjects)
        else:
            raise NotImplementedError()

    def add_not_alongside(self, subject: Subject) -> None:
        if subject != self:
            self.not_alongside.add(subject)
        else:
            raise NotImplementedError()

    def add_section(self, section: Section) -> None:
        if section.subject == self:
            self.sections.add(section)
            self.capacity.add(section.capacity)
        else:
            raise NotImplementedError()

    def inspect_student(self, student: Student) -> tuple[bool, list[str], Section | None]:
        ok_capacity      = [
            self.capacity.filled < self.capacity.maximum,
            '{} has full capacity'.format(self)
        ]
        taken_before     = [
            self in student.taken() and not self.repeatable,
            '{} has taken {} before'.format(student, self)
        ]
        ok_prerequisites = [
            all(
                len(set(subjects).intersection(student.taken())) > 0
                    for subjects in self.prerequisites
            ),
            '{} did not meet prerequisites of {}'.format(student, self)
        ]
        ok_not_alongside = [
            all(
                subject not in student.takes()
                    for subject in self.not_alongside
            ),
            '{} is taking a subject not alongside for {}'.format(student, self)
        ]

        qualifications      = [
            ok_capacity,
            taken_before,
            ok_prerequisites,
            ok_not_alongside
        ]
        initially_qualified = all(
            qualification[0]
                for qualification in qualifications
        )
        reasons             = list(
            qualification[1]
                for qualification in qualifications
                    if qualification[0] is True
        )

        section_qualified = list[bool]()
        official_sections = list()
        if initially_qualified:
            for section in self.sections:
                qualified, section_reasons = section.inspect_student(student)
                section_qualified.append(qualified)
                if not qualified:
                    for reason in section_reasons:
                        reasons.append('{}: {}'.format(section, reason))
                else:
                    official_sections.append(section)
        official_sections.sort(
            key=lambda x: x.capacity.maximum - x.capacity.filled,
            reverse=True
        )
        
        section_qualified = any(section_qualified)
        if not section_qualified:
                reasons.append('No section/s of {} can allot'.format(self))
        return initially_qualified and section_qualified, reasons, official_sections[0]

    def add_student(self, student: Student) -> tuple[bool, list[str]]:
        qualified, reasons, section = self.inspect_student(student)
        if qualified:
            self.capacity.filled += 1
            section.add_student(student)
            
            student.add_subject(self)
            student.add_section(section)
        return qualified, reasons


class Capacity:
    def __init__(
        self,
        minimum: int,
        ideal:   int,
        maximum: int,
        filled:  int = int()
    ) -> None:
        self.minimum = minimum
        self.ideal   = ideal
        self.maximum = maximum
        self.filled  = filled
    
    def __repr__(self) -> str:
        return '{}/{}'.format(
            self.filled,
            self.maximum
        )


class Section:
    def __init__(
        self,
        shift:            Shift,
        parallel_session: ParallelSession,
        capacity:         Capacity,
        subject:          Subject,
        students:         set[Student]     = set()
    ) -> None:
        self.shift = shift

        self.parallel_session = parallel_session
        assert self.shift == self.parallel_session.shift

        self.capacity = capacity
        self.subject  = subject
        self.students = students

    def __repr__(self) -> str:
        return '{} {}'.format(
            self.subject,
            self.parallel_session
        )

    def inspect_student(self, student: Student) -> tuple[bool, list[str]]:
        has_slots     = [
            self.capacity.filled < self.capacity.maximum,
            '{} has no more slots available'.format(self)
        ]
        ok_shift      = [
            student.shift in {None, self.shift},
            '{} is not in the same shift as {}'.format(student, self)
        ]
        not_attending = [
            any(
                self.parallel_session not in student.attending,
                student.attending[self.parallel_session] is None
            ),
            '{} is already attending a/an {} session'.format(student, self.parallel_session)
        ]
        ok_classmates = [
            all(
                len(self.students.intersection(student.not_alongside)) == 0,
                self.students.issuperset(student.prerequisites)
            ),
            '{} classmates are inappropriate for {}'.format(self, student)
        ]
        ok_groupmates = [
            all(
                any(
                    groupmate in self.students or groupmate.section[self.subject.type] is None
                        for groupmate in group
                )
                    for group in student.groups
            ),
            '{} does not have the same section as their groupmates'.format(student)
        ]

        qualifications = [
            has_slots,
            ok_shift,
            not_attending,
            ok_classmates,
            ok_groupmates
        ]
        reasons        = list[str](
            item[1]
                for item in qualifications
                    if item[0] is True
        )
        qualified      = all(item[0] for item in qualifications)
        return qualified, reasons


class Student:
    def __init__(
        self,
        id:            str,
        level:         int,
        shift:         Shift,
        to_rank:       list[str],
        subjects:      dict[str, Subject | None] = dict(),
        sections:      dict[str, Section | None] = dict(),
        categories:    set[Category]             = set(),
        groups:        set[Group]                = set(),
        prerequisites: set[Student]              = set(),
        not_alongside: set[Student]              = set()
    ) -> None:
        self.id            = id
        self.level         = level
        self.shift         = shift
        self.to_rank       = to_rank
        self.irank         = Rank('{}I'.format(self.id), self.to_rank)
        self.frank         = Rank('{}F'.format(self.id), self.to_rank)
        self.subjects      = subjects
        self.sections      = sections
        self.categories    = categories
        self.groups        = groups
        self.prerequisites = prerequisites
        self.not_alongside = not_alongside
    
    def __repr__(self) -> str:
        return self.id

    def taken(self) -> set[Subject]:
        return set()

    def takes(self) -> set[Subject]:
        takes = set(
            subject
                for subject in self.subjects.values()
                    if isinstance(subject, Subject)
        )
        return takes

    def has_enlisted_level(self, level: int) -> bool:
        for type in self.to_rank:
            for subject in self.irank[type]:
                if subject.level == level:
                    return True
        return False

    def has_level(self, level: int) -> bool:
        for subject in self.taken():
            if subject.level == level:
                return True
        for subject in self.subjects.values():
            if isinstance(subject, Subject):
                if subject.level == level:
                    return True
        return False


class Shift:
    def __init__(
        self,
        partitions: set[str] = set()
    ) -> None:
        self.partitions = partitions
    
    def __repr__(self) -> str:
        return ''.join(sorted(self.partitions))

    def add_partition(self, partition: str) -> None:
        self.partitions.add(partition)


class ParallelSession:
    def __init__(
        self,
        shift: Shift,
        partition: str,
        index: int = int()
    ) -> None:
        self.shift = shift

        self.partition = partition
        assert self.partition in self.shift.partitions

        self.index = index
    
    def __repr__(self) -> str:
        return '{}{}'.format(
            self.partition,
            self.index
                if self.index != int()
                else ''
        )


class Group:
    def __init__(
        self,
        id:       str,
        parent:   Subject | Category,
        students: set[Student]       = set(),
        required: bool               = bool()
    ) -> None:
        self.id       = id
        self.parent   = parent
        self.students = students
        self.required = required
        '''Whether the students in this group must have the same shift'''
    
    def __repr__(self) -> str:
        return self.id
    
    def add_student(self, student: Student) -> bool:
        '''Adds a student. Returns whether the attempt is successful'''
        if student not in self.students:
            if self.parent.max_group_members > len(self.students):
                if self.required:
                    for member in self.students:
                        if member.shift != student.shift:
                            return False
                self.students.add(student)
                student.groups.add(self)
                return True
        return False


class Rank:
    def __init__(
        self,
        id:    str,
        types: list[str]
    ) -> None:
        self.id    = 'RANK-{}'.format(id)
        self.types = set(types)
        '''Categories to rank'''
        self.lst = dict(
            (type, list[Subject]())
                for type in self.types
        )
        '''Ranked subject preferences'''
        self.set = dict(
            (type, set[Subject]())
                for type in self.types
        )
        self.rsn = dict(
            (type, list[str]())
                for type in types
        )
        '''Reason for not being accepted to a ranked subject'''
    
    def __repr__(self) -> str:
        return self.id

    def add(
        self,
        type:    str,
        subject: Subject
    ) -> None:
        '''Add a subject to the backmost of the ranking of a category'''
        if subject not in self.set[type]:
            self.lst[type].append(subject)
            self.set[type].add(subject)

    def get(
        self,
        type: str,
        index: int
    ) -> Subject:
        return self.lst[type][index]

    def reject(
        self,
        type:    str,
        subject: Subject,
        reasons: list[str] = list()
    ) -> None:
        self.lst[type].remove(subject)
        self.set[type].remove(subject)
        self.rsn[type].extend(reasons)

    def clear(self, type: str) -> None:
        self.lst[type].clear()
        self.set[type].clear()


class Category:
    def __init__(
        self,
        name:              str,
        capacity:          Capacity                       = Capacity(0, INF, INF, 0),
        max_group_members: int                            = int(),
        students:          set[Student]                   = set()
    ) -> None:
        self.name              = name
        self.capacity          = capacity
        self.max_group_members = max_group_members
        self.students          = students
    
    def __repr__(self) -> str:
        return self.name

    def inspect_student(self, student: Student) -> tuple[bool, list[str]]:
        ok_capacity = [
            self.capacity.filled < self.capacity.maximum,
            '{} does not meet requirements for {}'.format(student, self)
        ]

        qualifications = [
            ok_capacity
        ]
        reasons        = [
            item[1]
                for item in qualifications
                    if item[0] is True
        ]
        qualified      = all(
            item[0]
                for item in qualifications
        )
        return qualified, reasons

    def add_student(self, student: Student) -> tuple[bool, list[str]]:
        qualified, reasons = self.inspect_student(student)
        if qualified:
            self.students.add(student)
            self.capacity.filled += 1
        return qualified, reasons