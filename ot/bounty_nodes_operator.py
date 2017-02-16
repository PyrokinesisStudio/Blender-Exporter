# ---------- BEGIN GPL LICENSE BLOCK -----------------------------------------#
#
#  This file is part of TheBounty exporter for Blender 2.5 and newer
#  Copyright (C) 2010 - 2015 by some Author's
# -----------------------------------------------------------------------------
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
# ---------- END GPL LICENSE BLOCK -------------------------------------------#
'''
Created on 13/05/2014

@author: Pedro
'''
import bpy

light_node_types = {
    'POINT': 'LightPointNode',
    'SPOT' : 'LightSpotNode'
}
op_classes = []

# test for nodetree operator
class TheBountyAddLightNodetree(bpy.types.Operator):
    #
    bl_idname = "bounty.add_lightnodetree"
    bl_label = "Add Light Nodetree"
    bl_description = "Add a node tree linked to this lamp"
    COMPAT_ENGINES = {'THEBOUNTY'}
    
    @classmethod
    def poll(cls, context):
        #
        renderer = context.scene.render.engine
        return (context.lamp and renderer in cls.COMPAT_ENGINES)

    def execute(self, context):
        # create node
        lamp = context.object.data
        nodetree = bpy.data.node_groups.new( lamp.name, 'TheBountyLightNodeTree')
        nodetree.use_fake_user = True
        nodeOut = nodetree.nodes.new("LightOutputNode")
        nodeOut.location = [100, 100]
        lamp.bounty.nodetree = nodetree.name
        lamp.bounty.node_output = nodeOut.name 
        #
        lightnode = nodetree.nodes.new(light_node_types.get(lamp.type))
        lightnode.location = [-200, 0]
        nodetree.links.new(nodeOut.inputs[0],lightnode.outputs[0])
        
        return {'FINISHED'}
#
op_classes.append(TheBountyAddLightNodetree)

#-----------------------------------------------------------------------------------

mat_node_types = {
    'shinydiffusemat' : "ShinyDiffuseShaderNode",
    'glossy'          : "GlossyShaderNode",
    'coated_glossy'   : "GlossyShaderNode",
    'glass'           : "GlassShaderNode",
    'rough_glass'     : "GlassShaderNode",
    'blend'           : "BlendShaderNode",
    'translucent'     : "TranslucentShaderNode",
}
def setNodes(node, mat):
    #
    print('setup node.. ', mat.name)
    #print(node.inputs['Diffuse'].diff_color)
    
    if mat.bounty.mat_type in {'glossy', 'coated_glossy'}:
        node.inputs['Diffuse'].diff_color = mat.diffuse_color
        node.inputs['Glossy'].glossy_color  = mat.bounty.glossy_color
        node.inputs['Specular'].glossy_reflect = mat.bounty.glossy_reflect
        node.inputs['Diffuse'].diffuse_reflect = mat.bounty.diffuse_reflect
    #
    elif mat.bounty.mat_type == 'shinydiffusemat':
        #
        node.inputs['Diffuse'].diff_color = mat.diffuse_color
        node.inputs['Mirror'].mirror_color = mat.bounty.mirror_color
        node.inputs['Translucency'].translucency = mat.bounty.translucency
        node.inputs['Transparency'].transparency = mat.bounty.transparency
        node.inputs['Diffuse'].diffuse_reflect = mat.bounty.diffuse_reflect
        node.inputs['Specular'].specular_reflect = mat.bounty.specular_reflect
        node.fresnel_effect = mat.bounty.fresnel_effect
        node.IOR_reflection = mat.bounty.IOR_reflection
        node.transmit = mat.bounty.transmit_filter
        node.emittance = mat.bounty.emittance
        node.brdf_type = mat.bounty.brdf_type
        node.sigma = mat.bounty.sigma
                                          
    elif mat.bounty.mat_type == 'blend':
        node.blend_amount = mat.bounty.blend_value
        
    elif mat.bounty.mat_type == 'translucent':
        #
        node.exponent = mat.bounty.exponent
        node.sssSigmaS = mat.bounty.sssSigmaS
        node.sssSigmaS_factor = mat.bounty.sssSigmaS_factor
        node.phaseFuction = mat.bounty.phaseFuction
        node.sssSigmaA = mat.bounty.sssSigmaA
        node.sss_transmit = mat.bounty.sss_transmit
        node.sssIOR = mat.bounty.sssIOR
        node.inputs['Diffuse'].diff_color = mat.diffuse_color 
        node.inputs['Diffuse'].diffuse_reflect = mat.bounty.diffuse_reflect
        node.inputs['Glossy Color'].glossy_color = mat.bounty.glossy_color
        node.inputs[2].mirror_color = mat.bounty.sssSpecularColor
    
    return        


# test for nodetree operator
class TheBountyAddMaterialNodetree(bpy.types.Operator):
    #
    bl_idname = "bounty.add_nodetree"
    bl_label = "Add TheBounty Nodetree"
    bl_description = "Add a node tree linked to this material"
    COMPAT_ENGINES = {'THEBOUNTY'}
    
    @classmethod
    def poll(cls, context):
        #
        renderer = context.scene.render.engine
        return (context.material and renderer in cls.COMPAT_ENGINES)
    
    def addNode(self, material):
        pass
    
    
    def execute(self, context):
        # create node tree
        material = context.object.active_material
        nodetree = bpy.data.node_groups.new( material.name, 'TheBountyMaterialNodeTree')
        nodetree.use_fake_user = True
        nodeOut = nodetree.nodes.new("MaterialOutputNode")
        nodeOut.location = [100, 100]
        material.bounty.nodetree = nodetree.name
        material.bounty.node_output = nodeOut.name 
        #
        shadernode = nodetree.nodes.new(mat_node_types.get(material.bounty.mat_type))
        shadernode.location = [-200, 0]
        nodetree.links.new(nodeOut.inputs[0], shadernode.outputs[0])
        #
        mat = bpy.data.materials[material.name]
        setNodes(shadernode, mat)
        
        if material.bounty.mat_type == 'blend':
            #
            mat1 = bpy.data.materials[ material.bounty.blendOne if material.bounty.blendOne !="" else 'blendone']            
            shaderOne = nodetree.nodes.new(mat_node_types.get(mat1.bounty.mat_type))
            shaderOne.location = [-500, 200]
            nodetree.links.new(shadernode.inputs[0], shaderOne.outputs[0])
            setNodes(shaderOne, mat1)
            
            #
            mat2 = bpy.data.materials[ material.bounty.blendTwo if material.bounty.blendTwo !="" else 'blendtwo']
            shaderTwo = nodetree.nodes.new(mat_node_types.get(mat2.bounty.mat_type))
            shaderTwo.location = [-500, -200]
            nodetree.links.new(shadernode.inputs[1], shaderTwo.outputs[0])
            setNodes(shaderTwo, mat2)
        
        return {'FINISHED'}
#
#
op_classes.append(TheBountyAddMaterialNodetree)
#
def register():
    for clas in op_classes:
        bpy.utils.register_class(clas)
    

def unregister():
    for cls in op_classes:
        bpy.utils.unregister_class(clas)


if __name__ == '__main__':
    pass