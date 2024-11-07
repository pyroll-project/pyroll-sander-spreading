import numpy as np

from pyroll.core import SymmetricRollPass, root_hooks, Unit
from pyroll.core.hooks import Hook

VERSION = "3.0.0"

SymmetricRollPass.sander_temperature_coefficient = Hook[float]()
"""Temperature correction factor a for Sander's spread equation."""

SymmetricRollPass.sander_velocity_coefficient = Hook[float]()
"""Velocity correction factor c for Sander's spread equation."""

SymmetricRollPass.sander_material_coefficient = Hook[float]()
"""Material correction factor d for Sander's spread equation."""

SymmetricRollPass.sander_friction_coefficient = Hook[float]()
"""Friction correction factor f for Sander's spread equation."""

SymmetricRollPass.sander_exponent = Hook[float]()
"""Exponent w for for Sander's spread equation."""

root_hooks.add(Unit.OutProfile.width)


@SymmetricRollPass.sander_temperature_coefficient
def sander_temperature_coefficient(self: SymmetricRollPass):
    if self.in_profile.temperature >= (950 + 273.15):
        return 1
    else:
        return 1.005


@SymmetricRollPass.sander_velocity_coefficient
def sander_velocity_coefficient(self: SymmetricRollPass):
    if self.velocity <= 60:
        return 1 - 0.0033 * self.velocity * (
                1 - 1 / (self.out_profile.equivalent_width / self.in_profile.equivalent_width))
    else:
        return 1


@SymmetricRollPass.sander_material_coefficient
def sander_material_coefficient(self: SymmetricRollPass):
    return 1


@SymmetricRollPass.sander_friction_coefficient
def sander_friction_coefficient(self: SymmetricRollPass):
    return 1


@SymmetricRollPass.sander_exponent
def sander_exponent(self: SymmetricRollPass):
    equivalent_height_change = self.in_profile.equivalent_height - self.out_profile.equivalent_height

    return 10 ** (
            -0.76 * (self.in_profile.equivalent_width / self.in_profile.equivalent_height) ** 0.39 * (
            self.in_profile.equivalent_width / np.sqrt(self.roll.working_radius * equivalent_height_change)) ** 0.12 * (
                    self.in_profile.equivalent_width / self.roll.working_radius) ** 0.59
    )


@SymmetricRollPass.OutProfile.width
def width(self: SymmetricRollPass.OutProfile):
    rp = self.roll_pass

    if not self.has_set_or_cached("width"):
        return None

    return (
            rp.sander_temperature_coefficient
            * rp.sander_velocity_coefficient
            * rp.sander_material_coefficient
            * rp.sander_friction_coefficient
            * rp.draught ** (-rp.sander_exponent)
    ) * rp.in_profile.width
