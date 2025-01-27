import math
from dataclasses import dataclass


@dataclass
class BenchNum:
    val: float
    err: float | None
    unit: str | None


class Ratio:
    """
    Represents the ratio between two numeric values (t2 / t1), handling
    potential issues like division by zero, NaN, and None values. It also
    supports marking a ratio as insignificant.

    Attributes:
        _t1 (float | None): The first value (denominator).
        _t2 (float | None): The second value (numerator).
        val (float): The calculated ratio, which can be:
            - The actual ratio if both _t1 and _t2 are valid numbers and _t1 is not zero.
            - math.inf if either _t1 or _t2 is None or NaN, or if _t1 is zero.
        is_insignificant (bool): A flag indicating whether the ratio should be
            considered statistically insignificant. Defaults to False.

    Methods:
        __init__(self, t1: float | None, t2: float | None):
            Initializes a Ratio object, calculating the ratio if possible.

        __repr__(self):
            Returns a string representation of the ratio:
            - "n/a" if the ratio is undefined (val is math.inf).
            - "~" followed by the formatted ratio if is_insignificant is True.
            - A formatted string with 2 decimal places otherwise.

        _is_invalid(self, t1, t2):
            A private helper method to check if the inputs are invalid for ratio calculation.
    """

    def __init__(self, t1: float | None, t2: float | None):
        """
        Initializes a Ratio object.

        Args:
            t1 (float | None): The first value (denominator).
            t2 (float | None): The second value (numerator).
        """
        self._t1 = t1
        self._t2 = t2
        self.is_insignificant = False
        self.val = None

        if self._is_invalid(t1, t2):
            self.val = math.inf
        else:
            try:
                self.val = t2 / t1
            except ZeroDivisionError:
                self.val = math.inf

    def __repr__(self):
        """
        Returns a string representation of the ratio.

        If val is math.inf, returns "n/a".
        If is_insignificant is True, returns "~" followed by the formatted ratio.
        Otherwise, returns the ratio formatted to 2 decimal places.
        """
        if self.val == math.inf:
            return "n/a"
        elif self.is_insignificant:
            return "~" + f"{self.val:6.2f}".strip()
        else:
            return f"{self.val:6.2f}"

    def _is_invalid(self, t1, t2):
        """
        Checks if the inputs are invalid for ratio calculation.

        Args:
            t1 (float | None): The first value.
            t2 (float | None): The second value.

        Returns:
            bool: True if either t1 or t2 is None or NaN, False otherwise.
        """
        return t1 is None or t2 is None or math.isnan(t1) or math.isnan(t2)
