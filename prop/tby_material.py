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
                       BoolProperty,
                       EnumProperty,
                       FloatVectorProperty,
                       PointerProperty,
                       StringProperty)


enum_material_types = (
    ('shinydiffusemat', "Shiny Diffuse",    ""),
    ('glossy',          "Glossy",           ""),
    ('coated_glossy',   "Coated Glossy",    ""),
    ('glass',           "Glass",            ""),
    ('rough_glass',     "Rough Glass",      ""),
    ('blend',           "Blend",            ""),
    ('translucent',     "Translucent(SSS)", ""),
)

enum_reflectance_mode = (
    ('oren-nayar', "Oren-Nayar", "Reflectance Model"),
    ('lambert', "Lambert", "Reflectance Model"),
)
enum_sss_presets = (
    ('cream',       "Cream",        ""),
    ('ketchup',     "Ketchup",      ""),
    ('marble',      "Marble",       ""),
    ('milkskimmed', "Milk Skimmed", ""),
    ('milkwhole',   "Milk Whole",   ""),
    ('potato',      "Potato",       ""),
    ('skinbrown',   "Skin Brown",   ""),
    ('skinpink',    "Skin Pink",    ""),
    ('skinyellow',  "Skin Yellow",  ""),
    ('custom',      "Custom",       ""),
)   
  

