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

#-------------------------------------------
# Add support for use ibl files
#-------------------------------------------
import re, os
   
class Thebounty_OT_ParseIBL(Operator):
    bl_idname = "world.parse_ibl"
    bl_label = "Parse IBL"
    iblValues = {}
    
    @classmethod
    def poll(cls, context):
        world = context.world
        return world and (world.bounty.bg_type == "Texture")
    #
    def execute(self, context):
        world = context.world.bounty
        scene = context.scene
        file = world.ibl_file
        # parse..
        self.iblValues = self.parseIbl(file)
        # maybe dirname only work with Win OS ??
        # TODO: test on linux OS
        iblFolder = os.path.dirname(file) 
        print(iblFolder)
        worldTexture = scene.world.active_texture
        if worldTexture.type == "IMAGE" and (worldTexture.image is not None):
            evfile = self.iblValues.get('EV')
            newval = os.path.join(iblFolder, evfile) 
            worldTexture.image.filepath = newval #self.iblValues.get('EV')
        
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
            if line[:7] == 'ICOfile':
                self.parseValue(line, 2) # string
            #
            if line[:11] == 'PREVIEWfile':
                self.iblValues['PRE']= self.parseValue(line, 2) #PREVIEWfile          
            #
            if line[:6] == 'BGfile':
                self.iblValues['BG']= self.parseValue(line, 2) #BGfile
            #
            if line[:8] == 'BGheight':
                self.parseValue(line, 1) # integer
            #
            if line[:6] == 'EVfile':
                self.iblValues['EV']= self.parseValue(line, 2) #EVfile
            #
            if line[:8] == 'EVheight':
                self.parseValue(line, 1) # integer
            #
            if line[:7] == 'EVgamma':
                self.parseValue(line, 0) # float
                
            if line[:7] == 'REFfile':
                self.iblValues['REF']= self.parseValue(line, 2) #REFfile
                
            if line[:9] == 'REFheight':
                self.parseValue(line, 1) # integer
                
            if line[:8] == 'REFgamma':
                self.parseValue(line, 0) # float
                     
        f.close()
        return self.iblValues
# test

def register():
    bpy.utils.register_class(OBJECT_OT_get_position)
    bpy.utils.register_class(OBJECT_OT_get_angle)
    bpy.utils.register_class(OBJECT_OT_update_sun)
    bpy.utils.register_class(TheBounty_OT_render_view)
    bpy.utils.register_class(TheBounty_OT_render_animation)
    bpy.utils.register_class(TheBounty_OT_render_still)
    bpy.utils.register_class(TheBounty_OT_presets_ior_list)
    bpy.utils.register_class(Thebounty_OT_ParseIBL)
    

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_get_position)
    bpy.utils.unregister_class(OBJECT_OT_get_angle)
    bpy.utils.unregister_class(OBJECT_OT_update_sun)
    bpy.utils.unregister_class(TheBounty_OT_render_view)
    bpy.utils.unregister_class(TheBounty_OT_render_animation)
    bpy.utils.unregister_class(TheBounty_OT_render_still)
    bpy.utils.unregister_class(TheBounty_OT_presets_ior_list)
    bpy.utils.unregister_class(Thebounty_OT_ParseIBL)

