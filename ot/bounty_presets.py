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
import bpy
import os

class TheBountyMaterialPresets(AddPresetBase, bpy.types.Operator):
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
                (ms +".diffuse_color",(diff[0], diff[1], diff[2])),
                (m +".glossy_color", (glos[0], glos[1], glos[2])),
                (m +".coat_mir_col", (cmir[0], cmir[1], cmir[2])),
                (m +".diffuse_reflect", mat.diffuse_reflect),
                (m +".mat_type", self.to_str(mat.mat_type)),
                (m +".glossy_reflect", mat.glossy_reflect),
                (m +".IOR_reflection", mat.IOR_reflection),
                (m +".anisotropic", mat.anisotropic),
                (m +".as_diffuse", mat.as_diffuse),
                (m +".exponent", mat.exponent),
                (m +".exp_u", mat.exp_u),
                (m +".exp_v", mat.exp_v),
                (m +".sigma", mat.sigma),
                (m +".brdf_type", brdf),
            ]
        elif mat.mat_type in {'glass', 'rough_glass'}:
            filt = mat.filter_color
            absp = mat.absorption
            mirc = mat.glass_mir_col
            values = [
                (m +".glass_mir_col", (mirc[0], mirc[1], mirc[2])),
                (m +".filter_color", (filt[0], filt[1], filt[2])),
                (m +".absorption", (absp[0], absp[1], absp[2])),
                (m +".dispersion_power", mat.dispersion_power),
                (m +".absorption_dist", mat.absorption_dist),
                (m +".mat_type", self.to_str(mat.mat_type)),
                (m +".IOR_refraction", mat.IOR_refraction),
                (m +".refr_roughness", mat.refr_roughness),
                (m +".glass_transmit", mat.glass_transmit),
                (m +".fake_shadows", mat.fake_shadows),                
            ]
        elif mat.mat_type == 'shinydiffusemat':
            mircol = mat.mirror_color
            values = [
                (m +".mirr_color", (mircol[0], mircol[1], mircol[2])),
                (ms +".diffuse_color", (diff[0], diff[1], diff[2])),
                (m +".specular_reflect", mat.specular_reflect),
                (m +".specular_reflect", mat.specular_reflect),
                (m +".diffuse_reflect", mat.diffuse_reflect),
                (m +".transmit_filter", mat.transmit_filter),
                (m +".mat_type", self.to_str(mat.mat_type)),
                (m +".fresnel_effect", mat.fresnel_effect),
                (m +".IOR_reflection", mat.IOR_reflection),
                (m +".transparency", mat.transparency),
                (m +".translucency", mat.translucency),
                (m +".emittance", mat.emittance),
                (m +".sigma", mat.sigma),
                (m +".brdf_type", brdf),
            ]
                    
        elif mat.mat_type == 'translucent':
            sSpec = mat.sssSpecularColor
            sigmA = mat.sssSigmaA
            sigmS = mat.sssSigmaS
            values = [
                (m +".sssSpecularColor", (sSpec[0], sSpec[1], sSpec[2])),
                (ms +".diffuse_color", (diff[0], diff[1], diff[2])),
                (m +".glossy_color", (glos[0], glos[1], glos[2])),
                (m +".sssSigmaS", (sigmS[0], sigmS[1], sigmS[2])),
                (m +".sssSigmaA", (sigmA[0], sigmA[1], sigmA[2])),
                (m +".sssSigmaS_factor", mat.sssSigmaS_factor),
                (m +".diffuse_reflect", mat.diffuse_reflect),
                (m +".mat_type", self.to_str(mat.mat_type)),
                (m +".glossy_reflect", mat.glossy_reflect),
                (m +".phaseFuction", mat.phaseFuction),
                (m +".sss_transmit", mat.sss_transmit),
                (m +".exponent", mat.exponent),
                (m +".sssIOR", mat.sssIOR),
            ]
        
        elif mat.mat_type == 'blend':
            # blend material
            values = [
                ("mat.mat_type", self.to_str(mat.mat_type)),
                ("mat.blendOne", self.to_str(mat.blendOne)),
                ("mat.blendTwo", self.to_str(mat.blendTwo)),
                ("mat.blend_value", mat.blend_value),
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
    # test
    remove_active = bpy.props.BoolProperty(
            default=False,
            options={'HIDDEN', 'SKIP_SAVE'},
    )
       
    def execute(self, context):
        #
        material = bpy.context.object.active_material
        ext = ".py"
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
        #
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
                
        else:
            print('Remove presets')
        
                 
        return {'FINISHED'}
    

class TheBountySettingsPresets(AddPresetBase, bpy.types.Operator):
    # Add render presets
    bl_idname = "bounty.render_preset_add"
    bl_label = "TheBounty Settings Presets"
    preset_menu = "THEBOUNTY_MT_render_presets"
    
    preset_defines = [
        "scene = bpy.context.scene.bounty",
        "render = bpy.context.scene.render"
    ]
    
def register():
    bpy.utils.register_class(TheBountySettingsPresets)
    bpy.utils.register_class(TheBountyMaterialPresets)
    

def unregister():
    bpy.utils.unregister_class(TheBountySettingsPresets)
    bpy.utils.unregister_class(TheBountyMaterialPresets)
    

if __name__ == "__main__":
    register()
