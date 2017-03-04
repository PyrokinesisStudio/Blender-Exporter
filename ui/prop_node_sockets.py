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

import bpy
from bpy.types import Node, NodeSocket
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

class light_color_socket(NodeSocket):
    #-----------------------
    # Light color socket 
    #-----------------------
    
    bl_idname = 'color'
    bl_label = 'Color Socket'
    params = {}
    color = bpy.props.FloatVectorProperty(
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
class diffuse_color_socket(NodeSocket):
    bl_idname = 'diffuse_color'
    bl_label = 'Color Socket'
    validNodes = ['Image', 'Clouds']
    
    #properties..
    diff_color = MatProperty.diff_color
    
    # useful helper functions
    def default_value_get(self):
        return self.diff_color
    
    def default_value_set(self, value):
        self.diff_color = value
        
    default_value =  bpy.props.FloatVectorProperty( subtype='COLOR', get=default_value_get, set=default_value_set)
    
    #         
    def draw(self, context, layout, node, text):
        col = layout.column()
        label = 'Diffuse Color' if self.is_linked else 'Diffuse color layer'
        #                     
        col.prop(self, "diff_color", text= label )
    
    def getParams(self):
        params = dict()
        params['color']= [c for c in self.diff_color]
        #
        if self.is_linked:
            #print('linked to: ', self.links[0].from_node.bl_label)
            linked_node = self.links[0].from_node
            if linked_node.bl_label in self.validNodes:
                params['diffuse_shader']='diff_layer'
                params['DiffuseLayer']= linked_node.getParams()
            else:
                print('Invalid node: ', linked_node.bl_label)
                
        return params
    #
    def draw_color(self, context, node):
        return (color_socket)

#
bounty_socket_class.append(diffuse_color_socket)


#-------------------------------------
# translucency
#-------------------------------------
class translucency_socket(NodeSocket):
    bl_idname = 'translucency'
    bl_label = 'Translucency Socket'
    matParams={}
    validNodes = ['Image', 'Clouds']  
    
    translucency = MatProperty.translucency    
    
    # default values for socket
    def default_value_get(self):
        return self.translucency
    
    def default_value_set(self, value):
        self.translucency = value
        
    default_value =  bpy.props.FloatProperty( get=default_value_get, set=default_value_set)
    #    
    def draw(self, context, layout, node, text):
        #
        col = layout.column()
        if self.is_linked:
            col.label('Translucency Layer')
        col.prop(self, "translucency", slider=True)
    #
    def getParams(self):
        #                
        self.matParams['translucency']= self.translucency
        #
        if self.is_linked:
            linked_node = self.links[0].from_node
            self.matParams['translucency_shader'] = 'translu_layer'
            self.matParams['TranslucencyLayer'] = linked_node.getParams()
        return self.matParams
    # 
    def draw_color(self, context, node):
        return (float_socket)
#
bounty_socket_class.append(translucency_socket)

#----------------------------------------------------------
# transparency
#----------------------------------------------------------   
class transparency_socket(NodeSocket):
    bl_idname = 'transparency'
    bl_label = 'Transparency Socket'
    matParams = {}
    validNodes = ['Image', 'Clouds'] # for review
    
    transparency = MatProperty.transparency
    
    # default values for socket
    def default_value_get(self):
        return self.transparency
    
    def default_value_set(self, value):
        self.transparency = value
    
    default_value =  bpy.props.FloatProperty( get=default_value_get, set=default_value_set)
            
    # draw socket
    def draw(self, context, layout, node, text):
        col = layout.column()
        if self.is_linked:
            col.label('Transparency Layer')
        col.prop(self, "transparency", slider=True)    
    #
    def getParams(self):
        #self.matParams['transparency']= self.transparency
        #
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

#----------------------------------------------------------
# specular reflect sockect
#----------------------------------------------------------
class specular_reflect_socket(NodeSocket):
    bl_idname = 'specular'
    bl_label = 'Specular Socket'
    matParams = {}
    validNodes = ['Image', 'Clouds'] # for review
    
    specular_reflect = MatProperty.specular_reflect
    
    # default values for socket's
    def default_value_get(self):
        return self.specular_reflect
    
    def default_value_set(self, value):
        self.specular_reflect = value
    
    default_value =  bpy.props.FloatProperty( get=default_value_get, set=default_value_set)
    
    def draw(self, context, layout, node, text):
        col = layout.column()
        if self.is_linked:
            col.label("Specular reflect layer")
        col.prop(self, "specular_reflect", slider=True)     
    #
    def getParams(self):
        self.matParams['specular_reflect']= self.specular_reflect
        #
        if self.is_linked:
            linked_node = self.links[0].from_node
            if linked_node.bl_label in self.validNodes:
                self.matParams['mirror_shader']='mirr_layer'
                self.matParams['MirrorLayer']= linked_node.getParams()
                
        return self.matParams
    
    def draw_color(self, context, node):
        return (float_socket)
#
bounty_socket_class.append(specular_reflect_socket)


#----------------------------------------------------------
# specular sockect
#----------------------------------------------------------
class specular_color_socket(NodeSocket):
    bl_idname = 'mirror'
    bl_label = 'Mirror Color Socket'
    matParams = {}
    validNodes = ['Image']
    
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
    def getParams(self):
        #
        self.matParams['mirror_color']= [c for c in self.mirror_color]
        
        if self.is_linked:
            linked_node = self.links[0].from_node
            if linked_node.bl_label in self.validNodes:
                self.matParams['mirror_color_shader']='mircol_layer'
                self.matParams['MirrorColorLayer']= linked_node.getParams()
            else:
                print('Not valid node: ', linked_node.bl_label)
        #
        return self.matParams
    #
    def draw_color(self, context, node):
        return (color_socket)
#
bounty_socket_class.append(specular_color_socket)

#----------------------------------------------------------
# glossy color and reflection sockets
#----------------------------------------------------------
class glossy_color_socket(NodeSocket):
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
    def getParams(self):
        self.params['glossy_color']= [c for c in self.glossy_color]
        if self.is_linked:
            linked_node = self.links[0].from_node
            try:
                linked_node.getParams(self)
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
class glossy_reflect_socket(NodeSocket):
    bl_idname = 'glossy_reflect'
    bl_label = 'Reflection Socket'
    
    glossy_reflect = MatProperty.diffuse_reflect
    
    # helper property
    def default_value_get(self):
        return self.glossy_reflect
    
    def default_value_set(self, value):
        self.glossy_reflect  = value
        
    default_value =  bpy.props.FloatProperty( get=default_value_get, set=default_value_set, default=0.0 , min=0.0, max=1.0)
    #    
    def draw(self, context, layout, node, text):
        #
        layout.prop(self, "glossy_reflect", text= 'Glossy Reflection', slider=True)
    
    #
    def getParams(self):
        self.params['glossy_reflect']= self.glossy_reflect
        if self.is_linked:
            linked_node = self.links[0].from_node
            try:
                linked_node.getParams(self)
            except:
                print('Not export values on node')
        #
        return self.params
    #
    def draw_color(self, context, node):
        return (float_socket)
#
bounty_socket_class.append(glossy_reflect_socket)

#------------------------
# Color Specular sockect
#------------------------
class glass_mirror_color_socket(NodeSocket):
    bl_idname = 'glass_mir_col'
    bl_label = 'Mirror Socket'
    params = {}
    
    glass_mir_col = MatProperty.glass_mir_col
    
    # default values for socket's
    def default_value_get(self):
        return self.glass_mir_col
    
    def default_value_set(self, value):
        self.glass_mir_col = value
    
    default_value =  bpy.props.FloatVectorProperty( subtype='COLOR', get=default_value_get, set=default_value_set)
    #        
    def draw(self, context, layout, node, text):
        #
        col = layout.column()
        label = "Reflect layer" if self.is_linked else "Mirror color"
        
        col.prop(self, "glass_mir_col", text="")
    #
    def draw_color(self, context, node):
        return (color_socket)
#
bounty_socket_class.append(glass_mirror_color_socket)

##
class scatter_color_socket(NodeSocket): 
    bl_idname = 'scatter_color'
    bl_label = 'Color Socket'
    matParams = {}
    validNodes = ['Image', 'Clouds']
    
    #properties..
    scatter_color = MatProperty.diff_color
    
    # useful helper functions
    def default_value_get(self):
        return self.scatter_color
    
    def default_value_set(self, value):
        self.scatter_color = value
        
    default_value =  bpy.props.FloatVectorProperty( subtype='COLOR', get=default_value_get, set=default_value_set)
    
    #         
    def draw(self, context, layout, node, text):
        col = layout.column()
        label = 'Scatter (SigmaS)'
        if self.is_linked: # and not self.is_output:
            label = 'Scatter color layer'
        #                     
        col.prop(self, "scatter_color", text= label )
    
    def getParams(self):
        self.matParams['scatter_color']= [c for c in self.scatter_color]
        #
        if self.is_linked:
            linked_node = self.links[0].from_node
            if linked_node.bl_label in self.validNodes:
                self.matParams['scatter_shader']='scatter_layer'
                self.matParams['ScatterLayer']= linked_node.getParams()
            else:
                print('Not valid node: ', linked_node.bl_label)
                
        return self.matParams
    #
    def draw_color(self, context, node):
        return (color_socket)

#
bounty_socket_class.append(scatter_color_socket)

##
class absorption_color_socket(NodeSocket): 
    bl_idname = 'absorption_color'
    bl_label = 'Color Socket'
    matParams = {}
    validNodes = ['Image', 'Clouds']
    
    #properties..
    absorption_color = MatProperty.diff_color
    
    # useful helper functions
    def default_value_get(self):
        return self.absorption_color
    
    def default_value_set(self, value):
        self.absorption_color = value
        
    default_value =  bpy.props.FloatVectorProperty( subtype='COLOR', get=default_value_get, set=default_value_set)
    
    #         
    def draw(self, context, layout, node, text):
        col = layout.column()
        label = 'Absorption (SigmaA)'
        if self.is_linked: # and not self.is_output:
            label = 'Absorption color layer'
        #                     
        col.prop(self, "absorption_color", text= label )
    
    def getParams(self):
        self.matParams['absorption_color']= [c for c in self.absorption_color]
        #
        if self.is_linked:
            linked_node = self.links[0].from_node
            if linked_node.bl_label in self.validNodes:
                self.matParams['absorption_shader']='absorption_layer'
                self.matParams['AbsorptionLayer']= linked_node.getParams()
            else:
                print('Not valid node: ', linked_node.bl_label)
                
        return self.matParams
    #
    def draw_color(self, context, node):
        return (color_socket)

#
bounty_socket_class.append(absorption_color_socket)

#-------------------
# bumpmap sockect
#-------------------
class bumpmap_socket(NodeSocket):
    bl_idname = 'bumpmap'
    bl_label = 'Bumpmap Socket' 
    
    bumpmap = bpy.props.BoolProperty(
            name="Bumpmap layer",
            description="Apply bumpmap effect to material",
            default=False
    )  
    bump = bpy.props.FloatProperty(
            name="Bumpmap layer",
            description="Bumpmap effect amount to material",
            default=0.0
    )  
    
    # default values for socket
    def default_value_get(self):
        return self.bumpmap
    
    def default_value_set(self, value):
        self.bumpmap = value
    
    default_value =  bpy.props.BoolProperty( get=default_value_get, set=default_value_set)
            
    # draw socket
    def draw(self, context, layout, node, text):
        col = layout.column()
        label="BumpMap texture Layer" if self.is_linked else "BumpMap"
        #
        if self.is_linked:
            #
            col.prop(self, "bumpmap", text=label)
            col.prop(self, "bump")
        else:
            col.label(label)
            
    #
    def getParams(self):
        params = dict()
        params['bumpmap']= self.bumpmap
        if self.is_linked:
            linked_node = self.links[0].from_node
            try:
                params=linked_node.getParams(self)
            except:
                print('Not export values on node')
        #
        return params
                
    #
    def draw_color(self, context, node):
        return (float_socket)
#
bounty_socket_class.append(bumpmap_socket)

class mapping_socket(NodeSocket):
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
        
    mapping_type = bpy.props.EnumProperty(
            name="Mapping",
            description="Texture coordinates mapping mode",
            items=enum_texture_mapping_mode,
            default='UV',
    )
    default_value =  bpy.props.EnumProperty(items=enum_default_texture_mapping_mode, set=default_value_set)
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
class projection_socket(NodeSocket):
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
        
    projection_type = bpy.props.EnumProperty(
            name="Projection",
            description="Texture projection mode",
            items=enum_texture_projection_mode,
            default='FLAT',
    )    
    default_value =  bpy.props.EnumProperty(items=enum_default_texture_projection_mode, set=default_value_set)
    #
    def draw(self, context, layout, node, text):
        col = layout.column()
        if self.is_linked:
            col.label('Texture projection')
        else:
            col.prop(self, "projection_type")  
    #
    def getParams(self):
        #self.params['projection_type']= self.projection_type
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
    