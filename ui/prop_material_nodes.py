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
#
from nodeitems_utils import NodeCategory, NodeItem, NodeItemCustom

from ..prop.tby_material import TheBountyMaterialProperties as MatProperty
#------------------------------------------------------

def fixNodeSize(nmin, nmax):
    bl_width_min = nmin
    bl_width_max = nmax

bounty_node_class=[]

#
class TheBountyMaterialNodeTree(bpy.types.NodeTree):
    #    
    bl_idname = 'TheBountyMaterialNodeTree'
    bl_label = 'TheBounty NodeTree'
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
        '''
        elif ob and ob.type == 'LAMP':
            la = ob.data
            nt_name = la.bounty.nodetree
            if nt_name != '':
                return bpy.data.node_groups[la.bounty.nodetree], la, la
        '''        
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
bounty_node_class.append(TheBountyMaterialNodeTree)

''' TheBounty material node class base declaration
'''  
class TheBountyMaterialNode:
    # test for lock node sizes
    bl_width_min = bl_width_max = 180
      
    @classmethod
    def poll( cls, context):
        #
        engine = context.scene.render.engine 
        return (context.bl_idname == "TheBountyMaterialNodeTree" and engine == 'THEBOUNTY')

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
    # base
    #
    def traverse_node_tree(self, material_node):
        #
        for socket in self.inputs:
            if socket.is_linked:
                linked_node = socket.links[0].from_node
                linked_node.traverse_node_tree( material_node)
        material_node.listedNodes.append(self)
        
        '''
        for socket in self.inputs:
            
            if socket.is_linked:
                print('linked socket: ', socket.name)
                linked_node = socket.links[0].from_node
                linked_node.traverse_node_tree(material_node)
                # start
                for input in linked_node.inputs:
                    if input.is_linked:
                        new_node = input.links[0].from_node
                        new_node.traverse_node_tree(material_node)
                        print('new node: ', new_node.name)
                        #print('input on node: ', input.bl_label, 'values: ', input.getValues())
                        #material_node.nodeValues.append((input.bl_idname, input.exportValues())) # getValues()))
                    material_node.nodeValues = input.exportValues()
                # end
                
                if linked_node.name not in material_node.nodetreeListNames:
                    material_node.nodetreeListNames.append(linked_node.name)
                #material_node.nodetreeListNodes.append(linked_node.bl_label)
            # si no es linked que hacemos??
            else:
                print('unlinked socket: ', socket.name, ', value: ', socket.default_value)
            
        #return material_node.nodetreeListNames, 
        #return material_node.nodeValues
        '''  
    
#
bounty_node_class.append(TheBountyMaterialNode)

#------------------------------------------------
# Material Output node
#------------------------------------------------
class TheBountyMaterialOutputNode(Node, TheBountyMaterialNode):
    bl_idname = 'MaterialOutputNode'
    bl_label = 'Output Material'
    bl_icon = 'NODETREE'
    bl_width_min = 120
    bl_width_max = 130
    #
    listedNodes = []

    def init(self, context):
        self.inputs.new('NodeSocketShader', "Surface")
        
    
    def draw_buttons(self, context, layout):
        try:
            layout.label(context.active_object.active_material.name)
        except:
            layout.label(context.material.name)
    #
    def filterNodeList( self, nodes):
        nodeList = []
        for node in nodes:
            if node not in nodeList:
                nodeList.append( node)
        return nodeList
    #
    def traverse_node_tree( self):
        #
        self.listedNodes.clear()
        for socket in self.inputs:
            if socket.is_linked:
                linked_node = socket.links[0].from_node
                linked_node.traverse_node_tree( self)
        #
        return self.filterNodeList(self.listedNodes)  
#
bounty_node_class.append(TheBountyMaterialOutputNode)
        
#------------------------------------------------
# Shinydiffuse node
#------------------------------------------------           
class TheBountyShinyDiffuseShaderNode(Node, TheBountyMaterialNode):
    bl_idname = 'ShinyDiffuseShaderNode'
    bl_label = 'shinydiffusemat'
    bl_icon = 'MATERIAL'
       
    #
    def init(self, context):
        # slots shaders
        self.outputs.new('NodeSocketColor', "Shader")
        
        self.inputs.new('diffuse_color',"Diffuse")
        
        self.inputs.new('emittance', 'Emittance')
        self.inputs['Emittance'].enabled = False
        
        self.inputs.new('brdf', 'BRDF')
        
        self.inputs.new('transparency', 'Transparency')
        
        self.inputs.new('translucency', 'Translucency')
        
        self.inputs.new('mirror', 'Mirror')
        
        self.inputs.new('fresnel', 'Fresnel')
        
        #self.inputs.new('bumpmap', 'Bumpmap')
    
    def draw_buttons(self, context, layout):
        # Additional buttons displayed on the node.
        pass
    
#
bounty_node_class.append(TheBountyShinyDiffuseShaderNode)

