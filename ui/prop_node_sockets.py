#---------- BEGIN GPL LICENSE BLOCK ------------------------------------------#
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
#  or visit https://www.fsf.org for more info.
#
#---------- END GPL LICENSE BLOCK --------------------------------------------#

# <pep8 compliant>

#-------------------------------------------------
# This file is part of TheBounty Blender exporter
# Created by povmaniac at 20/01/15
#-------------------------------------------------
import bpy
from bpy.types import Node, NodeSocket
from bpy.props import (FloatProperty, 
                       FloatVectorProperty, 
                       StringProperty, 
                       BoolProperty,
                       EnumProperty)

from ..prop.tby_material import TheBountyMaterialProperties as MatProperty
from ..prop.tby_light import TheBountyLightProperties as LightProperty


color_socket = (0.9, 0.9, 0.0, 1.0)
float_socket = (0.63, 0.63, 0.63, 1.0)
enum_sockect = (0.0, 0.0, 1.0, 1.0)
#
bounty_socket_class=[]

glossy_layers = ["diffuse_shader", "glossy_shader", "glossy_reflect_shader", "bump_shader"]
glass_layers = ["mirror_color_shader", "bump_shader"]
shiny_layers = ["diffuse_shader", "mirror_color_shader", "transparency_shader", "translucency_shader", "mirror_shader", "bump_shader"]
translucent_layers = ["diffuse_shader", "glossy_shader", "glossy_reflect_shader", "bump_shader", "sigmaA_shader", "sigmaS_shader"]



        
''' Base class for node sockets.
'''   
class TheBountyNodeSocket():
    #
    def getParams(self):
        pass
                
#
bounty_socket_class.append(TheBountyNodeSocket)

class light_color_socket(NodeSocket, TheBountyNodeSocket):
    #-----------------------
    # Light color socket 
    #-----------------------
    
    bl_idname = 'color'
    bl_label = 'Color Socket'
    params = {}
    color = FloatVectorProperty(
            name="Light color",
            description="Diffuse albedo light color",
            subtype='COLOR',
            min=0.0, max=1.0,
            default=(0.8, 0.8, 0.8),
    )
    energy = LightProperty.energy
    
    # useful helper functions
    def default_value_get(self):
        return self.color
    
    def default_value_set(self, value):
        self.color = value
        
    default_value =  bpy.props.FloatVectorProperty( subtype='COLOR', get=default_value_get, set=default_value_set)
    
    #         
    def draw(self, context, layout, node, text):
        col = layout.column()
        #                     
        col.prop(self, "color", text= 'Color' )
        col.prop(self, "energy", text="Power", slider=True)
     
    #
    def draw_color(self, context, node):
        return (color_socket)

#
bounty_socket_class.append(light_color_socket)


''' diffuse color and reflection socket 
'''
class diffuse_color_socket(NodeSocket, TheBountyNodeSocket): 
    bl_idname = 'diffuse_color'
    bl_label = 'Color Socket'
    matParams = {}
    texParams = {}
    validNodes = ['Image', 'Clouds']
    
    #properties..
    diff_color = MatProperty.diff_color
    diffuse_reflect = MatProperty.diffuse_reflect
    
    # useful helper functions
    def default_value_get(self):
        return self.diff_color
    
    def default_value_set(self, value):
        self.diff_color = value
        
    default_value =  bpy.props.FloatVectorProperty( subtype='COLOR', get=default_value_get, set=default_value_set)
    
    #         
    def draw(self, context, layout, node, text):
        col = layout.column()
        label = 'Diffuse Color'
        if self.is_linked: # and not self.is_output:
            label = 'Diffuse color layer'
        #                     
        col.prop(self, "diff_color", text= label )
        col.prop(self, "diffuse_reflect", text="Diffuse Reflection", slider=True)
    
    def getParams(self):
        self.matParams['color']= [c for c in self.diff_color]
        self.matParams['diffuse_reflect']= self.diffuse_reflect
        # test
        self.matParams['DiffuseLayer']= None
        self.matParams['diffuse_shader']= None
        if self.is_linked:
            linked_node = self.links[0].from_node
            if linked_node.bl_label in self.validNodes:
                self.matParams['diffuse_shader']='diff_layer'
                self.matParams['DiffuseLayer']= linked_node.getParams()
        
        return self.matParams
    #
    def draw_color(self, context, node):
        return (color_socket)

#
bounty_socket_class.append(diffuse_color_socket)

