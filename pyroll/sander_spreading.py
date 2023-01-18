import numpy as np

from pyroll.core import RollPass, root_hooks, Unit
from pyroll.core.hooks import Hook

VERSION = "2.0.0b"

RollPass.sander_temperature_coefficient = Hook[float]()
RollPass.sander_velocity_coefficient = Hook[float]()
RollPass.sander_material_coefficient = Hook[float]()
RollPass.sander_friction_coefficient = Hook[float]()
RollPass.sander_exponent = Hook[float]()


@RollPass.sander_temperature_coefficient
def sander_temperature_coefficient(self: RollPass):
    if self.in_profile.temperature >= (950 + 273.15):
        return 1
    else:
        return 1.005


@RollPass.sander_velocity_coefficient
def sander_velocity_coefficient(self: RollPass):
    if self.velocity <= 60:
        return 1 - 0.0033 * self.velocity * (
                1 - 1 / (self.out_profile.equivalent_width / self.in_profile.equivalent_width))
    else:
        return 1


@RollPass.sander_material_coefficient
def sander_material_coefficient(self: RollPass):
    return 1


@RollPass.sander_friction_coefficient
def sander_friction_coefficient(self: RollPass):
    return 1


@RollPass.sander_exponent
def sander_exponent(self: RollPass):
    equivalent_height_change = self.in_profile.equivalent_height - self.out_profile.equivalent_height

    return 10 ** (
            -0.76 * (self.in_profile.equivalent_width / self.in_profile.equivalent_height) ** 0.39 * (
            self.in_profile.equivalent_width / np.sqrt(self.roll.working_radius * equivalent_height_change)) ** 0.12 * (
                    self.in_profile.equivalent_width / self.roll.working_radius) ** 0.59
    )


@RollPass.OutProfile.width
def width(self: RollPass.OutProfile):
    roll_pass = self.roll_pass()

    if not self.has_set_or_cached("width"):
        self.width = roll_pass.roll.groove.usable_width

    spread = (
            roll_pass.sander_temperature_coefficient
            * roll_pass.sander_velocity_coefficient
            * roll_pass.sander_material_coefficient
            * roll_pass.sander_friction_coefficient
            * roll_pass.draught ** (-roll_pass.sander_exponent)
    )

    return spread * roll_pass.in_profile.width


root_hooks.add(Unit.OutProfile.width)
