import enum
from dataclasses import dataclass

from asv_spyglass._num import BenchNum


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


@dataclass
class ASVChange:
    mark: ResultMark
    color: ResultColor
    description: str
    before: BenchNum
    after: BenchNum
    machine: str
    envname: str


@dataclass
class Incomparable(ASVChange):
    mark: ResultMark = ResultMark.INCOMPARABLE
    color: ResultColor = ResultColor.LIGHTGREY
    description: str = "Not comparable"
    after: str = ""
    before: str = ""


@dataclass
class Failure(ASVChange):
    mark: ResultMark = ResultMark.FAILURE
    color: ResultColor = ResultColor.RED
    description: str = "Introduced a failure"
    after: str = "Failed"
    before: str = "Succeeded"


@dataclass
class Fixed(ASVChange):
    mark: ResultMark = ResultMark.FIXED
    color: ResultColor = ResultColor.GREEN
    description: str = "Fixed a failure"
    after: str = "Succeeded"
    before: str = "Failed"


@dataclass
class NoChange(ASVChange):
    mark: ResultMark = ResultMark.UNCHANGED
    color: ResultColor = ResultColor.DEFAULT
    description: str = "Both failed or either was skipped or no significant change"
    after: str = ""
    before: str = ""


@dataclass
class Insignificant(NoChange):
    mark: ResultMark = ResultMark.INSIGNIFICANT
    color: ResultColor = ResultColor.DEFAULT
    description: str = "Statistically insignificant change"
    after: str = ""
    before: str = ""


@dataclass
class Better(ASVChange):
    mark: ResultMark = ResultMark.BETTER
    color: ResultColor = ResultColor.GREEN
    description: str = "Relative improvement"
    after: str = "Better"
    before: str = "Worse"


@dataclass
class Worsened(ASVChange):
    mark: ResultMark = ResultMark.WORSE
    color: ResultColor = ResultColor.RED
    description: str = "Relatively worse"
    after: str = "Worse"
    before: str = "Better"