#-------------------------------------------
# Emission socket for shinydiffuse material
#-------------------------------------------
class emitt_socket(NodeSocket, TheBountyNodeSocket):
    bl_idname = 'emittance'
    bl_label = 'Emission Socket'
    params={}  
    
    emittance = MatProperty.emittance
    
    # get/set default values
    def default_value_get(self):
        return self.emittance
    
    def default_value_set(self, value):
        self.emittance = value
    #
    default_value = bpy.props.FloatProperty( get=default_value_get, set=default_value_set)
    #    
    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "emittance", slider=True)    
    #
    def exportValues(self):
        self.params['emit']=  self.emittance
        if self.is_linked:
            linked_node = self.links[0].from_node
            try:
                linked_node.exportValues(self)
            except:
                pass
        #
        return self.params
            
    #
    def draw_color(self, context, node):
        return (float_socket)    
#
bounty_socket_class.append(emitt_socket)

#-------------------------------------
# BRDF socket
#-------------------------------------
class brdf_socket(NodeSocket, TheBountyNodeSocket):
    bl_idname = 'brdf'
    bl_label = 'BRDF Socket' 
    params={}   
    
    #brdf_type = MatProperty.brdf_type
    sigma = MatProperty.sigma
    
    enum_reflectance_mode = [
        ('lambert', "Lambert", "Reflectance Model",0),
        ('oren_nayar', "Oren-Nayar", "Reflectance Model",1),
        
    ]
    # small trick..
    enum_reflectance_default_mode = (('lambert', "Lambert", "Reflectance Model"),)
        
    # default values for a socket
    def default_value_get(self):
        return self.brdf_type
    
    def default_value_set(self, value):
        self.brdf_type = 'lambert'
        
    brdf_type = EnumProperty(
            name="BRDF",
            description="Reflectance model",
            items=enum_reflectance_mode,
            default='lambert',
    )        
    default_value =  EnumProperty(items=enum_reflectance_mode, set=default_value_set)
    #
    def draw(self, context, layout, node, text):
        col = layout.box()
        if self.is_linked:
            col.label("Reflectance model")
        else:
            col.prop(self, "brdf_type")
            col.prop(self, "sigma", text='Sigma', slider=True)
    #
    def exportValues(self):
        self.params['brdf_type']= self.brdf_type
        self.params['sigma']= self.sigma
        if self.is_linked:
            linked_node = self.links[0].from_node
            try:
                linked_node.exportValues(self)
            except:
                print('Not export values on node')
        return self.params
    #
    def draw_color(self, context, node):
        return (float_socket)
#
bounty_socket_class.append(brdf_socket)

'''
class sigma_socket(NodeSocket):
    bl_idname = 'sigma'
    bl_label = 'Sigma Socket'
    hide_value = True 
    
    sigma = MatProperty.sigma
    
    # default values for socket
    def default_value_get(self):
        return self.sigma
    
    def default_value_set(self, value):
        self.sigma = value
        
    default_value =  FloatProperty( get=default_value_get, set=default_value_set)
    #
    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "sigma", slider=True)    
    #
    def draw_color(self, context, node):
        return (float_socket)
#
bounty_socket_class.append(sigma_socket)
'''
#-------------------------------------
# translucency
#-------------------------------------
class translucency_socket(NodeSocket, TheBountyNodeSocket):
    bl_idname = 'translucency'
    bl_label = 'Translucency Socket'
    params={} 
    
    translucency = MatProperty.translucency
    #transmit = MatProperty.transmit_filter
    
    # default values for socket
    def default_value_get(self):
        return self.translucency
    
    def default_value_set(self, value):
        self.translucency = value
        
    default_value =  bpy.props.FloatProperty( get=default_value_get, set=default_value_set)
    #    
    def draw(self, context, layout, node, text):
        col = layout.column()
        if self.is_linked:
            col.label('Translucency Layer')
        else:
            col.prop(self, "translucency", slider=True)
        #col.prop(self, "transmit", slider=True)    
    #
    def exportValues(self):
        self.params['translucency']= self.translucency
        #self.params['transmit']= self.transmit
        if self.is_linked:
            linked_node = self.links[0].from_node
            try:
                linked_node.exportValues(self)
            except:
                print('Not export values on node')
        return self.params
    # 
    def draw_color(self, context, node):
        return (float_socket)
#
bounty_socket_class.append(translucency_socket)

