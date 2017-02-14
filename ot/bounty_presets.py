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


# review for fix error with path
from bl_operators.presets import AddPresetBase
from bpy.types import Operator

import os
import bpy
from bpy.props import StringProperty, EnumProperty, BoolProperty
from bpy.types import Menu, Operator

# test
class TheBountyMaterialPresets(AddPresetBase, Operator):
    # Add material presets
    bl_idname = "bounty.material_preset_add"
    bl_label = "Material Presets"
    preset_menu = "TheBountyMaterialPresets"
    
    file_header = ("#Preset material file\n"
            "import bpy\n" +
            "material = bpy.context.object.active_material\n" +
            "mat = material.bounty\n\n")
    
    def define_values(self, material):
        mat = material.bounty
        dif = material.diffuse_color
        glos = mat.glossy_color
        mirc = mat.coat_mir_col
        mirr = mat.mirr_color
        brdf = "'" + str(mat.brdf_type) + "'"
        
        if mat.mat_type in {"glossy", "coated_glossy"}:
            values = [
                ("material.diffuse_color",(dif[0], dif[1], dif[2])),
                ("mat.brdf_type", brdf),
                ("mat.sigma", mat.sigma),
                ("mat.diffuse_reflect", mat.diffuse_reflect),
                ("mat.glossy_color", (glos[0], glos[1], glos[2])),
                ("mat.exponent", mat.exponent),
                ("mat.anisotropic", mat.anisotropic),
                ("mat.exp_u", mat.exp_u),
                ("mat.exp_v", mat.exp_v),
                ("mat.glossy_reflect", mat.glossy_reflect),
                ("mat.as_diffuse", mat.as_diffuse),
                ("mat.coat_mir_col", (mirc[0], mirc[1], mirc[2])),
                ("mat.IOR_reflection", mat.IOR_reflection),
            ]
        elif mat.mat_type == 'shinydiffusemat':
            values = [
               ("material.diffuse_color = ", (dif[0], dif[1], dif[2])),
               ("mat.mirr_color = ", (mirr[0], mirr[1], mirr[2])),
               ("mat.specular_reflect = ", mat.specular_reflect),
               ("mat.transparency = ", mat.transparency),
               ("mat.translucency = ", mat.translucency),
               ("mat.emittance = ", mat.emittance),
               ("mat.diffuse_reflect = ", mat.diffuse_reflect),
               ("mat.transmit_filter = ", mat.transmit_filter),
               ("mat.specular_reflect = ", mat.specular_reflect),
               ("mat.fresnel_effect = ", mat.fresnel_effect),
               ("mat.IOR_reflection = ", mat.IOR_reflection),
               ("mat.brdf_type = ", brdf),
               ("mat.sigma = ", mat.sigma),
            ]
        elif mat.mat_type == 'blend':
            one = "'" + str(mat.blendOne) + "'"
            two = "'" + str(mat.blendTwo) + "'"
            values = [
                ("mat.blendOne = ", one),
                ("mat.blendTwo = ", two)
            ]
        
        return values
        
          
    @classmethod
    def poll(cls, context):
        material = context.material
        return material
    
    def execute(self, context):
        material = context.material
        mat = material.bounty
        
        #bpy.context.object.active_material.bounty.preset_folder = "C:\\devs\\"
        folder = 'c:/devs/'
        name = material.name
        filepath = folder + name + '.py'
        
        with open(filepath, 'w') as pfile:
            pfile.write(self.file_header)
            pfile.write("mat.mat_type = '" + str(mat.mat_type) + "'\n")
            val = self.define_values(material)
            for p in range(0, len(val)):
                #print(shiny[p][0]+ ' = '+ str(shiny[p][1]))
                pfile.write(val[p][0] + str(val[p][1]))
                pfile.write('\n')
                
        return {'FINISHED'}


class TheBountySettingsPresets(AddPresetBase, Operator):
    # Add render presets
    bl_idname = "bounty.render_preset_add"
    bl_label = "TheBounty Settings Presets"
    preset_menu = "THEBOUNTY_MT_render_presets"
    
    preset_defines = [
        "scene = bpy.context.scene.bounty",
        "render = bpy.context.scene.render"
    ]
    
    preset_subdir = "thebounty/render"
    
    folder = bpy.props.StringProperty(
            name="Presets folder",
            description="",
            subtype='DIR_PATH',
            default=""
    )
    
    @property
    def preset_values(self):
        #
        print(self.folder)
    
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
        return preset_values

    
class TheBountyMaterialPresetsd(AddPresetBase, Operator):
    # Add material presets
    bl_idname = "bounty.material_preset_addd"
    bl_label = "Material Presets"
    #preset_menu = "TheBountyMaterialPresets"
    
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
        "mat.translucency",
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
