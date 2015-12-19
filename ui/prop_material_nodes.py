#---------- BEGIN GPL LICENSE BLOCK ------------------------------------------#
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
#  or visit https://www.fsf.org for more info.
#
#---------- END GPL LICENSE BLOCK --------------------------------------------#

# <pep8 compliant>

import bpy
from bpy.types import Node, NodeSocket
from bpy.props import (FloatProperty, FloatVectorProperty, StringProperty, BoolProperty, EnumProperty)

from . import prop_node_sockets
# test move here
#import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem, NodeItemCustom

from ..prop.tby_material import TheBountyMaterialProperties as MatProperty


bounty_node_class=[]
# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class TheBountyNodeTree(bpy.types.NodeTree):
    #
    
    bl_idname = 'TheBountyNodeTree'
    bl_label = 'TheBounty Node Tree'
    bl_icon = 'MATERIAL'

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'THEBOUNTY'
    
    # code orignally from Matt Ebb's 3Delight exporter   
    @classmethod
    def get_from_context(cls, context):
        
        ob = context.active_object
        if ob and ob.type not in {'LAMP', 'CAMERA'}:
            active_mat = ob.active_material
            if active_mat != None: 
                nt_name = active_mat.bounty.nodetree
                if nt_name != '':
                    return bpy.data.node_groups[active_mat.bounty.nodetree], active_mat, active_mat
                
        return (None, None, None)
        
    # This block updates the preview, when socket links change
    def update(self):
        self.refresh = True
    
    def acknowledge_connection(self, context):
        while self.refresh == True:
            self.refresh = False
            break
    
    refresh = BoolProperty(
                name='Links Changed', 
                default=False, 
                update=acknowledge_connection)
#    
bounty_node_class.append(TheBountyNodeTree)

''' bounty node declaration
'''  
class TheBountyNode:
    @classmethod
    def poll( cls, context):
        # 
        return (context.bl_idname == "TheBountyNodeTree" and context.scene.render.engine == 'THEBOUNTY')

    def draw_buttons( self, context, layout):
        pass
        
    def draw_buttons_ext(self, context, layout):
        pass
    
    def copy( self, node):
        pass
    
    def free( self):
        print("Removing node ", self, ", Goodbye!")
    
    def draw_label( self):
        return self.bl_label
    ##
    def get_name( self):
        #
        return self.name
    
    def traverse_node_tree( self, material_node):
        
        #Iterate inputs and traverse the tree backward if any inputs are connected.
        #Nodes are added to a list attribute of the material output node.
        
        for socket in self.inputs:
            if socket.is_linked:
                linked_node = socket.links[0].from_node
                linked_node.traverse_node_tree( material_node)
        material_node.tree.append( self)
 
''' Base class for node sockets.
'''   
class TheBountyNodeSocket( object):
    # Set to default None.
    socket_value = None

    def get_socket_value( self, texture_only = True):
        '''
        Method to return socket's value, if not linked. 
        If linked, return the name of the node with appended pointer.
        '''
        if self.is_linked:
            linked_node = self.links[0].from_node
            if texture_only and linked_node.node_type == 'texture':
                # The socket only accepts image textures.
                return linked_node.get_node_name() + "_inst"
            if not texture_only:
                return linked_node.get_node_name()
        # Return socket value if not linked, or if the incoming node is incompatible.
        return self.socket_value
       
#
bounty_node_class.append(TheBountyNode)

#------------------------------------------------
# Output node
#------------------------------------------------
class TheBountyMaterialOutputNode(Node, TheBountyNode):
    bl_idname = 'MaterialOutputNode'
    bl_label = 'Material Output'
    bl_icon = 'NODETREE'
    bl_width_min = 120
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', "Surface")
        self.inputs.new('diffuse_color',"Color")
    
    def draw_buttons(self, context, layout):
        try:
            layout.label(context.active_object.active_material.name)
        except:
            layout.label(context.material.name)
#
bounty_node_class.append(TheBountyMaterialOutputNode)
        
