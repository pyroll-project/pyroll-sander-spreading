import numpy as np
from pyroll.core import RollPass


@RollPass.hookimpl
def sander_exponent(roll_pass: RollPass):
    in_equivalent_height = roll_pass.in_profile.equivalent_rectangle.height
    in_equivalent_width = roll_pass.in_profile.equivalent_rectangle.width
    equivalent_height_change = roll_pass.in_profile.equivalent_rectangle.height - roll_pass.out_profile.equivalent_rectangle.height

    return 10 ** (
            -0.76 * (in_equivalent_width / in_equivalent_height) ** 0.39 * (
                in_equivalent_width / np.sqrt(roll_pass.roll.working_radius * equivalent_height_change)) ** 0.12 * (
                    in_equivalent_width / roll_pass.roll.working_radius) ** 0.59
    )


@RollPass.hookimpl
def spread(roll_pass: RollPass):
    compression = (roll_pass.in_profile.equivalent_rectangle.height
                   / roll_pass.out_profile.equivalent_rectangle.height)

    spread = (compression ** roll_pass.sander_exponent)

    return spread
