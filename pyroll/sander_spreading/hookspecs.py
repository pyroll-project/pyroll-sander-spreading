from pyroll.core import RollPass


@RollPass.hookspec
def sander_exponent(roll_pass: RollPass):
    """Gets the Sander spreading model exponent w."""
