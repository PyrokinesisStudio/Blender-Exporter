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
import mathutils
from bpy.types import Operator
from bpy.props import PointerProperty, StringProperty

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
        material = context.material
        return material and (material.bounty.mat_type == "blend")
    #
    def execute(self, context):
        obj = context.object
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
    
opClasses.append(Thebounty_OT_UpdateBlend)            
#-------------------------------------------
# Add support for use ibl files
#-------------------------------------------
import re

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
            material.diffuse_color = material.diffuse_color
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
        world = context.scene.world
        return world and (world.bounty.bg_type == "textureback")
    #
    def isIBL(self, file):
        
        ibl = (file !="" and 
               os.path.exists(file) and 
               (file.endswith('.ibl') or file.endswith('.IBL'))
        )
        return ibl
    
    #
    def execute(self, context):
        world = context.scene.world
        scene = context.scene
        file = world.bounty.ibl_file
        if not self.isIBL(file):
            return {'CANCELLED'}
        # parse..
        self.iblValues = self.parseIbl(file)
        iblFolder = os.path.dirname(file) 
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
            
            # [Background]
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

# test
class Thebounty_OT_ParseIES(Operator):
    bl_idname = "lamp.parse_ies"
    bl_label = "Parse IES file"
    bl_description='Parse IES file to store data in scene'
    '''
    Parts of code are extract from "IES to Cycles" addon, by Lockal S.
    and modified by Pedro Alcaide, aka 'povmaniac'
    '''
    
    @classmethod
    def poll(self, context):
        lamp = context.lamp        
        return lamp and (lamp.type == 'SPOT' and lamp.bounty.use_ies)
    
    def execute(self, context):
        #
        lamp = context.lamp
        # allow relative path
        iesfile = bpy.path.abspath(lamp.bounty.ies_file)
        iesfile = os.path.realpath(iesfile)
        iesfile = os.path.normpath(iesfile)
        #print('file..', iesfile)
        
        allow_ies = ( os.path.exists(iesfile) and
            (iesfile.endswith('.ies') or iesfile.endswith('.IES')))
        
        if not allow_ies:
            self.report({'ERROR'}, "Missing or invalid IES file")
            return {'CANCELLED'}
        
        self.parseIES(iesfile)
            
        return {'FINISHED'}
    
    def simple_interp(self, k, x, y):
        for i in range(len(x)):
            if k == x[i]:
                return y[i]
            elif k < x[i]:
                return y[i] + (k - x[i]) * (y[i - 1] - y[i]) / (x[i - 1] - x[i])
            
    def parseIES(self, filename):
        #(log, filename, generate_rig, multiplier, image_format, color_temperature):
        INFO = "INFO: IES Parser:"
        multiplier = 1        
        version_table = {
            'IESNA:LM-63-1986': 1986,
            'IESNA:LM-63-1991': 1991,
            'IESNA91': 1991,
            'IESNA:LM-63-1995': 1995,
            'IESNA:LM-63-2002': 2002,
        }
        
        name = os.path.splitext(os.path.split(filename)[1])[0]
    
        file = open(filename, 'rt', encoding='cp1252')
        content = file.read()
        file.close()
        s, content = content.split('\n', 1)
    
        if s in version_table:
            version = version_table[s]
        else:
            self.report({'INFO'}, "IES file does not specify any version")
            version = None
    
        keywords = dict()
    
        while content and not content.startswith('TILT='):
            s, content = content.split('\n', 1)
    
            if s.startswith('['):
                endbracket = s.find(']')
                if endbracket != -1:
                    keywords[s[1:endbracket]] = s[endbracket + 1:].strip()
    
        s, content = content.split('\n', 1)
    
        if not s.startswith('TILT'):
            self.report({'ERROR'}, "TILT keyword not found, check your IES file")
            return {'CANCELLED'}
    
        # fight against ill-formed files
        file_data = content.replace(',', ' ').split()
    
        lamps_num = int(file_data[0])
        print(INFO, 'Number of lamps: ', lamps_num)
        if lamps_num != 1:
            self.report({'INFO'}, "Only 1 lamp is supported, %d in IES file" % lamps_num)
    
        lumens_per_lamp = float(file_data[1])
        print(INFO, 'Lumens per lamp: ', lumens_per_lamp)
        
        candela_mult = float(file_data[2])
        candela_mult *= 0.001
        print(INFO, 'Candela multiplier (kcd): ', candela_mult)
    
        v_angles_num = int(file_data[3])
        print(INFO, 'Vertical Angles: ', v_angles_num)
        
        h_angles_num = int(file_data[4])
        print(INFO, 'Horizontal Angles: ', h_angles_num)
        
        if not v_angles_num or not h_angles_num:
            self.report({'ERROR'}, "TILT keyword not found, check your IES file")
            return {'CANCELLED'}
    
        photometric_type = int(file_data[5])
        print(INFO, 'Photometric type: ', photometric_type)
        
        units_type = int(file_data[6])
        print(INFO, 'Units Type: ', units_type)
        
        if units_type not in [1, 2]:
            self.report({'INFO'}, "Units type should be either 1 (feet) or 2 (meters)")
    
        width, length, height = map(float, file_data[7:10])
        print(INFO, '(Width, Length, Height) = (', width ,', ', length, ', ', height ,')')
        #
        geoType = "Unknown light type!!"

        if (width ==   0.0 and length == 0.0 and height == 0.0):  geoType = "Point Light"    
        elif (width >= 0.0 and length >= 0.0 and height >= 0.0):  geoType = "Rectangular Light"    
        elif (width <  0.0 and length == 0.0 and height == 0.0):  geoType = "Circular Light"    
        elif (width <  0.0 and length == 0.0 and height <  0.0):  geoType = "Shpere Light"    
        elif (width <  0.0 and length == 0.0 and height >= 0.0):  geoType = "Vertical Cylindric Light"    
        elif (width == 0.0 and length >= 0.0 and height <  0.0):  geoType = "Horizontal Cylindric Light (Along width)"    
        elif (width >= 0.0 and length == 0.0 and height <  0.0):  geoType = "Horizontal Cylindric Light (Along length)"    
        elif (width <  0.0 and length >= 0.0 and height >= 0.0):  geoType = "Elipse Light (Along width)"    
        elif (width >= 0.0 and length <  0.0 and height >= 0.0):  geoType = "Elipse Light (Along length)"    
        elif (width <  0.0 and length >= 0.0 and height <  0.0):  geoType = "Elipsoid Light (Along width)"    
        elif (width >= 0.0 and length <  0.0 and height <  0.0):  geoType = "Elipsoid Light (Along length)"
        
        print(INFO, 'Lamp Geometry: ', geoType)    
    
        ballast_factor = float(file_data[10])
        print(INFO, 'Ballast Factor: ', ballast_factor)
    
        future_use = float(file_data[11])
        print(INFO, 'Ballast-Lamp Photometric Factor: ', future_use)
        if future_use != 1.0:
            self.report({'INFO'}, "Invalid future use field")
    
        input_watts = float(file_data[12])
        print(INFO, 'Input Watts: ', input_watts)
    
        v_angs = [float(s) for s in file_data[13:13 + v_angles_num]]
        h_angs = [float(s) for s in file_data[13 + v_angles_num:
                                              13 + v_angles_num + h_angles_num]]
    
        if v_angs[0] == 0 and v_angs[-1] == 90:
            lamp_cone_type = 'TYPE90'
        elif v_angs[0] == 0 and v_angs[-1] == 180:
            lamp_cone_type = 'TYPE180'
        else:
            self.report({'INFO'}, "Lamps with vertical angles (%d-%d) are not supported" % (v_angs[0], v_angs[-1]))
            lamp_cone_type = 'TYPE180'
    
    
        if len(h_angs) == 1 or abs(h_angs[0] - h_angs[-1]) == 360:
            lamp_h_type = 'TYPE360'
        elif abs(h_angs[0] - h_angs[-1]) == 180:
            lamp_h_type = 'TYPE180'
        elif abs(h_angs[0] - h_angs[-1]) == 90:
            lamp_h_type = 'TYPE90'
        else:
            self.report({'INFO'}, "Lamps with horizontal angles (%d-%d) are not supported" % (h_angs[0], h_angs[-1]))
            lamp_h_type = 'TYPE360'
            
        # print(h_angs, lamp_h_type)
    
        # read candela values
        offset = 13 + len(v_angs) + len(h_angs)
        candela_num = len(v_angs) * len(h_angs)
        candela_values = [float(s) for s in file_data[offset:offset + candela_num]]
    
        # reshape 1d array to 2d array
        candela_2d = list(zip(*[iter(candela_values)] * len(v_angs)))
        
        # check if angular offsets are the same
        v_d = [v_angs[i] - v_angs[i - 1] for i in range(1, len(v_angs))]
        h_d = [h_angs[i] - h_angs[i - 1] for i in range(1, len(h_angs))]
    
        v_same = all(abs(v_d[i] - v_d[i - 1]) < 0.001 for i in range(1, len(v_d)))
        h_same = all(abs(h_d[i] - h_d[i - 1]) < 0.001 for i in range(1, len(h_d)))
    
        if not v_same:
            vmin, vmax = v_angs[0], v_angs[-1]
            divisions = int((vmax - vmin) / max(1, min(v_d)))
            step = (vmax - vmin) / divisions
    
            # Approximating non-uniform vertical angles with step = step
            new_v_angs = [vmin + i * step for i in range(divisions + 1)]
            new_candela_2d = [[self.simple_interp(ang, v_angs, line) for ang in new_v_angs] for line in candela_2d]
            #print('candela ', candela_2d)
            #print('new candela', new_candela_2d)
            v_angs = new_v_angs
            candela_2d = new_candela_2d
    
        if not h_same:
            self.report({'INFO'}, "Different offsets for horizontal angles!")
        #print('vangle: ', v_angs)    
        # normalize candela values
        maxval = max([max(row) for row in candela_2d])
        candela_2d = [[val / maxval for val in row] for row in candela_2d]
    
        # add extra left and right rows to bypass cycles repeat of uv coordinates
        candela_2d = [[line[0]] + list(line) + [line[-1]] for line in candela_2d]
        
        if len(candela_2d) > 1:
            candela_2d = [candela_2d[0]] + candela_2d + [candela_2d[-1]]
    
        # flatten 2d array to 1d
        candela_values = [y for x in candela_2d for y in x]
        #print('candela ', candela_values)
        
        intensity = max(500, min(maxval * multiplier * candela_mult, 5000))
        #print('intensity ', intensity)
        
        return {'FINISHED'}

opClasses.append(Thebounty_OT_ParseIES)

def register():
    for cls in opClasses:
        bpy.utils.register_class(cls)
    

def unregister():
    for cls in opClasses:
        bpy.utils.unregister_class(cls)