class TheBountyMaterialProperties(bpy.types.PropertyGroup):
    #---------------------------
    # list of material properies
    #---------------------------
    blendOne = StringProperty(
            name="Material One",
            description="Name of the material one in blend material",
            default="blendone"
    )
    blendTwo = StringProperty(
            name="Material Two",
            description="Name of the material one in blend material",
            default="blendtwo"
    )
    mat_type = EnumProperty(
            name="Material type",
            items=enum_material_types,
            default='shinydiffusemat'
    )
    diff_color = FloatVectorProperty(
            name="Diffuse color",
            description="Diffuse albedo color material",
            subtype='COLOR',
            min=0.0, max=1.0,
            default=(0.8, 0.8, 0.8)
    )
    emittance = FloatProperty(
            name="Emit",
            description="Amount of emissive property",
            min=0.0, max=1.0,
            step=1, precision=3,
            soft_min=0.0, soft_max=1.0,
            default=0.00
    )       
    diffuse_reflect = FloatProperty(
            name="Reflection strength",
            description="Amount of diffuse reflection",
            min=0.0, max=1.0,
            step=1, precision=3,
            soft_min=0.0, soft_max=1.0,
            default=1.000
    )
    mirror_color = FloatVectorProperty(
            name="Mirror color",
            description="Mirror reflectance color material",
            subtype='COLOR',
            min=0.0, max=1.0,
            default=(0.8, 0.8, 0.8)
    )    
    specular_reflect = FloatProperty(
            name="Reflection strength",
            description="Amount of perfect specular reflection (mirror)",
            min=0.0, max=1.0,
            step=1, precision=3,
            soft_min=0.0, soft_max=1.0,
            default=0.000
    )    
    transparency = FloatProperty(
            name="Transparency",
            description="Material transparency",
            min=0.0, max=1.0,
            step=1, precision=3,
            soft_min=0.0, soft_max=1.0,
            default=0.000
    )
    translucency = FloatProperty(
            name="Translucency",
            description="Material translucency",
            min=0.0, max=1.0,
            step=1, precision=3,
            soft_min=0.0, soft_max=1.0,
            default=0.000
    )       
    transmit_filter = FloatProperty(
            name="Transmit filter",
            description="Amount of tinting of light passing through the Material",
            min=0.0, max=1.0, step=1, precision=3,
            soft_min=0.0, soft_max=1.0, default=1.000
    )    
    fresnel_effect = BoolProperty(
            name="Fresnel effect",
            description="Apply a fresnel effect to specular reflection",
            default=False
    )    
    brdf_type = EnumProperty(
            name="BDRF",
            description="Reflectance model",
            items=enum_reflectance_mode,
            default='lambert',
    )
    sigma = FloatProperty(
            name="Sigma",
            description="Roughness of the surface",
            min=0.0, max=1.0, step=1, precision=4,
            soft_min=0.0, soft_max=1.0,
            default=0.10000
    ) 
    mirr_color = FloatVectorProperty(
            name="Mirror color",
            description="Mirror Color",
            subtype='COLOR',
            min=0.0, max=1.0,
            default=(1.0, 1.0, 1.0)
    )   
    glossy_color = FloatVectorProperty(
            name="Glossy color",
            description="Glossy Color",
            subtype='COLOR',
            min=0.0, max=1.0,
            default=(1.0, 1.0, 1.0)
    )
    coat_mir_col = FloatVectorProperty(
            name="Mirror color",
            description="Reflection color of coated layer",
            subtype='COLOR',
            min=0.0, max=1.0,
            default=(1.0, 1.0, 1.0)
    )
    glass_mir_col = FloatVectorProperty(
            name="Reflection color",
            description="Reflection color of glass material",
            subtype='COLOR',
            min=0.0, max=1.0,
            default=(1.0, 1.0, 1.0)
    )
    glossy_reflect = FloatProperty(
            name="Reflection strength",
            description="Amount of glossy reflection",
            min=0.0, max=1.0, step=1, precision=3,
            soft_min=0.0, soft_max=1.0, default=0.0001
    )    
    exp_u = FloatProperty(
            name="Exponent U",
            description="Horizontal anisotropic exponent value",
            min=1.0, max=10000.0, step=10, precision=2,
            soft_min=1.0, soft_max=10000.0, default=50.00
    )    
    exp_v = FloatProperty(
            name="Exponent V",
            description="Vertical anisotropic exponent value",
            min=1.0, max=10000.0, step=10, precision=2,
            soft_min=1.0, soft_max=10000.0, default=50.00
    )    
    exponent = FloatProperty(
            name="Exponent",
            description="Blur of the glossy reflection, higher exponent = sharper reflections",
            min=1.0, max=10000.0, step=10, precision=2,
            soft_min=1.0, soft_max=10000.0, default=500.00
    )    
    as_diffuse = BoolProperty(
            name="Use photon map",
            description="Treat glossy component as diffuse",
            default=False
    )    
    anisotropic = BoolProperty(
            name="Anisotropic",
            description="Use anisotropic reflections",
            default=False
    )    
    IOR_refraction = FloatProperty(
            name="IOR",
            description="Index of refraction",
            min=0.0, max=30.0, step=1, precision=3,
            soft_min=0.0, soft_max=30.0, default=1.520
    )    
    IOR_reflection = FloatProperty(
            name="IOR",
            description="Fresnel reflection strength",
            min=1.0, max=30.0, step=1, precision=3,
            soft_min=1.0, soft_max=30.0, default=1.800
    )    
    absorption = FloatVectorProperty(
            name="Absorption Color",
            description="Glass volumetric absorption color. White disables absorption",
            subtype='COLOR',
            min=0.0, max=1.0, step=1, precision=3,
            default=(1.0, 1.0, 1.0)
    )    
    absorption_dist = FloatProperty(
            name="Distance of Absorption",
            description="Absorption distance scale",
            min=0.0, max=100.0,
            step=1, precision=4,
            soft_min=0.0, soft_max=100.0,
            default=1.0000
    )    
    glass_transmit = FloatProperty(
            name="Transmit filter",
            description="Filter strength applied to refracted light",
            min=0.0, max=1.0,
            step=1, precision=3,
            soft_min=0.0, soft_max=1.0,
            default=1.000
    )    
    filter_color = FloatVectorProperty(
            name="Filter color",
            description="Filter color for refracted light of glass, also tint transparent shadows if enabled",
            subtype='COLOR',
            min=0.0, max=1.0,
            default=(1.0, 1.0, 1.0)
    )    
    dispersion_power = FloatProperty(
            name="Power",
            description="Strength of dispersion effect, disabled when 0",
            min=0.0, max=5.0,
            step=1, precision=4,
            soft_min=0.0, soft_max=5.0,
            default=0.0000
    )    
    refr_roughness = FloatProperty(
            name="Exponent",
            description="Refraction factor on rough glass material",
            min=0.0, max=1.0,
            step=1, precision=3,
            soft_min=0.0, soft_max=1.0,
            default=0.200
    )    
    fake_shadows = BoolProperty(
            name="Fake shadows",
            description="Let light straight through for shadow calculation. Not to be used with dispersion",
            default=False
    )
    blend_value = FloatProperty(
            name="Blend value",
            description="The mixing balance: 0 -> only material 1, 1.0 -> only material 2",
            min=0.0, max=1.0, step=3, precision=3,
            soft_min=0.0, soft_max=1.0,
            default=0.500
    )      
    #--------------------------------------------
    #  Translucent SubSurface Scattering settings
    #--------------------------------------------
    sss_presets = EnumProperty(
            name="SSS",
            description="Scattering presets",
            items=enum_sss_presets,
            default='cream',
    )
    sssColor = FloatVectorProperty(
            name="Diffuse color",
            description="Diffuse color",
            subtype='COLOR',
            min=0.0, max=1.0,
            default=(1.0, 1.0, 1.0)
    )            
    sssSpecularColor = FloatVectorProperty(
            name="Specular Color",
            description="Specular Color",
            subtype='COLOR',
            min=0.0, max=1.0,
            default=(1.0, 1.0, 1.0)
    )    
    sssSigmaA = FloatVectorProperty(
            name="Absorption Color",
            description="Absorption Color",
            subtype='COLOR',
            min=0.0, max=2.0,
            default=(0.80, 0.80, 0.80)
    )    
    sssSigmaS = FloatVectorProperty(
            name="Scatter color",
            description="Scatter color",
            subtype='COLOR', precision=4,
            min=0.0, max=1.0,
            default=(0.7, 0.7, 0.7)
    )        
    sssSigmaS_factor = FloatProperty(
            name="SigmaS factor",
            description="Sigma factor for SSS",
            min=0.1, max=100.0,
            step=0.1, precision=2,
            default=10.0
    )    
    sss_transmit = FloatProperty(
            name="Transmittance",
            description="Transmittance",
            min=0.0, max=1.0,
            step=0.1, precision=3,
            default=0.50
    )        
    sssIOR = FloatProperty(
            name="IOR",
            description="Index of refraction for SSS",
            min=0.0, max=3.0, step=1, precision=3,
            soft_min=1.0, soft_max=30.0, default=1.300
    )
    phaseFuction = FloatProperty(
            name="Phase Function",
            description="Relative to forward  or backward scattering",
            min=-0.99, max=0.99, step=0.01, precision=2,
            default=0.0
    )

def register():
    bpy.utils.register_class(TheBountyMaterialProperties)
    bpy.types.Material.bounty = PointerProperty(type=TheBountyMaterialProperties )
    
def unregister():
    bpy.utils.unregister_class(TheBountyMaterialProperties)
    #bpy.types.Material.bounty = PointerProperty(type=TheBountyMaterialProperties )
