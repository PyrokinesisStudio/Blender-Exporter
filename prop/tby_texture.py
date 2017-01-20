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

# try to update blender propertie texture.type to texture.bounty.tex_type
def call_tex_type_update(self, context):
    try:
        tex = context.texture
        if tex is not None:
            tex.type = tex.bounty.tex_type
    except:
        pass
enum_texture_coord_type = [
    ('ORCO','Generated',""),
    ('OBJECT','Object',""),
    ('GLOBAL','Global',""),
    ('UV','UV',""),
    ('STRAND','Strand',""),
    ('WINDOW','Window',""),
    ('NORMAL','Normal',""),
    ('REFLECTION','Reflection',""),
    ('STRESS','Stress',""),
    ('TANGENT','Tangent',""),
]
enum_texture_projection_mode = [
    ('FLAT',   'Flat',  "Flat texture projection"),
    ('CUBE',   'Cube',  "Cube texture projection"),
    ('TUBE',   'Tube',  "Cylindrical texture projection"),
    ('SPHERE', 'Sphere',"Spherical texture projection"),        
]
enum_mapping_mode = [
    ('X','X',""),
    ('Y','Y',""),
    ('Z','Z',""),
    ('None','None',"")
]    
enum_texture_type = (
    ('NONE', "None", ""),
    ('BLEND', "Blend", ""),
    ('CLOUDS', "Clouds", ""),
    ('WOOD', "Wood", ""),
    ('MARBLE', "Marble", ""),
    ('VORONOI', "Voronoi", ""),
    ('MUSGRAVE', "Musgrave", ""),
    ('DISTORTED_NOISE', "Distorted Noise", ""),
    ('IMAGE', "Image", ""),
)
enum_interpolation_type=(
    ('none', "None", ""),
    ('bilinear', "Bilinear", ""),
    ('bicubic', "Bicubic", ""),
)
enum_blending_modes=(
    ('lighten', 'Lighten',''),
    ('darken', 'Darken',''),
    ('divide', 'Divide',''),
    ('difference', 'Difference',''),
    ('screen', 'Screen',''),
    ('multiply', 'Multiply',''),
    ('subtract', 'Subtract',''),
    ('add', 'Add',''),
    ('mix', 'Mix','')
)

class TheBountyTextureProperties(bpy.types.PropertyGroup):
    #--------------------------
    # Own texture properties.
    #--------------------------
    tex_type = bpy.props.EnumProperty(
            name="Type", description="",
            items=enum_texture_type,
            update=call_tex_type_update,
            default='NONE'
    )
    is_normal_map = bpy.props.BoolProperty(
            name="Use map as normal map",
            description="Use image RGB values for normal mapping",
            default=False
    )
    use_alpha = bpy.props.BoolProperty(
            name="Use alpha image info",
            description="Use alpha values for image mapping",
            default=False
    )    
    interpolation_type= bpy.props.EnumProperty(
            name="Interpolation", 
            description="Use image interpolation",
            items=enum_interpolation_type, 
            default="bilinear"
    )
    #---------------------------
    # Texture nodes properties
    #---------------------------     
    texture_coord = bpy.props.EnumProperty(
            name="Mapping",
            description="Texture coordinates mapping mode",
            items=enum_texture_coord_type,
            default='UV',
    )       
    projection_type = bpy.props.EnumProperty(
            name="Projection",
            description="Texture projection mode",
            items=enum_texture_projection_mode,
            default='FLAT',
    )    
    mapping_x = bpy.props.EnumProperty(
            name="", description="", items=enum_mapping_mode, default='X'
    )
    mapping_y = bpy.props.EnumProperty(
            name="", description="", items=enum_mapping_mode, default='Y'
    )
    mapping_z = bpy.props.EnumProperty(
            name="", description="", items=enum_mapping_mode, default='Z'
    )
    offset = bpy.props.FloatVectorProperty(
            name = "Offset", description = "", subtype = "XYZ", 
            min=-10.0, max=10.0, step=1, precision=2, default = (0.0, 0.0, 0.0)
    )
    scale = bpy.props.FloatVectorProperty(
            name = "Scale", description = "", subtype = "XYZ", 
            min=-100.0, max=100.0, step=1, precision=2, default = (1.0, 1.0, 1.0)
    )
    zero_to_one = bpy.props.FloatProperty(
            name="Amount", description="",
            min=0.0, max=1.0, step=1, precision=3,
            soft_min=0.0, soft_max=1.0, default=1.00
    )
    min_one_to_one = bpy.props.FloatProperty(
            name="Amount", description="",
            min=-1.0, max=1.0, step=1, precision=3,
            soft_min=-1.0, soft_max=1.0, default=1.00
    )    
    influence = bpy.props.FloatProperty(
            name="Influence", description="Amount of texture/color influence on a  material ( 0 : color, 1: texture)",
            min=0.0, max=1.0, step=1, precision=3,
            soft_min=0.0, soft_max=1.0, default=1.00
    )
    image_map = bpy.props.StringProperty(
            name="", description="Image File to be used on texture",
            subtype='FILE_PATH', default=""
    )
    blend = bpy.props.EnumProperty(
            name='', description='',
            items =enum_blending_modes,
            default='mix'
    )
    negative = bpy.props.BoolProperty(
            name='Negative', description='',
            default=False
    )
    no_rgb = bpy.props.BoolProperty(
            name='No RGB', description='',
            default=False
    )
    stencil = bpy.props.BoolProperty(
            name='Stencil', description='',
            default=False
    )
    bool_option = bpy.props.BoolProperty(
            name='Boolean', description='',
            default=False
    )

def register():
    bpy.utils.register_class(TheBountyTextureProperties)
    bpy.types.Texture.bounty = bpy.props.PointerProperty(type=TheBountyTextureProperties )
    
def unregister():
    bpy.utils.unregister_class(TheBountyTextureProperties)
    del bpy.types.Texture.bounty