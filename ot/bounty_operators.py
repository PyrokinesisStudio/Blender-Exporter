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
import mathutils
from bpy.types import Operator
from bpy.props import PointerProperty, StringProperty
#
opClasses = []

class OBJECT_OT_get_position(Operator):
    bl_label = "From( get position )"
    bl_idname = "world.get_position"
    bl_description = "Get the position of the sun from the selected lamp location"

    def execute(self, context):
        warning_message = sunPosAngle(mode="get", val="position")
        if warning_message:
            self.report({'WARNING'}, (warning_message))
            return {'CANCELLED'}
        else:
            return{'FINISHED'}
#            
opClasses.append(OBJECT_OT_get_position)

class OBJECT_OT_get_angle(Operator):
    bl_label = "From( get angle )"
    bl_idname = "world.get_angle"
    bl_description = "Get the position of the sun from selected lamp angle"

    def execute(self, context):
        warning_message = sunPosAngle(mode="get", val="angle")
        if warning_message:
            self.report({'WARNING'}, (warning_message))
            return {'CANCELLED'}
        else:
            return{'FINISHED'}
#
opClasses.append(OBJECT_OT_get_angle)

class OBJECT_OT_update_sun(Operator):
    bl_label = "From( update sun )"
    bl_idname = "world.update_sun"
    bl_description = "Update the position and angle of selected lamp in 3D View according to GUI values"

    def execute(self, context):
        warning_message = sunPosAngle(mode="update")
        if warning_message:
            self.report({'WARNING'}, (warning_message))
            return {'CANCELLED'}
        else:
            return{'FINISHED'}
#
opClasses.append(OBJECT_OT_update_sun)

def sunPosAngle(mode="get", val="position"):
    active_object = bpy.context.active_object
    scene = bpy.context.scene
    world = scene.world.bounty

    if active_object and active_object.type == "LAMP":

        if mode == "get":
            # get the position of the sun from selected lamp 'location'
            if val == "position":
                location = mathutils.Vector(active_object.location)

                if location.length:
                    point = location.normalized()
                else:
                    point = location.copy()

                world.bg_from = point
                return
            # get the position of the sun from selected lamps 'angle'
            elif val == "angle":
                matrix = mathutils.Matrix(active_object.matrix_local).copy()
                world.bg_from = (matrix[0][2], matrix[1][2], matrix[2][2])
                return

        elif mode == "update":

            # get gui from vector and normalize it
            bg_from = mathutils.Vector(world.bg_from).copy()
            if bg_from.length:
                bg_from.normalize()

            # set location
            sundist = mathutils.Vector(active_object.location).length
            active_object.location = sundist * bg_from

            # compute and set rotation
            quat = bg_from.to_track_quat("Z", "Y")
            eul = quat.to_euler()

            # update sun rotation and redraw the 3D windows
            active_object.rotation_euler = eul
            return

    else:
        return "No selected LAMP object in the scene!"



class TheBounty_OT_presets_ior_list(Operator):
    bl_idname = "material.set_ior_preset"
    bl_label = "IOR presets"
    index = bpy.props.FloatProperty()
    name = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        mat = context.material
        return mat.bounty.mat_type in {"glass", "rough_glass"}

    def execute(self, context):
        mat = context.material
        bpy.types.TheBounty_presets_ior_list.bl_label = self.name
        mat.bounty.IOR_refraction = self.index
        return {'FINISHED'}
#
opClasses.append(TheBounty_OT_presets_ior_list)
#

class Thebounty_OT_UpdateBlend(Operator):
    bl_idname = "material.parse_blend"
    bl_label = "Sync material slots or Fix empty selector"
    bl_description = "Sync material slot with selected materials or fix empty selected item"    
    
    @classmethod
    def poll(cls, context):
        material = context.object.active_material
        return material and (material.bounty.mat_type == "blend")
    #
    def execute(self, context):
        #
        obj = bpy.context.object
        mat = bpy.context.object.active_material
        #-------------------------
        # blend material one
        #-------------------------
        if mat.bounty.blendOne == "":
            if 'blendone' not in bpy.data.materials:
                bpy.data.materials.new('blendone')
            mat.bounty.blendOne = 'blendone'
        #       
        if mat.bounty.blendOne not in obj.data.materials:
            obj.data.materials.append(bpy.data.materials[mat.bounty.blendOne])
        #-------------------------
        # blend material two
        #-------------------------
        if mat.bounty.blendTwo == "":
            if 'blendtwo' not in bpy.data.materials:
                bpy.data.materials.new('blendtwo')
            mat.bounty.blendTwo = 'blendtwo'
        #
        if mat.bounty.blendTwo not in obj.data.materials:
            obj.data.materials.append(bpy.data.materials[mat.bounty.blendTwo])
        
        return {'FINISHED'}
# 
opClasses.append(Thebounty_OT_SyncBlendMaterial)
              
