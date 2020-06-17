import abc
from typing import Type, Dict, Sequence

acceptable_others: Dict[Type, Sequence[Type]] = {}


class StrContainer(abc.ABC):
    raw: str

    def __init__(self, ss: str):
        self.raw = ss

    def __str__(self):
        return self.raw


# You can subclass StrContainer or str, like so::
#
#   class SpecialStr(StrContainer, abc.ABC):
#       ...
#
# or::
#
#   class SpecialStr(str, abc.ABC):
#       ...
#
# One allows more strict type checking, the other allows you to use SpecialStr just
# like a normal string.
#
class SpecialStr(StrContainer, abc.ABC):
    def acceptable(self, other) -> bool:
        return isinstance(other, (self.__class__, *acceptable_others.get(self.__class__, ())))

    def __add__(self, other):
        if self.acceptable(other):
            return self.__class__(str(self) + str(other))
        elif type(other) == str:
            return str(self) + other
        else:
            return NotImplemented

    def __radd__(self, other):
        if self.acceptable(other):
            return self.__class__(str(other) + str(self))
        elif type(other) == str:
            return other + str(self)
        else:
            return NotImplemented
