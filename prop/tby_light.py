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
from bpy.props import (EnumProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       StringProperty,
                       PointerProperty
                       )

def set_shadow_method(self, context):
    lamp = context.lamp
    if context.lamp.bounty.show_dist_clip:
        lamp.shadow_method = 'BUFFER_SHADOW'
    else:
        lamp.shadow_method = 'RAY_SHADOW'

def sync_sphere_light(self, context):
    lamp = context.lamp
    if context.lamp.bounty.use_sphere:
        lamp.use_sphere = True
        # reasonable default size
        lamp.distance = 1
    else:
        lamp.use_sphere = False
        lamp.distance = 10
   
#######
def sync_with_distance(self, context):
    lamp = context.lamp
    radius = context.lamp.bounty.sphere_radius
    if radius != context.lamp.distance:
        context.lamp.distance = context.lamp.bounty.sphere_radius 
       
class TheBountyLightProperties(bpy.types.PropertyGroup):
    #
    nodetree = StringProperty(
            name="Node Tree",
            description="Name of the node tree for this light",
            default=""
    )
    energy = FloatProperty(
            name="Power",
            description="Intensity multiplier for color",
            min=0.0, max=10000.0,
            default=1.0
    )
    use_sphere = BoolProperty(
            name="Use Sphere",
            description="Use sphere object for light",
            default=False,
            update = sync_sphere_light
    )    
    sphere_radius = FloatProperty(
            name="Radius",
            description="Radius of the sphere light",
            min=0.01, max=10000.0,
            soft_min=0.01, soft_max=100.0,
            default=1.0, update=sync_with_distance
    )
    shadows_size = FloatProperty(
            name="Shadows soft size",
            description="Radius of directional cone",
            min=0.01, max=10000.0,
            soft_min=0.01, soft_max=100.0,
            default=10.0 #, update=sync_with_size
    )      
    create_geometry = BoolProperty(
            name="Create and show geometry",
            description="Creates a visible geometry in the dimensions of the light during the render",
            default=False
    )    
    infinite = BoolProperty(
            name="Infinite",
            description="Determines if light is infinite or filling a semi-infinite cylinder",
            default=True
    )    
    spot_soft_shadows = BoolProperty(
            name="Soft shadows (unused with photon only)",
            description="Use soft shadows(turn disabled with 'photon only')",
            default=False
    )    
    shadow_fuzzyness = FloatProperty(
            name="Shadow fuzzyness",
            description="Fuzzyness of the soft shadows (0 - hard shadow, 1 - fuzzy shadow)",
            min=0.0, max=1.0,
            default=1.0
    )    
    photon_only = BoolProperty(
            name="Photon only",
            description="This spot will only throw photons, not direct light",
            default=False
    )    
    angle = FloatProperty(
            name="Angle",
            description="Angle of the cone in degrees (shadow softness)",
            min=0.0, max=80.0,
            default=0.5
    )    
    ies_soft_shadows = BoolProperty(
            name="IES Soft shadows",
            description="Use soft shadows for IES light type",
            default=False
    )    
    ies_file = StringProperty(
            name="IES File",
            description="File to be used as the light projection",
            subtype='FILE_PATH',
            default=""
    )    
    samples = IntProperty(
            name="Samples",
            description="Number of samples to be taken for direct lighting",
            min=0, max=512,
            default=16
    )    
    show_dist_clip = BoolProperty(
            name="Show clipping",
            description="Show clip start and clip end settings for spot lamp in 3D view",
            default=False, 
            update=set_shadow_method
    )
    hemi_type = EnumProperty(
            name="Hemi light type",
            description="180 degree costant light source",
            items=(
                ('infinite', "Infinite", "Infinite light like Sun"),
                ('directional', "Directional", "Directional light like spotlight useful for concentrate light on specific areas"),
            ),
            default='infinite'
    )
    
#
def register():
    bpy.utils.register_class(TheBountyLightProperties)
    bpy.types.Lamp.bounty = PointerProperty(type=TheBountyLightProperties )
    
def unregister():
    bpy.utils.unregister_class(TheBountyLightProperties)
    del bpy.types.Lamp.bounty
