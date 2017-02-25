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

from . import prop_node_sockets
#
import nodeitems_utils
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
    MatNodeTypes = {}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'THEBOUNTY'
    
    # code orignally from Matt Ebb's 3Delight exporter   
    @classmethod
    def get_from_context(cls, context):
        #        
        ob = context.active_object
        if ob and ob.type not in {'LAMP', 'CAMERA'}:
            mat = ob.active_material
            if mat != None: 
                nt_name = mat.bounty.nodetree
                if nt_name != '':
                    return bpy.data.node_groups[nt_name], ob, mat #mat.bounty.nodetree], ob, mat
                
        return (None, None, None)
        
    # This block updates the preview, when socket links change
    def update(self):
        self.refresh = True
    
    def acknowledge_connection(self, context):
        while self.refresh == True:
            self.refresh = False
            break
    
    refresh = bpy.props.BoolProperty(
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
    params={}
      
    @classmethod
    def poll( cls, context):
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
    
    '''
    def traverse_node_tree(self, material_node):
        #
        for socket in self.inputs:
            if socket.is_linked:
                linked_node = socket.links[0].from_node
                linked_node.traverse_node_tree( material_node)
        #material_node.listedNodes.append(self)
    '''
   
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
    listedNodes = []
    params={}

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
        
    def getParams(self):
        #
        self.params.set()
        if self.inputs['Surface'].is_linked:
            input = self.inputs['Surface'].links[0].from_node
            linked_node = socket.links[0].from_node
            if input in validShaderTypes:
                self.params = input.getParams()
            else:
                bpy.data.node_groups[mat.bounty.nodetree].links.remove(inputNodeOut.links[0])
        #
        return self.params
    
bounty_node_class.append(TheBountyMaterialOutputNode)
        
#------------------------------------------------
# Shinydiffuse node
#------------------------------------------------           
class TheBountyShinyDiffuseShaderNode(Node, TheBountyMaterialNode):
    bl_idname = 'ShinyDiffuseShaderNode'
    bl_label = 'shinydiffusemat'
    bl_icon = 'MATERIAL'
    shinyparams = {}
    #
    diffuse_reflect = MatProperty.diffuse_reflect
    fresnel_effect = MatProperty.fresnel_effect
    IOR_reflection = MatProperty.IOR_reflection
    transmit = MatProperty.transmit_filter
    diffuse_brdf = MatProperty.brdf_type
    emittance = MatProperty.emittance
    sigma = MatProperty.sigma
         
    #
    def init(self, context):
        # slots shaders
        self.outputs.new('NodeSocketShader', "Shader")
        
        self.inputs.new('diffuse_color', 'Diffuse')
        
        self.inputs.new('transparency', 'Transparency')
        
        self.inputs.new('translucency', 'Translucency')
        
        self.inputs.new('mirror', 'Mirror')
        
        self.inputs.new('specular', 'Specular')
        
        self.inputs.new('bumpmap', 'Bumpmap')
    
    def draw_buttons(self, context, layout):
        # Additional buttons displayed on the node.        
        #mat = context.active_object.active_material
        
        col = layout.column()
        col.prop(self, "transmit", slider=True)
        col.prop(self, "emittance", slider=True)
        col.prop(self, "diffuse_brdf")
        sig = layout.column()
        sig.enabled = self.diffuse_brdf != 'lambert'
        sig.prop(self, "sigma", text='Sigma', slider=True)
        col = layout.column()
        col.prop(self, "fresnel_effect", toggle=True)
        col.prop(self, "IOR_reflection")
        col.prop(self, "diffuse_reflect", text="Diffuse reflect")        
    
    def getParams(self):
        #
        self.shinyparams['transparency'] = self.inputs['Transparency'].getParams()
        self.shinyparams['translucency'] = self.inputs['Translucency'].getParams()
        self.shinyparams['specular_reflect'] = self.inputs['Specular'].getParams()
        self.shinyparams['diffuse_color']= self.inputs['Diffuse'].getParams()
        self.shinyparams['mirror_color'] = self.inputs['Mirror'].getParams()
        self.shinyparams['Bumplayer'] = self.inputs['Bumpmap'].getParams()
        #
        self.shinyparams['fresnel_effect'] = self.fresnel_effect
        self.shinyparams['diffuse_brdf'] = self.diffuse_brdf
        self.shinyparams['transmit_filter'] = self.transmit
        self.shinyparams['IOR'] = self.IOR_reflection
        self.shinyparams['emit'] = self.emittance
        self.shinyparams['sigma'] = self.sigma        
        
        return self.shinyparams   
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
    sssparams = {}
    #
    sssSigmaS_factor = MatProperty.sssSigmaS_factor
    diffuse_reflect = MatProperty.diffuse_reflect
    sss_transmit = MatProperty.sss_transmit
    phaseFuction = MatProperty.phaseFuction
    sssPresets = MatProperty.sss_presets
    sssSigmaA = MatProperty.sssSigmaA
    sssSigmaS = MatProperty.sssSigmaS
    exponent = MatProperty.exponent
    sssIOR = MatProperty.sssIOR
    
    #
    def init(self, context):
        # slots shaders
        self.outputs.new('NodeSocketShader', "Shader")
        
        self.inputs.new('absorption_color', 'Absorption') # absorption
        
        self.inputs.new('scatter_color', 'Scattering')  # scattering         
        
        self.inputs.new('diffuse_color', "Diffuse")
        
        self.inputs.new('glossy_color', "Glossy")
        
        self.inputs.new('glossy_reflect', 'Specular')
        
        self.inputs.new('bumpmap', 'Bumpmap')
        
        
    def draw_buttons(self, context, layout):
        #
        #mat = context.active_object.active_material
                
        col = layout.column()
        col.prop(self, "sssPresets", text="Presets")     
        col.prop(self, "exponent", text="Spec. Exponent")
        #col.prop(self, "sssSigmaS", text="Scatter (SigmaS)")
        col.prop(self, "sssSigmaS_factor")
        col.prop(self, "phaseFuction")       
        #col.prop(self, "sssSigmaA", text="Absorption (SigmaA)")
        col.prop(self, "sss_transmit", text="Translucency")
        col.prop(self, "sssIOR")
        col.prop(self, "diffuse_reflect", text="Diffuse reflect")   
        
    def getParams(self):
        #
        self.sssparams['absorption_color'] = self.inputs['Absorption'].getParams()
        self.sssparams['scatter_color'] = self.inputs['Scattering'].getParams()
        self.sssparams['glossy_reflect'] = self.inputs['Specular'].getParams()
        self.sssparams['diffuse_color']= self.inputs['Diffuse'].getParams()
        self.sssparams['glossy_color'] = self.inputs['Glossy'].getParams()        
        self.sssparams['Bumplayer'] = self.inputs['Bumpmap'].getParams()
        
        return self.sssparams
#
bounty_node_class.append(TheBountyTranslucentShaderNode)

#------------------------------------------------
# Glossy node 
#------------------------------------------------
class TheBountyGlossyShaderNode(Node, TheBountyMaterialNode):
    bl_idname = 'GlossyShaderNode'
    bl_label = 'glossy'
    bl_icon = 'MATERIAL'    
    
    # properties
    diffuse_reflect = MatProperty.diffuse_reflect   
    IOR_reflection = MatProperty.IOR_reflection
    coat_mir_col = MatProperty.coat_mir_col
    anisotropic = MatProperty.anisotropic
    as_diffuse = MatProperty.as_diffuse
    brdf_type = MatProperty.brdf_type
    exponent = MatProperty.exponent
    exp_u = MatProperty.exp_u
    exp_v = MatProperty.exp_v
    sigma = MatProperty.sigma
    
    def draw_buttons(self, context, layout):
        #
        mat = context.active_object.active_material
        
        col = layout.column()
        col.prop(self, "brdf_type")
        sig = col.column()
        sig.enabled = self.brdf_type != 'lambert'
        sig.prop(self, "sigma", text='Sigma', slider=True)
        exp = col.column()
        exp.enabled = not self.anisotropic
        exp.prop(self, "exponent")

        sub = col.column(align=True)
        sub.prop(self, "anisotropic")
        ani = sub.column()
        ani.enabled = self.anisotropic
        ani.prop(self, "exp_u")
        ani.prop(self, "exp_v")
        layout.prop(self, "as_diffuse")

        layout.separator()

        if mat.bounty.mat_type == "coated_glossy":
            col = layout.column()
            col.prop(self, "coat_mir_col")
            col.prop(self, "IOR_reflection")
        
        col = layout.column()    
        col.prop(self, "diffuse_reflect", text="Diffuse reflect")  
        
    def init(self, context):
        #
        self.outputs.new('NodeSocketShader', "Shader")
        
        self.inputs.new('diffuse_color',"Diffuse")        
        self.inputs.new('glossy_color',"Glossy")
        self.inputs.new('glossy_reflect',"Specular")
        self.inputs.new('bumpmap', 'Bumpmap')
    
     
#
bounty_node_class.append(TheBountyGlossyShaderNode)

#------------------------------------------------
# Glass shader node
#------------------------------------------------                      
class TheBountyGlassShaderNode(Node, TheBountyMaterialNode):
    bl_idname = 'GlassShaderNode'
    bl_label = 'glass'
    bl_icon = 'MATERIAL'
    glassparams = {}
    
    # properties..
    dispersion_power = MatProperty.dispersion_power
    absorption_dist = MatProperty.absorption_dist
    refr_roughness = MatProperty.refr_roughness
    IOR_refraction = MatProperty.IOR_refraction
    glass_transmit = MatProperty.glass_transmit
    filter_color = MatProperty.filter_color
    fake_shadows = MatProperty.fake_shadows
    absorption = MatProperty.absorption
    
    

    def init(self, context):
        #
        self.outputs.new('NodeSocketShader', "Shader")
        # add only connectable slots
        self.inputs.new('glass_mir_col', 'Mirror')
        self.inputs.new('bumpmap', 'Bumpmap')

    def draw_buttons(self, context, layout):
        """ Same design to a UI panels ( column, split, row..) """
        mat = context.active_object.active_material        
        col = layout.column()
        
        col.prop(self, "absorption")
        col.prop(self, "absorption_dist", text='Distance')
        col.prop(self, "dispersion_power", text='Dispersion power')
        if mat.bounty.mat_type == "rough_glass":
            col = layout.column()
            col.prop(self, "refr_roughness", text="Roughness exponent", slider=True)
        col.prop(self, "filter_color")
        col.prop(self, "glass_transmit", slider=True)
        col.prop(self, "fake_shadows")
        col.prop(self, "IOR_refraction")
    #
    def getParams(self):
        #
        self.glassparams['Mirror']= self.inputs['Mirror'].getParams()
        #self.glassparams['Bumpmap'] = self.inputs['Bumpmap'].getParams()
        return self.glassparams
#
bounty_node_class.append(TheBountyGlassShaderNode)

#------------------------------------------------
# Blend shader node
#------------------------------------------------
class TheBountyBlendShaderNode(Node, TheBountyMaterialNode):
    bl_idname = 'BlendShaderNode'
    bl_label = 'blend'
    bl_icon = 'MATERIAL'
    
    blend_amount = MatProperty.blend_value
    BlendOne = MatProperty.blendOne
    BlendTwo = MatProperty.blendTwo
    
    def init(self, context):
        # outputs
        self.outputs.new('NodeSocketShader', "Shader")
        
        self.inputs.new('NodeSocketShader', "blendOne")
        self.inputs.new('NodeSocketShader', "blendTwo")
        

    def draw_buttons(self, context, layout):
        #
        mat = context.active_object.active_material
        
        layout.prop_search(mat.bounty, 'blendOne', bpy.data, 'materials', text='')
        
        layout.prop(self, "blend_amount", text="", slider=True)
        
        layout.prop_search(mat.bounty, 'blendTwo', bpy.data, 'materials', text='')
        
        layout.operator('material.sync_blend', text='Sync mat slots')
#
bounty_node_class.append(TheBountyBlendShaderNode)

       
#------------------------------------------------
# Imagemap node
#------------------------------------------------
from ..prop.tby_texture import TheBountyTextureProperties as TexProperty

class TheBountyImageMapNode(Node, TheBountyMaterialNode):
    #
    bl_idname = 'TheBountyImageMapNode'
    bl_label = 'Image'
    bl_width_min = 225
    textParams={}
    
    # reuse properties
    projection_type = TexProperty.projection_type
    texture_coord = TexProperty.texture_coord
    image_map = TexProperty.image_map
    influence = TexProperty.influence
    mapping_x = TexProperty.mapping_x
    mapping_y = TexProperty.mapping_y
    mapping_z = TexProperty.mapping_z
    offset = TexProperty.offset
    scale = TexProperty.scale
    #
    blend = TexProperty.blend
    negative = TexProperty.negative
    no_rgb = TexProperty.no_rgb
    stencil = TexProperty.stencil
    # test
    default_value = TexProperty.zero_to_one
    from_dupli = TexProperty.bool_option
    
    def init(self, context):
        self.outputs.new('NodeSocketColor', 'Color')
        
    def draw_buttons(self, context, layout):
        #
        layout.prop_search(self, 'image_map', bpy.data, "images")
        layout.prop(self, 'influence', text='Texture Influence', slider=True)
        # blending
        row = layout.row()
        row.prop(self, 'blend')
        row.prop(self, 'negative')
        row = layout.row()
        row.prop(self, 'no_rgb')
        row.prop(self, 'stencil')
        layout.prop(self, 'default_value', text='Default value', slider=True)
        
        layout.label('Texture Mapping')
        layout.prop(self, 'texture_coord', text='Coordinates')
        layout.prop(self, 'projection_type')
        row = layout.row()
        row.prop(self, 'from_dupli', text='Dupli', toggle=True)
        row.prop(self, 'mapping_x', text='')
        row.prop(self, 'mapping_y', text='')
        row.prop(self, 'mapping_z', text='')
        row = layout.row()
        col = row.column(align=True)
        col.label('Offset')
        col.prop(self, 'offset', text='')        
        col = row.column(align=True)
        col.label('Scale')
        col.prop(self, 'scale', text='')
    
    
    def getParams(self):
        #
        self.textParams['projection_type'] = self.projection_type
        self.textParams['texture_coord'] = self.texture_coord
        self.textParams['offset'] = [ o for o in self.offset]
        self.textParams['scale'] = [s for s in self.scale]
        self.textParams['mapping_x'] = self.mapping_x
        self.textParams['mapping_y'] = self.mapping_y
        self.textParams['mapping_z'] = self.mapping_z
        #
        self.textParams['negative'] = self.negative
        self.textParams['stencil'] = self.stencil
        self.textParams['no_rgb'] = self.no_rgb
        self.textParams['blend'] = self.blend
        #
        return self.textParams
    
bounty_node_class.append(TheBountyImageMapNode)
    
class TheBountyNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (context.space_data.tree_type =='TheBountyMaterialNodeTree' and engine == 'THEBOUNTY')


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