#----------------------------------------------------------
# transparency
#----------------------------------------------------------   
class transparency_socket(NodeSocket, TheBountyNodeSocket):
    bl_idname = 'transparency'
    bl_label = 'Transparency Socket'
    matParams = {}
    validNodes = ['Image', 'Clouds'] 
    
    transparency = MatProperty.transparency
    
    # default values for socket
    def default_value_get(self):
        return self.transparency
    
    def default_value_set(self, value):
        self.transparency = value
    
    default_value =  bpy.props.FloatProperty( get=default_value_get, set=default_value_set)
            
    # draw socket
    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label('Transparency Layer')
        else:
            layout.prop(self, "transparency", slider=True)    
    #
    def getParams(self):
        self.matParams['transparency']= self.transparency
        # test
        self.matParams['TransparencyLayer']= None
        self.matParams['transparency_shader']= None
        if self.is_linked:
            linked_node = self.links[0].from_node
            if linked_node.bl_label in self.validNodes:
                self.matParams['transparency_shader']='transp_layer'
                self.matParams['TransparencyLayer']= linked_node.getParams()
        
        return self.matParams
                
    #
    def draw_color(self, context, node):
        return (float_socket)
#
bounty_socket_class.append(transparency_socket)

class transmit_socket(NodeSocket, TheBountyNodeSocket):
    bl_idname = 'transmit'
    bl_label = 'Transmittance Socket'  
    
    transmit_filter = MatProperty.transmit_filter
    
    # default values for socket
    def default_value_get(self):
        return self.transmit_filter
    
    def default_value_set(self, value):
        self.transmit_filter = value
    
    default_value =  bpy.props.FloatProperty( get=default_value_get, set=default_value_set)
    
    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "transmit_filter", slider=True) 
    #
    def draw_color(self, context, node):
        return (float_socket)
#
bounty_socket_class.append(transmit_socket)

#----------------------------------------------------------
# specular reflect sockect
#----------------------------------------------------------
class specular_reflect_socket(NodeSocket):
    bl_idname = 'specular'
    bl_label = 'Specular Socket'
    
    specular_reflect = MatProperty.specular_reflect
    
    # default values for socket's
    def default_value_get(self):
        return self.specular_reflect
    
    def default_value_set(self, value):
        self.specular_reflect = value
    
    default_value =  bpy.props.FloatProperty( get=default_value_get, set=default_value_set)
    
    def draw(self, context, layout, node, text):
        col = layout.column()
        label ="Specular reflect"
        if self.is_linked:
            col.label("Specular reflect layer")
        else:
            col.prop(self, "specular_reflect", slider=True)     
    #
    def draw_color(self, context, node):
        return (float_socket)
#
bounty_socket_class.append(specular_reflect_socket)


#----------------------------------------------------------
# specular sockect
#----------------------------------------------------------
class specular_color_socket(NodeSocket, TheBountyNodeSocket):
    bl_idname = 'mirror'
    bl_label = 'Mirror Color Socket'
    params = {}
    
    mirror_color = MatProperty.mirror_color
    
    # default values for socket's
    def default_value_get(self):
        return self.mirror_color
    
    def default_value_set(self, value):
        self.mirror_color = value
    
    default_value =  bpy.props.FloatVectorProperty( subtype='COLOR', get=default_value_get, set=default_value_set)
    #        
    def draw(self, context, layout, node, text):
        col = layout.column()
        label="Specular color"
        if self.is_linked:
            label="Specular Color layer"
        col.prop(self, "mirror_color", text=label)
    #
    def exportValues(self):
        #
        self.params['mirror_color']= [c for c in self.mirror_color]
        
        if self.is_linked:
            linked_node = self.links[0].from_node
            try:
                linked_node.exportValues(self)
            except:
                print('Not export values on node')
        #
        return self.params
    #
    def draw_color(self, context, node):
        return (color_socket)
#
bounty_socket_class.append(specular_color_socket)

#----------------------------------------------------------
# glossy color and reflection sockets
#----------------------------------------------------------
class glossy_color_socket(NodeSocket, TheBountyNodeSocket):
    #-----------------------
    # Glossy color sockets 
    #-----------------------
    bl_idname = 'glossy_color'
    bl_label = 'Color Socket'
    params = {}
    
    glossy_color = MatProperty.glossy_color
    
    # useful helper functions
    def default_value_get(self):
        return self.glossy_color
    
    def default_value_set(self, value):
        self.glossy_color = value
        
    default_value =  bpy.props.FloatVectorProperty( subtype='COLOR', get=default_value_get, set=default_value_set)
    
    #         
    def draw(self, context, layout, node, text):
        col = layout.column()
        label = 'Glossy Color Layer' if self.is_linked else 'Glossy Color'            
        #                     
        col.prop(self, "glossy_color", text= label )
    #
    def exportValues(self):
        self.params['glossy_color']= [c for c in self.glossy_color]
        if self.is_linked:
            linked_node = self.links[0].from_node
            try:
                linked_node.exportValues(self)
            except:
                print('Not export values on node')
        #
        return self.params
    #
    def draw_color(self, context, node):
        return (color_socket)