#------------------------------------------------
# Shinydiffuse node
#------------------------------------------------           
class TheBountyShinyDiffuseShaderNode(Node, TheBountyNode):
    bl_idname = 'ShinyDiffuseShaderNode'
    bl_label = 'shinydiffusemat'
    bl_icon = 'MATERIAL'
    bl_width_min = 180
    
    node_type='shinydiffusemat'    
    #
    def init(self, context):
        # slots shaders
        self.outputs.new('NodeSocketColor', "Shader")
        
        self.inputs.new('diffuse_color',"Color")
        self.inputs.new('emittance', 'Emitt')
        
        self.inputs.new('brdf', 'BRDF')
        
        self.inputs.new('transparency', 'Transparency')
        self.inputs.new('translucency', 'Translucency')
        
        self.inputs.new('mirror', 'Mirror')
        
        self.inputs.new('fresnel', 'Fresnel Effect')
        
        #self.inputs.new('NodeSocketColor', "BumpMap")
    
    def copy(self, node):
        # Copy function to initialize a copied node from an existing one.
        print("Copying from node ", node)

    def free(self):
        # Free function to clean up on removal.
        print("Removing node ", self, ", Goodbye!")
    
    def draw_buttons(self, context, layout):
        # Additional buttons displayed on the node.
        pass
            
    def draw_buttons_ext(self, context, layout):
        # Detail buttons in the sidebar.
        # If this function is not defined, the draw_buttons function is used instead
        pass
#
bounty_node_class.append(TheBountyShinyDiffuseShaderNode)

#------------------------------------------------
# Translucent SSS node
#------------------------------------------------
class TheBountyTranslucentShaderNode(Node, TheBountyNode):
    #
    bl_idname = 'TranslucentScattering'
    bl_label = 'translucent'
    bl_icon = 'MATERIAL'
    bl_width_min = 180
    
    #
    def init(self, context):
        # slots shaders
        self.outputs.new('NodeSocketColor', "Shader")
        
        self.inputs.new('diffuse_color',"Color")
        self.inputs.new('diffuse_reflection', 'Reflection')
    
    def draw_buttons(self, context, layout):
        #
        mat = context.active_object.active_material
                
        col = layout.column()
        #col.prop(mat, "diffuse_color")
        #col.prop(mat.bounty, "diffuse_reflect", text="Diff. Reflect",slider=True)
        col.prop(mat.bounty, "glossy_color")
        col.prop(mat.bounty, "glossy_reflect", text="Gloss. Reflect",slider=True)
        col.prop(mat.bounty, "sssSpecularColor")
        col.prop(mat.bounty, "exponent", text="Specular Exponent")
        
        #row = layout.row()
        #row.label("SSS Presets")
        #row.menu("TheBountyScatteringPresets", text=bpy.types.TheBountyScatteringPresets.bl_label)
        
        col = layout.column()        
        
        col.prop(mat.bounty, "sssSigmaS", text="Scatter color")
        col.prop(mat.bounty, "sssSigmaS_factor")
        col.prop(mat.bounty, "phaseFuction")
                
        col.prop(mat.bounty, "sssSigmaA", text="Absorption color")
        col.prop(mat.bounty, "sss_transmit", text="Transmit")
        col.prop(mat.bounty, "sssIOR")
#
bounty_node_class.append(TheBountyTranslucentShaderNode)

#------------------------------------------------
# Glossy node
#------------------------------------------------
class TheBountyGlossyShaderNode(Node, TheBountyNode):
    bl_idname = 'GlossyShaderNode'
    bl_label = 'glossy'
    bl_icon = 'MATERIAL'
    bl_width_min = 180
    
    def init(self, context):
        #
        self.outputs.new('NodeSocketColor', "Shader")
        
        self.inputs.new('diffuse_color',"Diffuse Color")        
        self.inputs.new('brdf', 'BRDF')
    
    def draw_buttons(self, context, layout):
        """ Same design to a UI panels ( column, split, row..) """
        # sync values with panels
        mat = context.active_object.active_material
        
        col = layout.column()
        
        col = layout.column()
        col.prop(mat.bounty, "glossy_color")
        exp = col.column()
        exp.enabled = mat.bounty.anisotropic == False
        exp.prop(mat.bounty, "exponent")

        #col = split.column()
        sub = col.column(align=True)
        sub.prop(mat.bounty, "anisotropic")
        ani = sub.column()
        ani.enabled = mat.bounty.anisotropic == True
        ani.prop(mat.bounty, "exp_u")
        ani.prop(mat.bounty, "exp_v")
        col= layout.column()
        col.prop(mat.bounty, "glossy_reflect", slider=True)
        col.row().prop(mat.bounty, "as_diffuse")

        layout.separator()

        if mat.bounty.mat_type == "coated_glossy":
            box = layout.box()
            box.label(text="Coated layer")
            col = layout.column()
            col.prop(mat.bounty, "coat_mir_col")
            col.label(text="Fresnel reflection:")
            col.prop(mat.bounty, "IOR_reflection")
    
    def draw_buttons_ext(self, context, layout):
        # many buttons..
        pass

    def copy(self, node):
        print("Copying from node ", node)

    def free(self):
        print("Removing node ", self, ", Goodbye!")
