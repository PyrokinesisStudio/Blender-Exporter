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

import bpy, os
from bpy.path import abspath, clean_name
from os.path import realpath, normpath, basename


class exportWorld:
    def __init__(self, interface):
        self.yi = interface

    def setEnvironment(self, scene):
        yi = self.yi
        
        # init..
        world = bpy.context.scene.world
        bg_type = "constant"
        bgColor = (0.0, 0.0, 0.0)
        useIBL = False
        iblSamples = 16
        bgPower = 1 
        
        if scene.world:
            # exporter properties
            world = scene.world.bounty
            bg_type = world.bg_type
            bgColor = world.bg_single_color
            useIBL = world.bg_use_ibl
            iblSamples = world.bg_ibl_samples
            bgPower = world.bg_power
            with_caustic = world.bg_with_caustic
            with_diffuse = world.bg_with_diffuse
            
        yi.paramsClearAll()

        if bg_type == 'textureback':
            #
            worldTexture = None
            if scene.world.active_texture is not None:
                worldTexture = scene.world.active_texture
                
                self.yi.printInfo("World Texture, name: {0}".format(worldTexture.name))

                if worldTexture.type == "IMAGE" and (worldTexture.image is not None):
                    #
                    image_file = ''
                    if worldTexture.image.packed_file:
                        # is packed but too exists on disk..
                        if not os.path.exists(abspath(worldTexture.image.filepath)):
                            worldTexture.image.unpack(method='WRITE_LOCAL')
                            yi.printInfo("Image file unpacked to: {0}".format(abspath(worldTexture.image.filepath)))
                        image_file = abspath(worldTexture.image.filepath)
                            
                    else:
                        # not packed..
                        image_file = abspath(worldTexture.image.filepath)
                    #
                    image_file = realpath(image_file)
                    image_file = normpath(image_file)                        
                    
                    yi.paramsSetString("filename", image_file)
                    
                    # image interpolate
                    yi.paramsSetString("interpolate", worldTexture.interpolation_type)
                    yi.paramsSetString("type", "image")
                    yi.createTexture("world_texture")

                    # Background settings..
                    yi.paramsClearAll()
                    #
                    worldMappingCoord = "angular"
                    if world.bg_mapping_type == "SPHERE":
                        worldMappingCoord = "spherical"
                        
                    yi.paramsSetString("mapping", worldMappingCoord)                    
                        
                    yi.paramsSetString("type", "textureback")
                    yi.paramsSetString("texture", "world_texture")
                    yi.paramsSetBool("ibl", world.bg_use_ibl)
                    yi.paramsSetBool("with_caustic", world.bg_with_caustic)
                    yi.paramsSetBool("with_diffuse", world.bg_with_diffuse)
                    yi.paramsSetInt("ibl_samples", world.bg_ibl_samples)
                    yi.paramsSetFloat("power", world.bg_power)
                    yi.paramsSetFloat("rotation", world.bg_rotation)
                else:
                    self.yi.printWarning("World Texture, name: {0} is not valid format".format(worldTexture.name))
            else:
                self.yi.printWarning('texture background not found')
            
        elif bg_type == 'gradientback':
            c = world.bg_horizon_color
            yi.paramsSetColor("horizon_color", c[0], c[1], c[2])

            c = world.bg_zenith_color
            yi.paramsSetColor("zenith_color", c[0], c[1], c[2])

            c = world.bg_horizon_ground_color
            yi.paramsSetColor("horizon_ground_color", c[0], c[1], c[2])

            c = world.bg_zenith_ground_color
            yi.paramsSetColor("zenith_ground_color", c[0], c[1], c[2])

            yi.paramsSetFloat("power", world.bg_power)
            yi.paramsSetBool("ibl", world.bg_use_ibl)
            yi.paramsSetInt("ibl_samples", world.bg_ibl_samples)

        elif bg_type in {'sunsky', "darksky"}:
            #
            if bg_type == 'sunksky':
                yi.paramsSetFloat("turbidity", world.bg_turbidity)
            
            #-------------------------
            # specific sunsky2 values
            #-------------------------            
            if bg_type == 'darksky':
                yi.paramsSetFloat("turbidity", world.bg_ds_turbidity)
                yi.paramsSetFloat("altitude", world.bg_dsaltitude)
                yi.paramsSetFloat("bright", world.bg_dsbright)
                yi.paramsSetBool("night", world.bg_dsnight)
                yi.paramsSetFloat("exposure", world.bg_exposure)
                yi.paramsSetString("color_space", world.bg_color_space)
                if world.bg_background_light:
                    yi.paramsSetBool("with_caustic", world.bg_with_caustic)
                    yi.paramsSetBool("with_diffuse", world.bg_with_diffuse)
            #---------------
            # common values
            #---------------
            f = world.bg_from
            yi.paramsSetPoint("from", f[0], f[1], f[2])
            yi.paramsSetFloat("a_var", world.bg_a_var)
            yi.paramsSetFloat("b_var", world.bg_b_var)
            yi.paramsSetFloat("c_var", world.bg_c_var)
            yi.paramsSetFloat("d_var", world.bg_d_var)
            yi.paramsSetFloat("e_var", world.bg_e_var)            
            yi.paramsSetBool("add_sun", world.bg_add_sun)
            yi.paramsSetFloat("sun_power", world.bg_sun_power)
            yi.paramsSetBool("background_light", world.bg_background_light)
            yi.paramsSetFloat("power", world.bg_power)            
            yi.paramsSetInt("light_samples", world.bg_light_samples)           

        else:
            yi.paramsSetColor("color", bgColor[0], bgColor[1], bgColor[2])
            yi.paramsSetBool("ibl", useIBL)
            yi.paramsSetInt("ibl_samples", iblSamples)
            yi.paramsSetFloat("power", bgPower)
        #
        yi.paramsSetString("type", bg_type)
        yi.createBackground("world_background")
        self.yi.printInfo("Exporting World, type: {0}".format(bg_type))
        
        return True