#
class Thebounty_OT_ParseSSS(Operator):
    bl_idname = "material.parse_sss"
    bl_label = "Apply SSS preset values"
    
    
    @classmethod
    def poll(cls, context):
        material = context.material
        return material and (material.bounty.mat_type == "translucent")
    #
    def execute(self, context):

        material = bpy.context.object.active_material
        mat = material.bounty
        scene = bpy.context.scene.bounty
        if scene.intg_light_method == 'pathtracing':
            exp = 1
        else:
            exp = 500
        #
        mat.exponent = exp        
        
        if mat.sss_presets=='cream':
            # colors
            material.diffuse_color = (0.987, 0.90, 0.73)
            mat.sssSigmaS = (.738, .547, .315)
            mat.sssSigmaA = (0.0002, 0.0028, 0.0163)
            mat.sssSpecularColor = (1.00, 1.00, 1.00)
            
            # values
            mat.sssIOR = 1.3
            mat.phaseFuction = 0.8
            mat.sssSigmaS_factor = 10.0
            mat.glossy_reflect = 0.6
            
        elif mat.sss_presets=='ketchup':
            # colors
            material.diffuse_color = (0.16, 0.01, 0.00)
            mat.sssSigmaS = (0.018, 0.007, 0.0034)
            mat.sssSigmaA = (0.061, 0.97, 1.45)
            mat.sssSpecularColor = (1.00, 1.00, 1.00)
            # values
            mat.sssIOR = 1.3
            mat.phaseFuction = 0.9
            mat.sssSigmaS_factor = 10.0
            mat.glossy_reflect = 0.7       
        
        elif mat.sss_presets=='marble':
            material.diffuse_color = (0.83, 0.79, 0.75)
            mat.sssSigmaS = (0.219, 0.262, 0.300)
            mat.sssSigmaA = (0.0021, 0.0041, 0.0071)
            mat.sssSpecularColor = (1.00, 1.00, 1.00)
            # values
            mat.sssIOR = 1.5
            mat.phaseFuction = -0.25
            mat.sssSigmaS_factor = 10.0
            mat.glossy_reflect = 0.7
            
        elif mat.sss_presets=='milkskimmed':
            # colors
            material.diffuse_color = (0.81, 0.81, 0.69)
            mat.sssSigmaS = (0.070, 0.122, 0.190)
            mat.sssSigmaA = (0.81, 0.81, 0.68)
            mat.sssSpecularColor = (1.00, 1.00, 1.00)
            # values
            mat.sssIOR = 1.3
            mat.phaseFuction = 0.8
            mat.sssSigmaS_factor = 10.0
            mat.glossy_reflect = 0.8
            
        elif mat.sss_presets=='milkwhole':
            # colors
            material.diffuse_color = (0.90, 0.88, 0.76)
            mat.sssSigmaS = (0.255, 0.321, 0.377)
            mat.sssSigmaA = (0.011, 0.0024, 0.014)
            mat.sssSpecularColor = (1.00, 1.00, 1.00)
            # values
            mat.sssIOR = 1.3
            mat.phaseFuction = 0.9
            mat.sssSigmaS_factor = 10.0
            mat.glossy_reflect = 0.8
            
        elif mat.sss_presets=='potato':
            # colors
            material.diffuse_color = (0.77, 0.62, 0.21)
            mat.sssSigmaS = (0.068, 0.070, 0.055)
            mat.sssSigmaA = (0.0024, 0.0090, 0.12)
            mat.sssSpecularColor = (1.00, 1.00, 1.00)
    
            # values
            mat.sssIOR = 1.3
            mat.phaseFuction = 0.8
            mat.sssSigmaS_factor = 10.0
            mat.glossy_reflect = 0.5
            
        elif mat.sss_presets=='skinbrown': #skin1
            # colors
            material.diffuse_color = (0.44, 0.22, 0.13)
            mat.sssSigmaS = (0.074, 0.088, 0.101)
            mat.sssSigmaA = (0.032, 0.17, 0.48)
            mat.sssSpecularColor = (1.00, 1.00, 1.00)
            # values
            mat.glossy_reflect = 0.5
            mat.sssSigmaS_factor = 10.0
            mat.phaseFuction = 0.8
            mat.sssIOR = 1.3
            
        elif mat.sss_presets=='skinpink':
            #
            material.diffuse_color = (0.63, 0.44, 0.34)
            mat.sssSigmaS = (0.109, 0.159, 0.179) # *10
            mat.sssSigmaA = (0.013, 0.070, 0.145)
            mat.sssSpecularColor = (1.00, 1.00, 1.00)
            #
            mat.glossy_reflect = 0.5
            mat.sssSigmaS_factor = 10.0
            mat.phaseFuction = 0.8
            mat.sssIOR = 1.3
            
        elif mat.sss_presets=='skinyellow':
            # colors
            material.diffuse_color = (0.64, 0.42, 0.27)
            mat.sssSigmaS = (0.48, 0.17, 0.10)
            mat.sssSigmaA = (0.64, 0.42, 0.27)
            mat.sssSpecularColor = (1.00, 1.00, 1.00)
            # values
            mat.sssIOR = 1.3
            mat.phaseFuction = 0.8
            mat.sssSigmaS_factor = 10.0
            mat.glossy_reflect = 0.5
        
        elif mat.sss_presets=='custom':
            # colors
            material.diffuse_color = mat.diff_color
            mat.sssSigmaS = mat.sssSigmaS
            mat.sssSigmaA = mat.sssSigmaA
            mat.sssSpecularColor = mat.sssSpecularColor
            # values
            mat.sssIOR = mat.sssIOR
            mat.phaseFuction = mat.phaseFuction
            mat.sssSigmaS_factor = mat.sssSigmaS_factor
            mat.glossy_reflect = mat.glossy_reflect
            
            
        return {'FINISHED'}
      