#
bounty_node_class.append(TheBountyGlossyShaderNode)

#------------------------------------------------
# Glass shader node
#------------------------------------------------                      
class TheBountyGlassShaderNode(Node, TheBountyNode):
    bl_idname = 'GlassShaderNode'
    bl_label = 'glass'
    bl_icon = 'MATERIAL'
    bl_width_min = 180

    def init(self, context):
        #
        self.outputs.new('NodeSocketColor', "Shader")

    def draw_buttons(self, context, layout):
        """ Same design to a UI panels ( column, split, row..) """
        mat = context.active_object.active_material
        
        layout.label(text="Refraction and Reflections:")
        col = layout.column()
        col.prop(mat.bounty, "IOR_refraction")

        # TODO: need review..
        #col.menu("YAF_MT_presets_ior_list", text=bpy.types.YAF_MT_presets_ior_list.bl_label)

        col.prop(mat.bounty, "absorption")
        col.prop(mat.bounty, "absorption_dist")

        col.prop(mat.bounty, "dispersion_power")

        if mat.bounty.mat_type == "rough_glass":
            col = layout.column()
            #box.label(text="Glass roughness:")
            col.prop(mat.bounty, "refr_roughness",text="Roughness exponent", slider=True)

        col.prop(mat.bounty, "filter_color")
        col.prop(mat.bounty, "glass_mir_col")
        col.prop(mat.bounty, "glass_transmit", slider=True)
        col.prop(mat.bounty, "fake_shadows")
            
    def draw_buttons_ext(self, context, layout):
        # many buttons..
        pass

    def copy(self, node):
        print("Copying from node ", node)
        
    def free(self):
        print("Removing node ", self, ", Goodbye!")
#
bounty_node_class.append(TheBountyGlassShaderNode)

#------------------------------------------------
# Blend shader node
#------------------------------------------------
class TheBountyBlendShaderNode(Node, TheBountyNode):
    # Glossy custom node
    bl_idname = 'BlendShaderNode'
    bl_label = 'blend'
    bl_icon = 'MATERIAL'
    bl_width_min = 180
        
    # test
    # TODO: is need find the methode for acces to this parameter for exporter
    blend_amount = FloatProperty(
        name="Blend value",
        description="Amount of blending materials",
        default=0.5, min=0.0, max=1.0)

    def init(self, context):
        self.inputs.new('NodeSocketShader', "Material One")
        self.inputs.new('NodeSocketShader', "Material Two")
        # outputs
        self.outputs.new('NodeSocketShader', "Shader")

    def draw_buttons(self, context, layout):
        try:
            #mat = context.active_object.active_material
            layout.prop(self, "blend_amount", text="")
        except:
            print("Nonetype node")
#
bounty_node_class.append(TheBountyBlendShaderNode)

