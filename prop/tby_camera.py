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
from bpy.props import (FloatProperty,
                       EnumProperty,
                       BoolProperty,
                       PointerProperty)

enum_camera_types =(
    ('perspective', "Perspective", ""),
    ('architect', "Architect", ""),
    ('angular', "Angular", ""),
    ('orthographic', "Ortho", ""),
)

enum_bokeh_types =(
    ('disk1', "Disk1", ""),
    ('disk2', "Disk2", ""),
    ('triangle', "Triangle", ""),
    ('square', "Square", ""),
    ('pentagon', "Pentagon", ""),
    ('hexagon', "Hexagon", ""),
    ('ring', "Ring", ""),
)

enum_bokeh_bias = (
    ('uniform', "Uniform", ""),
    ('center', "Center", ""),
    ('edge', "Edge", ""),
)

def call_camera_update(self, context):
    cam = context.camera
    camera = context.camera.bounty
    if cam is not None:
        if camera.camera_type == 'orthographic':
            cam.type = 'ORTHO'
        elif camera.camera_type == 'angular':
            cam.type = 'PANO'
        else:
            cam.type = 'PERSP'

class TheBountyCameraSettings(bpy.types.PropertyGroup):
    #
    camera_type = EnumProperty(
            name="Camera Type",
            items=enum_camera_types,
            update=call_camera_update,
            default='perspective'
     )        
    angular_angle = FloatProperty(
            name="Angle",
            min=0.0, max=180.0, precision=3,
            default=90.0
    )
    max_angle = FloatProperty(
            name="Max Angle",
            min=0.0, max=180.0, precision=3,
            default=90.0
    )
    mirrored = BoolProperty(
            name="Mirrored",
            default=False
    )
    circular = BoolProperty(
            name="Circular",
            default=False
    )
    use_clipping = BoolProperty(
            name="Use clipping",
            default=False
    )
    bokeh_type = EnumProperty(
            name="Bokeh type",
            items=enum_bokeh_types,
            default='disk1'
    )
    aperture = FloatProperty(
            name="Aperture",
            min=0.0, max=20.0, precision=5,
            default=0.0
    )
    bokeh_rotation = FloatProperty(
            name="Bokeh rotation",
            min=0.0, max=180, precision=3,
            default=0.0
    )
    bokeh_bias = EnumProperty(
            name="Bokeh bias",
            items= enum_bokeh_bias,
            default='uniform'
    )

      
def register():
    bpy.utils.register_class(TheBountyCameraSettings)
    bpy.types.Camera.bounty = PointerProperty(type=TheBountyCameraSettings )
    
def unregister():
    bpy.utils.unregister_class(TheBountyCameraSettings)
    del bpy.types.Camera.bounty
            
            
            