#
bounty_socket_class.append(glossy_color_socket)

#--------------------------------------
# glossy reflect
#--------------------------------------
class glossy_reflect_socket(NodeSocket, TheBountyNodeSocket):
    bl_idname = 'glossy_reflect'
    bl_label = 'Reflection Socket'
    
    glossy_reflect = MatProperty.diffuse_reflect
    
    # helper property
    def default_value_get(self):
        return self.glossy_reflect
    
    def default_value_set(self, value):
        self.glossy_reflect  = value
        
    default_value =  bpy.props.FloatProperty( get=default_value_get, set=default_value_set)
    #    
    def draw(self, context, layout, node, text):
        #
        layout.prop(self, "glossy_reflect", text= 'Glossy Reflection', slider=True)
 
    #
    def draw_color(self, context, node):
        return (float_socket)
#
bounty_socket_class.append(glossy_reflect_socket)

class fresnel_socket(NodeSocket, TheBountyNodeSocket):
    bl_idname = "fresnel"
    bl_label = "Fresnel Socket"
    params ={} 
    
    fresnel_effect = MatProperty.fresnel_effect
    IOR_reflection = MatProperty.IOR_reflection
    
    # default values for socket's
    def default_value_get(self):
        return self.fresnel_effect
    
    def default_value_set(self, value):
        self.fresnel_effect = value
    
    default_value =  bpy.props.BoolProperty( get=default_value_get, set=default_value_set)
    
    def draw(self, context, layout, node, text):
        col = layout.column()
        if self.is_linked:
            col.label(text)
        else:
            col.prop(self, "fresnel_effect", toggle=True)
            col.prop(self, "IOR_reflection")               
    #
    def exportValues(self):
        self.params['fresnel_effect']= self.fresnel_effect
        self.params['IOR_reflection']= self.IOR_reflection
        #
        if self.is_linked:
            linked_node = self.links[0].from_node
            try:
                linked_node.exportValues(self)
            except:
                print('Not export values on node')
        #
        return self.params
                
    #
    def draw_color(self, context, node):
        return (float_socket)
#
bounty_socket_class.append(fresnel_socket) 
   
#-----------------------------------------
# Index of refraction socket (IOR)
#-----------------------------------------
class ior_socket(NodeSocket, TheBountyNodeSocket):
    bl_idname = "IOR"
    bl_label = "IOR Socket"
    
    IOR_reflection = MatProperty.IOR_reflection
    
    # default values for socket's
    def default_value_get(self):
        return self.IOR_reflection
    
    def default_value_set(self, value):
        self.IOR_reflection = value
    
    default_value =  FloatProperty( get=default_value_get, set=default_value_set)
        
    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "IOR_reflection")            
    #
    def draw_color(self, context, node):
        return (float_socket)
#
bounty_socket_class.append(ior_socket)

#------------------------
# Color Specular sockect
#------------------------
class glass_mirror_color_socket(NodeSocket, TheBountyNodeSocket):
    bl_idname = 'glass_mir_col'
    bl_label = 'Mirror Socket'
    params = {}
    
    glass_mir_col = FloatVectorProperty(
        name="Mirror", description="Mirror color reflection",
        subtype='COLOR', min=0.0, max=1.0, default=(0.8, 0.80, 0.80)
    )
    
    # default values for socket's
    def default_value_get(self):
        return self.glass_mir_col
    
    def default_value_set(self, value):
        self.glass_mir_col = value
    
    default_value =  bpy.props.FloatVectorProperty( subtype='COLOR', get=default_value_get, set=default_value_set)
    #        
    def draw(self, context, layout, node, text):
        col = layout.row()
        label = "Reflect layer" if self.is_linked else "Mirror color"
        
        col.prop(self, "glass_mir_col", text="")
        col.label(text=label) 
    #
    def draw_color(self, context, node):
        return (color_socket)
#
bounty_socket_class.append(glass_mirror_color_socket)

