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
enum_hair_shapes=(
    ('ribbon','Flat Ribbon', ""),
    ('cylinder','Thin cylinder', ""),
)




class TheBountyObjectSettings(bpy.types.PropertyGroup):
    #
    geometry_type = EnumProperty(
            name="Geometry types",
            description="Set the type of geometry object(simple mesh by default)",
            items= enum_geometry_types,
            default='geometry'
    )
    ml_color = FloatVectorProperty(
            name="Meshlight color",
            description="Meshlight color",
            subtype='COLOR',
            step=1, precision=2,
            min=0.0, max=1.0,
            soft_min=0.0, soft_max=1.0,
            default=(0.8, 0.8, 0.8)
    )    
    ml_power = FloatProperty(
            name="Power",
            description="Intensity multiplier for color",
            min=0.0, max=10000.0,
            default=1.0
    )    
    ml_samples = IntProperty(
            name="Samples",
            description="Number of samples to be taken for direct lighting",
            min=0, max=512,
            default=16
    )    
    ml_double_sided = BoolProperty(
            name="Double sided",
            description="Emit light at both sides of every face",
            default=False
    )
    ml_hidde_mesh = BoolProperty(
            name="Hidde mesh",
            description="Hidde mesh emitter",
            default=False
    )
    #------------------
    # portal light
    #------------------    
    bgp_power = FloatProperty(
            name="Power",
            description="Intensity multiplier for color",
            min=0.0, max=10000.0,
            default=1.0
    )    
    bgp_samples = IntProperty(
            name="Samples",
            description="Number of samples to be taken for the light",
            min=0, max=512,
            default=16
    )    
    bgp_with_caustic = BoolProperty(
            name="Caustic photons",
            description="Allow BG Portal Light to shoot caustic photons",
            default=True
    )    
    bgp_with_diffuse = BoolProperty(
            name="Diffuse photons",
            description="Allow BG Portal Light to shoot diffuse photons",
           default=True
    )    
    bgp_photon_only = BoolProperty(
            name="Photons only",
            description="Set BG Portal Light in photon only mode (no direct light contribution)",
            default=False
    )
    #--------------------
    # volume object
    #--------------------    
    vol_region = EnumProperty(
            name="Volume region",
            description="Set the volume region",
            items= enum_volume_types,
            default='ExpDensity Volume'
    )    
    vol_height = FloatProperty(
            name="Height",
            description="Controls the density of the volume before it starts to fall off",
            min=0.0, max=1000.0,
            default=1.0
    )    
    vol_steepness = FloatProperty(
            name="Steepness",
            description="Controls how quickly the density falls off",
            min=0.0, max=10.0,
            precision=3,
            default=1.000
    )    
    vol_sharpness = FloatProperty(
            name="Sharpness",
            description="Controls how sharp a NoiseVolume looks at the border between areas of high and low density",
            min=1.0, max=100.0,
            precision=3,
            default=1.000
    )    
    vol_cover = FloatProperty(
            name="Cover",
            description="Has the effect of defining what percentage of a procedural texture maps to zero density",
            min=0.0, max=1.0,
            precision=4,
            default=1.0000
    )    
    vol_density = FloatProperty(
            name="Density",
            description="Overall density multiplier",
            min=0.1, max=100.0,
            precision=3,
            default=1.000
    )    
    vol_absorp = FloatProperty(
            name="Absorption",
            description="Absorption coefficient",
            min=0.0, max=1.0,
            precision=4,
            default=0.1000
    )    
    vol_scatter = FloatProperty(
            name="Scatter",
            description="Scattering coefficient",
            min=0.0, max=1.0,
            precision=4,
            default=0.1000
    )

class TheBountyStrandProperties(bpy.types.PropertyGroup):
    # strand properties
    
    strand_shape = EnumProperty(
            name="Strand type",
            description="Set the strand type rendering",
            items= enum_hair_shapes,
            default='ribbon'
    )
    '''
    export_color = EnumProperty( 
            name = "Strand Color",
            description = "Strand color",
            items = [
                ( 'uv_texture_map', 'UV Texture Map', 'Use emitter\'s UV position and texture map for strand color, the W goes from 0.0 at the base to 1.0 at the tip'),
                # ( 'vertex_color', 'Vertex Color', 'Use emitter\'s base vertex color')
                # ( 'strand', 'Strand', 'Each strand has a constant U of 0 and a V progressing from 0.0 at the base to 1.0 at the tip')
                ( 'none', 'None', 'Use base color')
                ],
            default = 'uv_texture_map')
    '''
    root_size = bpy.props.FloatProperty( 
            name = "Root",
            description = "Thickness of strand root",
            default = 0.25,
            min = 0.25,
            max = 100
    )
    tip_size = bpy.props.FloatProperty( 
            name = "Tip",
            description = "Thickness of strand tip",
            default = 0.25,
            min = 0.25,
            max = 100
    )
    resolution = bpy.props.IntProperty( 
            name = "Resolution",
            description = "Cylindrical resolution. Higher values require longer export times",
            default = 0,
            min = 0,
            max = 2
    )
    scaling = bpy.props.FloatProperty( 
            name = "Scaling",
            description = "Multiplier of width properties",
            default = 0.25,
            min = 0.01,
            max = 1.0
    )
    close_tip = bpy.props.BoolProperty( 
            name = "Close Tip",
            description = "Closed hair tip",
            default = True
    )
    shape = bpy.props.FloatProperty( 
            name = "Shape",
            description = "-1 the hair thickness is constant from root to tip,"\
                          " 0 hair thickness is evenly interpolated from root to tip", 
            default = 0.0,
            min = -0.99,
            max = 0.99
    )
    thick = bpy.props.BoolProperty( 
            name = "Use thick",
            description = "Use bevel curve",
            default = False
    )
    bake_hair = bpy.props.BoolProperty( 
            name = "Bake",
            description = "Bake hair to disk",
            default = False
    )
    

def register():
    #
    bpy.utils.register_class(TheBountyObjectSettings)
    bpy.types.Object.bounty = PointerProperty(type=TheBountyObjectSettings )
    
    bpy.utils.register_class(TheBountyStrandProperties)
    bpy.types.ParticleSettings.bounty = bpy.props.PointerProperty(type=TheBountyStrandProperties)
    
    
def unregister():
    #
    bpy.utils.unregister_class(TheBountyObjectSettings)
    del bpy.types.Object.bounty
    
    bpy.utils.unregister_class(TheBountyStrandProperties)
    del bpy.types.ParticleSettings.bounty
    
