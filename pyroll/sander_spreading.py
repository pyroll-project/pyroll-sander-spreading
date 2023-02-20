import numpy as np

from pyroll.core import RollPass, ThreeRollPass, root_hooks, Unit
from pyroll.core.hooks import Hook

VERSION = "2.0.0"

RollPass.sander_temperature_coefficient = Hook[float]()
"""Temperature correction factor a for Sander's spread equation."""

RollPass.sander_velocity_coefficient = Hook[float]()
"""Velocity correction factor c for Sander's spread equation."""

RollPass.sander_material_coefficient = Hook[float]()
"""Material correction factor d for Sander's spread equation."""

RollPass.sander_friction_coefficient = Hook[float]()
"""Friction correction factor f for Sander's spread equation."""

RollPass.sander_exponent = Hook[float]()
"""Exponent w for for Sander's spread equation."""

root_hooks.add(Unit.OutProfile.width)


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


@RollPass.spread
def spread(self: RollPass):
    return (
            self.sander_temperature_coefficient
            * self.sander_velocity_coefficient
            * self.sander_material_coefficient
            * self.sander_friction_coefficient
            * self.draught ** (-self.sander_exponent)
    )


@RollPass.OutProfile.width
def width(self: RollPass.OutProfile):
    rp = self.roll_pass

    if not self.has_set_or_cached("width"):
        return None

    return rp.spread * rp.in_profile.width


@ThreeRollPass.OutProfile.width
def width(self: RollPass.OutProfile):
    rp = self.roll_pass

    if not self.has_set_or_cached("width"):
        return None

    return rp.spread * rp.in_profile.width