#-------------------
# bumpmap sockect
#-------------------
class bumpmap_socket(NodeSocket, TheBountyNodeSocket):
    bl_idname = 'bumpmap'
    bl_label = 'Bumpmap Socket'
    params = {} 
    
    bumpmap = BoolProperty(
            name="Bumpmap layer",
            description="Apply bumpmap effect to material",
            default=False
    )  
    
    # default values for socket
    def default_value_get(self):
        return self.bumpmap
    
    def default_value_set(self, value):
        self.bumpmap = value
    
    default_value =  bpy.props.BoolProperty( get=default_value_get, set=default_value_set)
            
    # draw socket
    def draw(self, context, layout, node, text):
        row = layout.row()
        label="BumpMap texture Layer" if self.is_linked else "BumpMap"
        #
        if self.is_linked:
            #
            row.prop(self, "bumpmap", text=label)
        else:
            row.label(text=label)
            
    #
    def exportValues(self):
        self.params['bumpmap']= self.bumpmap
        if self.is_linked:
            linked_node = self.links[0].from_node
            try:
                self.params=linked_node.exportValues(self)
            except:
                print('Not export values on node')
        #
        return self.params
                
    #
    def draw_color(self, context, node):
        return (float_socket)
#
bounty_socket_class.append(bumpmap_socket)

class mapping_socket(NodeSocket, TheBountyNodeSocket):
    bl_idname = 'mapping'
    bl_label = 'Texture Mapping Socket'
    params = {}
    
    enum_texture_mapping_mode = [
        ('ORCO','Generated',""),
        ('OBJECT','Object',""),
        ('GLOBAL','Global',""),
        ('UV','UV',""),
        ('STRAND','Strand',""),
        ('WINDOW','Window',""),
        ('NORMAL','Normal',""),
        ('REFLECTION','Reflection',""),
        ('STRESS','Stress',""),
        ('TANGENT','Tangent',""),
    ]
    
    # small trick..
    enum_default_texture_mapping_mode = (('UV', 'UV',"UV texture mapping"),)
        
    # default values for socket's
    def default_value_get(self):
        return self.mapping_type
    
    def default_value_set(self, value):
        self.mapping_type = 'UV'
        
    mapping_type = EnumProperty(
            name="Mapping",
            description="Texture coordinates mapping mode",
            items=enum_texture_mapping_mode,
            default='UV',
    )
    default_value =  EnumProperty(items=enum_default_texture_mapping_mode, set=default_value_set)
    #
    def draw(self, context, layout, node, text):
        if self.is_linked:
            layout.label('Mapping Coord.')
        else:
            layout.prop(self, "mapping_type")   
    #
    def exportValues(self):
        self.params['mapping_type']= self.mapping_type
        if self.is_linked:
            linked_node = self.links[0].from_node
            try:
                linked_node.exportValues(self)
            except:
                print('Not export values on node')
        #
        return self.params
                
    #
    def draw_color(self, context, node):
        return (float_socket)
#
bounty_socket_class.append(mapping_socket)

#---------------------------
# texture projection socket
#---------------------------
class projection_socket(NodeSocket, TheBountyNodeSocket):
    bl_idname = 'projection'
    bl_label = 'Texture Projection Socket'
    params = {}

    enum_texture_projection_mode = [
        ('FLAT',   'Flat',  "Flat texture projection"),
        ('CUBE',   'Cube',  "Cube texture projection"),
        ('TUBE',   'Tube',  "Cylindrical texture projection"),
        ('SPHERE', 'Sphere',"Spherical texture projection"),        
    ]
    # small trick..
    enum_default_texture_projection_mode = (('FLAT', 'Flat',"Flat texture mapping"),)
        
    # default values for socket's
    def default_value_get(self):
        return self.projection_type
    
    def default_value_set(self, value):
        self.projection_type = 'FLAT'
        
    projection_type = EnumProperty(
            name="Projection",
            description="Texture projection mode",
            items=enum_texture_projection_mode,
            default='FLAT',
    )    
    default_value =  EnumProperty(items=enum_default_texture_projection_mode, set=default_value_set)
    #
    def draw(self, context, layout, node, text):
        col = layout.column()
        if self.is_linked:
            col.label('Texture projection')
        else:
            col.prop(self, "projection_type")  
    #
    def exportValues(self):
        self.params['projection_type']= self.projection_type
        if self.is_linked:
            linked_node = self.links[0].from_node
            try:
                self.params=linked_node.exportValues(self)
            except:
                print('Not export values on node')
        #
        return self.params
        
    #
    def draw_color(self, context, node):
        return (float_socket)
#
bounty_socket_class.append(projection_socket)


def register():
    for bountyclasses in bounty_socket_class:
        bpy.utils.register_class(bountyclasses)
    
def unregister():
    for bountyclasses in bounty_socket_class:
        bpy.utils.unregister_class(bountyclasses)


if __name__ == "__main__":
    register()
    