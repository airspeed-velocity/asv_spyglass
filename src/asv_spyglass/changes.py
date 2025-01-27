import enum
from dataclasses import dataclass


class ResultColor(enum.StrEnum):
    DEFAULT = "black"
    GREEN = enum.auto()
    RED = enum.auto()
    LIGHTGREY = enum.auto()


class ResultMark(enum.StrEnum):
    BETTER = "-"
    WORSE = "+"
    FAILURE = "!"
    FIXED = "*"
    INCOMPARABLE = "x"
    UNCHANGED = " "
    INSIGNIFICANT = "~"


class AfterIs(enum.Enum):
    LUKEWARM = 0
    WORSE = -1
    BETTER = 1


@dataclass
class ASVChangeInfo:
    mark: ResultMark
    color: ResultColor
    description: str
    state: AfterIs
    before: str
    after: str


@dataclass
class Incomparable(ASVChangeInfo):
    mark: ResultMark = ResultMark.INCOMPARABLE
    color: ResultColor = ResultColor.LIGHTGREY
    description: str = "Not comparable"
    state: AfterIs = AfterIs.LUKEWARM
    before: str = ""
    after: str = ""


@dataclass
class Failure(ASVChangeInfo):
    mark: ResultMark = ResultMark.FAILURE
    color: ResultColor = ResultColor.RED
    description: str = "Introduced a failure"
    state: AfterIs = AfterIs.WORSE
    before: str = "Succeeded"
    after: str = "Failed"


@dataclass
class Fixed(ASVChangeInfo):
    mark: ResultMark = ResultMark.FIXED
    color: ResultColor = ResultColor.GREEN
    description: str = "Fixed a failure"
    state: AfterIs = AfterIs.BETTER
    before: str = "Failed"
    after: str = "Succeeded"


@dataclass
class NoChange(ASVChangeInfo):
    mark: ResultMark = ResultMark.UNCHANGED
    color: ResultColor = ResultColor.DEFAULT
    description: str = "Both failed or either was skipped or no significant change"
    state: AfterIs = AfterIs.LUKEWARM
    before: str = ""
    after: str = ""


@dataclass
class Better(ASVChangeInfo):
    mark: ResultMark = ResultMark.BETTER
    color: ResultColor = ResultColor.GREEN
    description: str = "Relative improvement"
    state: AfterIs = AfterIs.BETTER
    before: str = "Worse"
    after: str = "Better"


@dataclass
class Worse(ASVChangeInfo):
    mark: ResultMark = ResultMark.WORSE
    color: ResultColor = ResultColor.RED
    description: str = "Relatively worse"
    state: AfterIs = AfterIs.WORSE
    before: str = "Better"
    after: str = "Worse"