'''
class TheBountyTextureShaderNode(Node, TheBountyNode):
    # Texture shader node
    bl_idname = 'TextureShaderNode'
    bl_label = 'Texture Shader'
    bl_icon = 'TEXTURE'
    bl_width_min = 180

    def init(self, context):
        #self.inputs.new('NodeSocketColor', "Filter Color")
        #
        self.outputs.new('NodeSocketColor', "Shader")

    def draw_buttons(self, context, layout):
        #
        pass
            
    def draw_buttons_ext(self, context, layout):
        pass

    def copy(self, node):
        print("Copying from node ", node)
        
    def free(self):
        print("Removing node ", self, ", Goodbye!")
#
bounty_node_class.append(TheBountyTextureShaderNode)


#-------------------------------------------
# BDRF model
#-------------------------------------------
class TheBountyBrdfNode(Node, TheBountyNode):
    #    
    bl_idname = 'TheBountyBrdfNode'
    bl_label = 'BRDF Node'
    bl_width_min = 160  
    
    brdf_type = MatProperty.brdf_type
    sigma = MatProperty.sigma
   
    #
    def init(self, context):
        self.outputs.new('NodeSocketColor', 'Color')
        
    def draw_buttons(self, context, layout):
        layout.prop(self, 'brdf_type', text='')
        layout.prop(self,'sigma', text='', slider=True)       
#
bounty_node_class.append(TheBountyBrdfNode)   
'''       
#------------------------------------------------
# Imagemap node
#------------------------------------------------
class TheBountyImageMapNode(Node, TheBountyNode):
    #-------------------------
    # texture image map nodee
    #-------------------------
    bl_idname = 'TheBountyImageMapNode'
    bl_label = 'ImageMap'
    # 
    bl_width_min = 220
    
    #----------------------------------------------- 
    # properties
    #-----------------------------------------------
    influence = FloatProperty(
        name="Influence", description="Amount of texture/color influence on a  material ( 0 : color, 1: texture)",
        min=0.0, max=1.0, step=1, precision=3,
        soft_min=0.0, soft_max=1.0, default=1.00
    )
    image_map = StringProperty(
        name="", description="Image File to be used on texture",
        subtype='FILE_PATH', default=""
    )
    #
    def init(self, context):
        self.outputs.new('NodeSocketColor', 'Color')
        #
        self.inputs.new("mapping", "Mapping coord.")
        self.inputs.new("projection", "Projection")
        
    def draw_buttons(self, context, layout):
        #
        layout.label('Image file')
        layout.prop(self, "image_map")
        layout.prop(self,'influence', text='Texture Influence', slider=True)
                
#
bounty_node_class.append(TheBountyImageMapNode)

'''
#------------------------------------------------
# Mirror node
#------------------------------------------------      
class TheBountyMirrorNode(Node, TheBountyNode):
    bl_idname = 'TheBountyMirrorNode'
    bl_label = 'Mirror Node'    
    
    mirror_color = MatProperty.mirror_color
    specular_reflect = MatProperty.specular_reflect
    
    def init(self, context):
        self.outputs.new('NodeSocketColor', "Color")
        
    def draw_buttons(self, context, layout):
        col = layout.column()
        col.prop(self, 'mirror_color')
        col.prop(self, 'specular_reflect', slider=True)
#
bounty_node_class.append(TheBountyMirrorNode)    
       
'''

# our own base class with an appropriate poll function,
# so the categories only show up in our own tree type
class TheBountyNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.space_data.tree_type =='TheBountyNodeTree' and engine == 'THEBOUNTY'

# all categories in a list
TheBountyNodeCategories = [
    # identifier, label, items list
    #TheBountyNodeCategory("TheBountyLight", "Light Output", items=[
    #    # output node
    #    NodeItem("LampOutputNode"),
    #    ]),
    TheBountyNodeCategory("TheBountyMaterial", "Material", items=[
        # output node
        NodeItem(TheBountyMaterialOutputNode.bl_idname),
        ]),
    TheBountyNodeCategory("TheBountyShaders", "Shaders", items=[
        # shader nodes, use bl_idname's 
        NodeItem(TheBountyShinyDiffuseShaderNode.bl_idname),
        NodeItem(TheBountyGlossyShaderNode.bl_idname),
        NodeItem(TheBountyBlendShaderNode.bl_idname),
        NodeItem(TheBountyGlassShaderNode.bl_idname),
        NodeItem(TheBountyTranslucentShaderNode.bl_idname),
        #NodeItem(TheBountyBrdfNode.bl_idname),
        #NodeItem(TheBountyMirrorNode.bl_idname),
        ]),
    TheBountyNodeCategory("TheBountyTextures", "Textures", items=[
        # texture nodes
        NodeItem(TheBountyImageMapNode.bl_idname),
        #NodeItem(TheBountyTextureShaderNode.bl_idname),
        #NodeItem(TheBountyBrdfNode.bl_idname)
        ]),
    ]
#
bounty_node_class.append(TheBountyNodeCategory)


def register():
    for bclass in bounty_node_class:
        bpy.utils.register_class(bclass)
    
def unregister():
    for bclass in bounty_node_class:
        bpy.utils.unregister_class(bclass)


if __name__ == "__main__":
    register()
