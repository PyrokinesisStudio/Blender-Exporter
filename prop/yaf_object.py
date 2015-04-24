# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
from bpy.props import (FloatVectorProperty,
                       FloatProperty,
                       IntProperty,
                       BoolProperty,
                       EnumProperty,
                       StringProperty,
                       PointerProperty)

#
enum_volume_types=(
    ('ExpDensity Volume', "ExpDensity Volume", ""),
    ('Noise Volume', "Noise Volume", ""),
    ('Uniform Volume', "Uniform Volume", ""),
)

enum_geometry_types=(
    ('geometry', "Mesh Object", ""),
    ('mesh_light', "Mesh Light Object", ""),
    ('portal_light', "Portal Light Object", ""),
    ('volume_region', "Volume Region Object", "")
)


class TheBountyObjectSettings(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Object.bounty = PointerProperty(
            name="",
            description="Objects settings",
            type=cls,
        )
        cls.geometry_type = EnumProperty(
            name="Geometry types",
            description="Set the type of geometry object(simple mesh by default)",
            items= enum_geometry_types,
            default='geometry'
        )
        cls.ml_color = FloatVectorProperty(
            name="Meshlight color",
            description="Meshlight color",
            subtype='COLOR',
            step=1, precision=2,
            min=0.0, max=1.0,
            soft_min=0.0, soft_max=1.0,
            default=(0.8, 0.8, 0.8)
        )    
        cls.ml_power = FloatProperty(
            name="Power",
            description="Intensity multiplier for color",
            min=0.0, max=10000.0,
            default=1.0
        )    
        cls.ml_samples = IntProperty(
            name="Samples",
            description="Number of samples to be taken for direct lighting",
            min=0, max=512,
            default=16
        )    
        cls.ml_double_sided = BoolProperty(
            name="Double sided",
            description="Emit light at both sides of every face",
            default=False
        )
        #------------------
        # portal light
        #------------------    
        cls.bgp_power = FloatProperty(
            name="Power",
            description="Intensity multiplier for color",
            min=0.0, max=10000.0,
            default=1.0
        )    
        cls.bgp_samples = IntProperty(
            name="Samples",
            description="Number of samples to be taken for the light",
            min=0, max=512,
            default=16
        )    
        cls.bgp_with_caustic = BoolProperty(
            name="Caustic photons",
            description="Allow BG Portal Light to shoot caustic photons",
            default=True
        )    
        cls.bgp_with_diffuse = BoolProperty(
            name="Diffuse photons",
            description="Allow BG Portal Light to shoot diffuse photons",
           default=True
        )    
        cls.bgp_photon_only = BoolProperty(
            name="Photons only",
            description="Set BG Portal Light in photon only mode (no direct light contribution)",
            default=False
        )
        #--------------------
        # volume object
        #--------------------    
        cls.vol_region = EnumProperty(
            name="Volume region",
            description="Set the volume region",
            items= enum_volume_types,
            default='ExpDensity Volume'
        )    
        cls.vol_height = FloatProperty(
            name="Height",
            description="Controls the density of the volume before it starts to fall off",
            min=0.0, max=1000.0,
            default=1.0
        )    
        cls.vol_steepness = FloatProperty(
            name="Steepness",
            description="Controls how quickly the density falls off",
            min=0.0, max=10.0,
            precision=3,
            default=1.000
        )    
        cls.vol_sharpness = FloatProperty(
            name="Sharpness",
            description="Controls how sharp a NoiseVolume looks at the border between areas of high and low density",
            min=1.0, max=100.0,
            precision=3,
            default=1.000
        )    
        cls.vol_cover = FloatProperty(
            name="Cover",
            description="Has the effect of defining what percentage of a procedural texture maps to zero density",
            min=0.0, max=1.0,
            precision=4,
            default=1.0000
        )    
        cls.vol_density = FloatProperty(
            name="Density",
            description="Overall density multiplier",
            min=0.1, max=100.0,
            precision=3,
            default=1.000
        )    
        cls.vol_absorp = FloatProperty(
            name="Absorption",
            description="Absorption coefficient",
            min=0.0, max=1.0,
            precision=4,
            default=0.1000
        )    
        cls.vol_scatter = FloatProperty(
            name="Scatter",
            description="Scattering coefficient",
            min=0.0, max=1.0,
            precision=4,
            default=0.1000
        )
    #
    @classmethod
    def unregister(cls):
        del bpy.types.Object.bounty


def register():
    bpy.utils.register_class(TheBountyObjectSettings)

def unregister():
    bpy.utils.unregister_class(TheBountyObjectSettings)
