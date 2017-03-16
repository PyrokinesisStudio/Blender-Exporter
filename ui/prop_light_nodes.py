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
#from bpy.props import (FloatProperty, FloatVectorProperty, StringProperty, BoolProperty, EnumProperty)

from . import prop_node_sockets
#
from nodeitems_utils import NodeCategory, NodeItem, NodeItemCustom

from ..prop.tby_light import TheBountyLightProperties as LightProperty
#------------------------------------------------------

def fixNodeSize(nmin, nmax):
    bl_width_min = nmin
    bl_width_max = nmax

bounty_light_node_class=[]
#
class TheBountyLampNodeTree(bpy.types.NodeTree):
    #    
    bl_idname = 'TheBountyLightNodeTree'
    bl_label = 'TheBounty Light NodeTree'
    bl_icon = 'LAMP'

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'THEBOUNTY'
    
    # code orignally from Matt Ebb's 3Delight exporter   
    @classmethod
    def get_from_context(cls, context):
        
        ob = context.active_object
        #
        if ob and ob.type == 'LAMP':
            lamp = ob.data
            #lightree_name = lamp.bounty.lightree
            if lamp.bounty.lightree != '':
                return bpy.data.node_groups[lamp.bounty.lightree], lamp, lamp
                
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
bounty_light_node_class.append(TheBountyLampNodeTree)

''' TheBounty node class base declaration
'''  
class TheBountyLightNode:
    # test for lock node sizes
    #bl_width_min = bl_width_max = 180
      
    @classmethod
    def poll( cls, context):
        #
        engine = context.scene.render.engine 
        return (context.bl_idname == "TheBountyLightNodeTree" and engine == 'THEBOUNTY')

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
    def traverse_node_tree(self, light_node):
        #
        for socket in self.inputs:
            if socket.is_linked:
                linked_node = socket.links[0].from_node
                linked_node.traverse_node_tree( light_node)
                break
        light_node.listedNodes.append(self)    
#
bounty_light_node_class.append(TheBountyLightNode)


#------------------------------------------------
# Light Output node
#------------------------------------------------
class TheBountyLightOutputNode(Node, TheBountyLightNode):
    bl_idname = 'LightOutputNode'
    bl_label = 'Output Light'
    bl_icon = 'NODETREE'
    #bl_width_min = 120
    #bl_width_max = 130
    #
    listedNodes = []
    preview = bpy.props.BoolProperty(name='Preview', default=False)

    def init(self, context):
        self.inputs.new('NodeSocketShader', "Light")        
    
    def draw_buttons(self, context, layout):
        #
        layout.label(context.object.data.name)
        layout.prop(self, 'preview')
        if self.preview:
            layout.template_preview(context.object.data, show_buttons=True)
    #
    def filterNodeList(self, nodes):
        nodeList = []
        for node in nodes:
            if node not in nodeList:
                nodeList.append( node)
        return nodeList
    #
    def traverse_node_tree(self):
        #
        self.listedNodes.clear()
        for socket in self.inputs:
            if socket.is_linked:
                linked_node = socket.links[0].from_node
                linked_node.traverse_node_tree(self)
        #
        return self.filterNodeList(self.listedNodes)  
#
bounty_light_node_class.append(TheBountyLightOutputNode)

class TheBountyLightPreviewNode(Node, TheBountyLightNode):
    bl_idname = 'LightPreviewNode'
    bl_label = 'Preview Light'
    bl_icon = 'NODETREE'
    #bl_width_min = 120
    #bl_width_max = 130
    #
    listedNodes = []

    def init(self, context):
        self.inputs.new('NodeSocketShader', "Light")        
    
    def draw_buttons(self, context, layout):
        #try:
        layout.label(context.object.data.name)
        layout.template_preview(context.object.data)
        
bounty_light_node_class.append(TheBountyLightPreviewNode)


