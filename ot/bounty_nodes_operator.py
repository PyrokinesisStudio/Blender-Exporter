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

    def execute(self, context):
        # create node
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
        nodetree.links.new(nodeOut.inputs[0],shadernode.outputs[0])
        '''
        if material.bounty.mat_type == 'blend':
            shaderOne = nodetree.nodes.new('ShinyDiffuseShaderNode')
            shaderOne.location = [-500, 200]
            nodetree.links.new(shadernode.inputs[0],shaderOne.outputs[0])
            #
            shaderTwo = nodetree.nodes.new('GlossyShaderNode')
            shaderTwo.location = [-500, -200]
            nodetree.links.new(shadernode.inputs[1],shaderTwo.outputs[0])
        '''
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