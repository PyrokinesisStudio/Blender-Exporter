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



import os
import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty
#
from bl_operators.presets import AddPresetBase

#-----------------------------------------------
def getPresetpath():
    """Support user defined scripts directory
       Find the first ocurrence and return it as preset path"""
    presetpath = ""
    for p in bpy.utils.script_paths():
        presetpath = os.path.join(p, 'addons', 'thebounty', 'presets')
        if os.path.exists(presetpath):
            break
    #return presetpath
    
    # why not just do this
    script_file = os.path.realpath(__file__)
    directory = os.path.dirname(script_file)
    directory = os.path.join(directory, "presets")
    return directory

#----------------------------------------------------------------

class TheBountySettingsPresets(AddPresetBase, bpy.types.Operator):
    # Add render presets
    bl_idname = "bounty.render_preset_add"
    bl_label = "TheBounty Settings Presets"
    preset_menu = "THEBOUNTY_MT_render_presets"
    
    preset_defines = [
        "scene = bpy.context.scene.bounty",
        "render = bpy.context.scene.render"
    ]
    preset_values = [
        "render.resolution_x",
        "render.resolution_y",
        "scene.gs_ray_depth",
        "scene.gs_shadow_depth",
        "scene.gs_threads",
        "scene.gs_gamma",
        "scene.gs_gamma_input",
        "scene.gs_tile_size",
        "scene.gs_tile_order",
        "scene.gs_auto_threads",
        "scene.gs_clay_render",
        "scene.gs_draw_params",
        "scene.gs_custom_string",
        "scene.gs_premult",
        "scene.gs_transp_shad",
        "scene.gs_clamp_rgb",
        "scene.gs_show_sam_pix",
        "scene.gs_z_channel",
        "scene.gs_type_render",
        "scene.intg_light_method",
        "scene.intg_use_caustics",
        "scene.intg_photons",
        "scene.intg_caustic_mix",
        "scene.intg_caustic_depth",
        "scene.intg_caustic_radius",
        "scene.intg_use_AO",
        "scene.intg_AO_samples",
        "scene.intg_AO_distance",
        "scene.intg_AO_color",
        "scene.intg_bounces",
        "scene.intg_diffuse_radius",
        "scene.intg_cPhotons",
        "scene.intg_search",
        "scene.intg_final_gather",
        "scene.intg_fg_bounces",
        "scene.intg_fg_samples",
        "scene.intg_show_map",
        "scene.intg_caustic_method",
        "scene.intg_path_samples",
        "scene.intg_no_recursion",
        "scene.intg_debug_type",
        "scene.intg_show_perturbed_normals",
        "scene.intg_pm_ire",
        "scene.intg_pass_num",
        "scene.intg_times",
        "scene.intg_photon_radius",
        "scene.AA_min_samples",
        "scene.AA_inc_samples",
        "scene.AA_passes",
        "scene.AA_threshold",
        "scene.AA_pixelwidth",
        "scene.AA_filter_type"
    ]

    preset_subdir = "thebounty/render"

    
class TheBountyMaterialPresets(AddPresetBase, bpy.types.Operator):
    # Add material presets
    bl_idname = "bounty.material_preset_add"
    bl_label = "Material Presets"
    preset_menu = "TheBountyMaterialPresets"
    # test

    preset_defines = [
        "material = bpy.context.object.active_material",
        "mat = material.bounty"
    ]    
    preset_values = [   
        "mat.absorption",
        "material.diffuse_color",
        "mat.absorption_dist",
        "mat.anisotropic",
        "mat.as_diffuse",
        "mat.brdf_type",
        "mat.coat_mir_col",
        "mat.diffuse_reflect",
        "mat.dispersion_power",
        "mat.exp_u",
        "mat.exp_v",
        "mat.exponent",
        "mat.fake_shadows",
        "mat.filter_color",
        "mat.fresnel_effect",
        "mat.glass_mir_col",
        "mat.glass_transmit",
        "mat.glossy_color",
        "mat.glossy_reflect",
        "mat.IOR_reflection",
        "mat.IOR_refraction",
        "mat.mat_type",
        # "mat.material1", # blend material not work
        # "mat.material2",
        # "mat.blend_value",
        "mat.refr_roughness",
        "mat.sigma",
        "mat.specular_reflect",
        "mat.transmit_filter",
        "mat.transparency",
        # sss
        "mat.phaseFuction",
        "mat.sss_transmit",
        "mat.sssColor",
        "mat.sssIOR",
        "mat.sssSigmaA",
        "mat.sssSigmaS",
        "mat.sssSigmaS_factor",
        "mat.sssSpecularColor"
    ]
    preset_subdir = "thebounty/material"    
                
    
def register():
    #pass
    bpy.utils.register_class(TheBountySettingsPresets)
    bpy.utils.register_class(TheBountyMaterialPresets)
    
def unregister():
    #pass
    bpy.utils.unregister_class(TheBountySettingsPresets)
    bpy.utils.unregister_class(TheBountyMaterialPresets)
    
if __name__ == "__main__":
    register()