class TheBountyLightPointNode(Node, TheBountyLightNode):
    bl_idname = 'LightPointNode'
    bl_label = 'POINT'
    bl_icon = 'NODETREE'
    
    energy = LightProperty.energy
    samples = LightProperty.samples
    use_sphere = LightProperty.use_sphere
    sphere_radius = LightProperty.sphere_radius
    create_geometry = LightProperty.create_geometry
       
    #
    def init(self, context):
        # slots shaders
        self.outputs.new('NodeSocketColor', "Light")        
    
    def draw_buttons(self, context, layout):
        # Additional buttons displayed on the node.
        lamp = context.object.data
        layout.prop(lamp, "color")
        layout.prop(self, "energy", text="Power")
        col = layout.column(align=True)
        col.prop(self, "use_sphere", toggle=True)
        if lamp.use_sphere:
            col.prop(self, "sphere_radius")
            col.prop(self, "samples")
            col.prop(self, "create_geometry", toggle=True)
#
bounty_light_node_class.append(TheBountyLightPointNode)
            

class TheBountySpotLightNode(Node, TheBountyLightNode):
    bl_idname = 'LightSpotNode'
    bl_label = 'SPOT'
    bl_icon = 'NODETREE'
    
    #
    samples = LightProperty.samples
    ies_file = LightProperty.ies_file
    photon_only = LightProperty.photon_only
    show_dist_clip = LightProperty.show_dist_clip
    shadow_fuzzyness = LightProperty.shadow_fuzzyness
    spot_soft_shadows = LightProperty.spot_soft_shadows
    
    #
    def init(self, context):
        # slots shaders
        self.outputs.new('NodeSocketColor', "Light")
        self.inputs.new('color', 'Color')        
    
    def draw_buttons(self, context, layout):
        # Additional buttons displayed on the node.
        lamp = context.object.data
        
        layout.prop(self, "ies_file")
        if self.ies_file =="":
            layout.prop(self, "photon_only", toggle=True)
        col = layout.column(align=True)
        if not lamp.bounty.photon_only:
            col.prop(self, "spot_soft_shadows", text= 'Soft Shadows', toggle=True)
            if self.spot_soft_shadows:
                col.prop(self, "samples")
                if self.ies_file =="":
                    col.prop(self, "shadow_fuzzyness")
        #
        if lamp.bounty.ies_file =="":
                self.draw_spot_shape(layout, lamp)
                    
    def draw_spot_shape(self, layout, lamp):
        #        
        layout.label("Spot shape settings:")
        
        col = layout.column(align=True)
        col.prop(lamp, "spot_size", text="Size", slider=True)
        col.prop(lamp, "spot_blend", text="Blend", slider=True)
        #        
        col = layout.column(align=True)
        col.prop(lamp, "show_cone", toggle=True)
        col.prop(lamp.bounty, "show_dist_clip", toggle=True)
        if lamp.bounty.show_dist_clip:
            col.prop(lamp, "distance")
            col.prop(lamp, "shadow_buffer_clip_start", text="Clip Start")
            col.prop(lamp, "shadow_buffer_clip_end", text=" Clip End")
    
#
bounty_light_node_class.append(TheBountySpotLightNode)

# our own base class with an appropriate poll function,
# so the categories only show up in our own tree type
class TheBountyLightNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.space_data.tree_type =='TheBountyLightNodeTree' and engine == 'THEBOUNTY'
#
bounty_light_node_class.append(TheBountyLightNodeCategory)
   
# Light categories in a list
TheBountyLightNodeCategories = [
    # identifier, label, items list
    TheBountyLightNodeCategory("TheBountyLight", "Out Light", items=[
        # output node
        NodeItem(TheBountyLightOutputNode.bl_idname),
        ]),
    TheBountyLightNodeCategory("TheBountyLightNodes", "Lights", items=[
        NodeItem(TheBountySpotLightNode.bl_idname),
        NodeItem(TheBountyLightPointNode.bl_idname),
        ]),
]

def register():
    for light_class in bounty_light_node_class:
        bpy.utils.register_class(light_class)
    
def unregister():
    for light_class in bounty_light_node_class:
        bpy.utils.unregister_class(light_class)


if __name__ == "__main__":
    register()


