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

from bl_operators.presets import AddPresetBase
from bpy.types import Operator

import os
import bpy
from bpy.types import Menu, Operator

# test
class TheBountyMaterialPresets(AddPresetBase, Operator):
    # Add material presets
    bl_idname = "bounty.material_preset_add"
    bl_label = "Material Presets"
    preset_menu = "TheBountyMaterialPresets"
    preset_subdir = "thebounty/material"
    
    file_header = (
        "#Preset material file\n"
        "import bpy\n" +
        "material = bpy.context.object.active_material\n" +
        "mat = material.bounty\n\n"
    )
        
    def to_str(self, item):
        return ("'" + str(item) + "'")
    
    def define_values(self, material, blm=None):
        #
        mat = material.bounty
        diff = material.diffuse_color
        glos = mat.glossy_color        
        brdf = self.to_str(mat.brdf_type)
        # use only for write params to preset file, for data acces use always 'mat'
        m = 'mat' if blm is None else blm + '.bounty'
        ms = "material" if blm is None else blm # special case, without .bounty    
        
        if mat.mat_type in {"glossy", "coated_glossy"}:
            cmir = mat.coat_mir_col
            values = [
                (m +".mat_type", self.to_str(mat.mat_type)),
                (ms +".diffuse_color",(diff[0], diff[1], diff[2])),
                (m +".brdf_type", brdf),
                (m +".sigma", mat.sigma),
                (m +".diffuse_reflect", mat.diffuse_reflect),
                (m +".glossy_color", (glos[0], glos[1], glos[2])),
                (m +".exponent", mat.exponent),
                (m +".anisotropic", mat.anisotropic),
                (m +".exp_u", mat.exp_u),
                (m +".exp_v", mat.exp_v),
                (m +".glossy_reflect", mat.glossy_reflect),
                (m +".as_diffuse", mat.as_diffuse),
                (m +".coat_mir_col", (cmir[0], cmir[1], cmir[2])),
                (m +".IOR_reflection", mat.IOR_reflection),
            ]
        elif mat.mat_type in {'glass', 'rough_glass'}:
            filt = mat.filter_color
            absp = mat.absorption
            mirc = mat.glass_mir_col
            values = [
                (m +".mat_type", self.to_str(mat.mat_type)),
                (m +".IOR_refraction", mat.IOR_refraction),
                (m +".absorption", (absp[0], absp[1], absp[2])),
                (m +".absorption_dist", mat.absorption_dist),
                (m +".dispersion_power", mat.dispersion_power),
                (m +".refr_roughness", mat.refr_roughness),
                (m +".filter_color", (filt[0], filt[1], filt[2])),
                (m +".glass_mir_col", (mirc[0], mirc[1], mirc[2])),
                (m +".glass_transmit", mat.glass_transmit),
                (m +".fake_shadows", mat.fake_shadows),                
            ]
        elif mat.mat_type == 'shinydiffusemat':
            mirr = mat.mirr_color
            values = [
                (m +".mat_type", self.to_str(mat.mat_type)),
                (ms +".diffuse_color", (diff[0], diff[1], diff[2])),
                (m +".mirr_color", (mirr[0], mirr[1], mirr[2])),
                (m +".specular_reflect", mat.specular_reflect),
                (m +".transparency", mat.transparency),
                (m +".translucency", mat.translucency),
                (m +".emittance", mat.emittance),
                (m +".diffuse_reflect", mat.diffuse_reflect),
                (m +".transmit_filter", mat.transmit_filter),
                (m +".specular_reflect", mat.specular_reflect),
                (m +".fresnel_effect", mat.fresnel_effect),
                (m +".IOR_reflection", mat.IOR_reflection),
                (m +".brdf_type", brdf),
                (m +".sigma = ", mat.sigma),
            ]
                    
        elif mat.mat_type == 'translucent':
            sSpec = mat.sssSpecularColor
            sigmA = mat.sssSigmaA
            sigmS = mat.sssSigmaS
            values = [
                (m +".mat_type", self.to_str(mat.mat_type)),
                (ms +".diffuse_color", (diff[0], diff[1], diff[2])),
                (m +".diffuse_reflect", mat.diffuse_reflect),
                (m +".glossy_color", (glos[0], glos[1], glos[2])),
                (m +".glossy_reflect", mat.glossy_reflect),
                (m +".sssSpecularColor", (sSpec[0], sSpec[1], sSpec[2])),
                (m +".exponent", mat.exponent),
                (m +".sssSigmaS", (sigmS[0], sigmS[1], sigmS[2])),
                (m +".sssSigmaS_factor", mat.sssSigmaS_factor),
                (m +".phaseFuction", mat.phaseFuction),
                (m +".sssSigmaA", (sigmA[0], sigmA[1], sigmA[2])),
                (m +".sss_transmit", mat.sss_transmit),
                (m +".sssIOR", mat.sssIOR),
            ]
        
        elif mat.mat_type == 'blend':
            # blend material
            values = [
                ("mat.mat_type", self.to_str(mat.mat_type)),
                ("mat.blendOne", self.to_str(mat.blendOne)),
                ("mat.blend_value", mat.blend_value),
                ("mat.blendTwo", self.to_str(mat.blendTwo)),
            ]
            # blend one
            mat1 = bpy.data.materials[mat.blendOne]            
            values +=[("\nmat1", "bpy.data.materials.new(mat.blendOne)"),]            
            values += self.define_values(mat1, 'mat1')
                        
            # blend two
            mat2 = bpy.data.materials[mat.blendTwo]            
            values +=[("\nmat2", "bpy.data.materials.new(mat.blendTwo)"),]            
            values += self.define_values(mat2, 'mat2')
            
        return values
        
    '''      
    @classmethod
    def poll(cls, context):
        material = context.material
        return material
    '''
   
    def execute(self, context):
        #
        material = bpy.context.object.active_material
        #material = context.material # seems that is the same of above
        ext = ".py"
        #----------------------------------------------------------
        name = self.name.strip()
        if not name:
            return {'FINISHED'}

        filename = self.as_filename(name)

        target_path = os.path.join("presets", self.preset_subdir)
        target_path = bpy.utils.user_resource('SCRIPTS', target_path, create=True)

        if not target_path:
            self.report({'WARNING'}, "Failed to create presets path")
            return {'CANCELLED'}

        filepath = os.path.join(target_path, filename) + ext
        #----------------------------------------------------------
        if not self.remove_active:
            #
            val = list()
            # own write function for special cases with 'blendmat'
            with open(filepath, 'w') as pfile:
                pfile.write(self.file_header)
                #
                val = self.define_values(material)
                for p in range(0, len(val)):
                    #
                    pfile.write(val[p][0]+' = '+ str(val[p][1]))
                    pfile.write('\n')
                #
                self.report({'INFO'}, "File preset write sucessful: "+ str(filepath))
        
        #if hasattr(self, "post_cb"):
        #    self.post_cb(context)
                 
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