#------------------------------------------------
# Translucent SSS node
#------------------------------------------------
class TheBountyTranslucentShaderNode(Node, TheBountyMaterialNode):
    #
    bl_idname = 'TranslucentShaderNode'
    bl_label = 'translucent'
    bl_icon = 'MATERIAL'
    
    #
    def init(self, context):
        # slots shaders
        self.outputs.new('NodeSocketColor', "Shader")
        
        self.inputs.new('diffuse_color',"Diffuse")
        
        self.inputs.new('glossy_color',"Glossy Color")
        
        self.inputs.new('bumpmap', 'Bumpmap')
    
    def draw_buttons(self, context, layout):
        #
        mat = context.active_object.active_material
                
        col = layout.column()
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
class TheBountyGlossyShaderNode(Node, TheBountyMaterialNode):
    bl_idname = 'GlossyShaderNode'
    bl_label = 'glossy'
    bl_icon = 'MATERIAL'
    
    def init(self, context):
        #
        self.outputs.new('NodeSocketColor', "Shader")
        
        self.inputs.new('diffuse_color',"Diffuse")    
        self.inputs.new('brdf', 'BRDF')
        
        self.inputs.new('glossy_color',"Glossy")
        self.inputs.new('glossy_reflect',"Specular")
        #self.inputs.new('bumpmap', 'Bumpmap')
    
    def draw_buttons(self, context, layout):
        #
        mat = context.active_object.active_material
        
        col = layout.column()
        exp = col.column()
        exp.enabled = mat.bounty.anisotropic == False
        exp.prop(mat.bounty, "exponent")

        sub = col.column(align=True)
        sub.prop(mat.bounty, "anisotropic")
        ani = sub.column()
        ani.enabled = mat.bounty.anisotropic == True
        ani.prop(mat.bounty, "exp_u")
        ani.prop(mat.bounty, "exp_v")
        layout.prop(mat.bounty, "as_diffuse")

        layout.separator()

        if mat.bounty.mat_type == "coated_glossy":
            col = layout.column()
            col.prop(mat.bounty, "coat_mir_col")
            col.prop(mat.bounty, "IOR_reflection")
#
bounty_node_class.append(TheBountyGlossyShaderNode)

#------------------------------------------------
# Glass shader node
#------------------------------------------------                      
class TheBountyGlassShaderNode(Node, TheBountyMaterialNode):
    bl_idname = 'GlassShaderNode'
    bl_label = 'glass'
    bl_icon = 'MATERIAL'

    def init(self, context):
        #
        self.outputs.new('NodeSocketColor', "Shader")
        # add only connectable slots
        self.inputs.new('glass_mir_col', 'Mirror')
        self.inputs.new('bumpmap', 'Bumpmap')

    def draw_buttons(self, context, layout):
        """ Same design to a UI panels ( column, split, row..) """
        mat = context.active_object.active_material
        
        col = layout.column()
        # TODO: need review..
        #col.menu("YAF_MT_presets_ior_list", text=bpy.types.YAF_MT_presets_ior_list.bl_label)
        
        
        col.prop(mat.bounty, "absorption")
        col.prop(mat.bounty, "absorption_dist", text='Distance')
        col.prop(mat.bounty, "dispersion_power", text='Dispersion power')
        if mat.bounty.mat_type == "rough_glass":
            col = layout.column()
            col.prop(mat.bounty, "refr_roughness", text="Roughness exponent", slider=True)
        col.prop(mat.bounty, "filter_color")
        col.prop(mat.bounty, "glass_transmit", slider=True)
        col.prop(mat.bounty, "fake_shadows")
        col.prop(mat.bounty, "IOR_refraction")
#
bounty_node_class.append(TheBountyGlassShaderNode)

#------------------------------------------------
# Blend shader node
#------------------------------------------------
class TheBountyBlendShaderNode(Node, TheBountyMaterialNode):
    # Glossy custom node
    bl_idname = 'BlendShaderNode'
    bl_label = 'blend'
    bl_icon = 'MATERIAL'
        
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
            layout.prop(self, "blend_amount", text="", slider=True)
        except:
            print("Nonetype node")
#
bounty_node_class.append(TheBountyBlendShaderNode)

'''
#-------------------------------------------
# BDRF model
#-------------------------------------------
class TheBountyBrdfNode(Node, TheBountyMaterialNode):
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
class TheBountyImageMapNode(Node, TheBountyMaterialNode):
    #-------------------------
    # texture image map nodee
    #-------------------------
    bl_idname = 'TheBountyImageMapNode'
    bl_label = 'imagemap'
    # 
    bl_width_min = 225
    
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
class TheBountyMirrorNode(Node, TheBountyMaterialNode):
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

   
class TheBountyNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.space_data.tree_type =='TheBountyMaterialNodeTree' and engine == 'THEBOUNTY'

# all categories in a list
TheBountyMaterialNodeCategories = [
    # identifier, label, items list
    
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
    for bountyclass in bounty_node_class:
        bpy.utils.register_class(bountyclass)
    
def unregister():
    for bountyclass in bounty_node_class:
        bpy.utils.unregister_class(bountyclass)


if __name__ == "__main__":
    register()