#
opClasses.append(Thebounty_OT_ParseSSS)

#-------------------------------------------
# Add support for use ibl files
#-------------------------------------------
import re, os

class Thebounty_OT_ParseIBL(Operator):
    bl_idname = "world.parse_ibl"
    bl_label = "Parse IBL"
    iblValues = {}
    ''' TODO:
    - test paths on linux systems.
    - add support for relative paths.
    - solve the question about packed ibl files inside the .blend 
    '''
    
    @classmethod
    def poll(cls, context):
        world = context.world
        return world and (world.bounty.bg_type == "textureback")
    #
    def execute(self, context):
        world = context.world.bounty
        scene = context.scene
        file = world.ibl_file
        filePath = bpy.path.abspath(world.ibl_file)
        filePath = os.path.realpath(filePath)
        filePath = os.path.normpath(filePath)
        # parse..
        self.iblValues = self.parseIbl(filePath)
        iblFolder = os.path.dirname(filePath) 
        #print(iblFolder)
        worldTexture = scene.world.active_texture
        if worldTexture.type == "IMAGE" and (worldTexture.image is not None):
            evfile = self.iblValues.get('EVfile')
            newval = os.path.join(iblFolder, evfile) 
            worldTexture.image.filepath = newval
        
        return {'FINISHED'}
    
    #---------------------
    # some parse helpers
    #---------------------
    def parseValue(self, line, valueType):
        items = re.split(" ", line)
        item = items[2]  # items[1] is '='
        if valueType == 2:
            ext = (len(item) - 2)
            return item[1:ext]            
        elif valueType == 1:
            return int(item)
        elif valueType == 0:
            return float(item)
    
    #---------------------
    # parse .ibl file
    #---------------------
    def parseIbl(self, filename):
        f = open(filename, 'r')
        line = f.readline()
        while line != "":
            line = f.readline()
            if line.startswith('ICOfile'):
                self.iblValues['ICOfile']= self.parseValue(line, 2) # string
            #
            if line.startswith('PREVIEWfile'):
                self.iblValues['PREVIEWfile']= self.parseValue(line, 2) # string          
            
            #[Background]
            if line.startswith('BGfile'):
                self.iblValues['BGfile']= self.parseValue(line, 2) # string
            #
            if line.startswith('BGheight'):
                self.iblValues['BGheight']= self.parseValue(line, 1) # integer
            
            # [Enviroment]
            if line.startswith('EVfile'):
                self.iblValues['EVfile']= self.parseValue(line, 2) # string
            #
            if line.startswith('EVheight'):
                self.iblValues['EVheight']= self.parseValue(line, 1) # integer
            #
            if line.startswith('EVgamma'):
                self.iblValues['EVgamma']= self.parseValue(line, 0) # float
            
            # [Reflection]   
            if line.startswith('REFfile'):
                self.iblValues['REFfile']= self.parseValue(line, 2) # string
                
            if line.startswith('REFheight'):
                self.iblValues['REFheight']= self.parseValue(line, 1) # integer
                
            if line.startswith('REFgamma'):
                self.iblValues['REFgamma']= self.parseValue(line, 0) # float
                
            # [Sun]
            if line.startswith('SUNcolor'):
                self.iblValues['SUNcolor'] = (255,255,245)
                
            if line.startswith('SUNmulti'):
                self.iblValues['SUNmulti']= self.parseValue(line, 0) # float
                
            if line.startswith('SUNu'):
                self.iblValues['SUNu']= self.parseValue(line, 0) # float
                
            if line.startswith('SUNv'):
                self.iblValues['SUNv']= self.parseValue(line, 0) # float
                     
        f.close()
        return self.iblValues
    
opClasses.append(Thebounty_OT_ParseIBL)

def register():
    for cls in opClasses:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in opClasses:
        bpy.utils.unregister_class(cls)

