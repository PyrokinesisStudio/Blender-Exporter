# ---------- BEGIN GPL LICENSE BLOCK -----------------------------------------#
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
# ---------- END GPL LICENSE BLOCK -------------------------------------------#
'''
Created on 13/05/2014

@author: Pedro
'''
import bpy

# test for nodetree operator
class TheBountyAddNodetree(bpy.types.Operator):
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
        nodetree = bpy.data.node_groups.new( material.name, 'TheBountyNodeTree')
        nodetree.use_fake_user = True
        node = nodetree.nodes.new("MaterialOutputNode")
        material.bounty.nodetree = nodetree.name
        material.bounty.node_output = node.name      
        
        return {'FINISHED'}


if __name__ == '__main__':
    pass