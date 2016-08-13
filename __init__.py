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

bl_info = {
    "name": "TheBounty Render Engine",
    "description": "TheBounty Renderer integration for Blender",
    "author": "Pedro Alcaide (povmaniaco), rubdos, TynkaTopi, paultron",
    "version": (0, 1, 6, 4),
    "blender": (2, 77, 0),
    "location": "Info Header > Engine dropdown menu",
    "wiki_url": "https://github.com/TheBounty/Blender-Exporter/wiki",
    "tracker_url": "https://github.com/TheBounty/Blender-Exporter/issues",
    "category": "Render"
}

import sys
import os
#import ctypes


PLUGIN_PATH = os.path.join(__path__[0], 'bin', 'plugins')
BIN_PATH = os.path.join(__path__[0], 'bin')
#sys.path.append(BIN_PATH)
sys.path.insert(0,BIN_PATH)

#--------------------------
# import exporter modules
#--------------------------
if "bpy" in locals():
    import imp
    imp.reload(prop)
    imp.reload(io)
    imp.reload(ui)
    imp.reload(ot)
else:
    import bpy
    from . import prop
    from . import io
    from . import ui
    from . import ot

def register():
    #
    nodeitems_utils.register_node_categories("THEBOUNTY_MATERIAL_NODES", ui.prop_material_nodes.TheBountyMaterialNodeCategories)
    nodeitems_utils.register_node_categories("THEBOUNTY_LIGHT_NODES", ui.prop_light_nodes.TheBountyLightNodeCategories)
     
    prop.register()
    bpy.utils.register_module(__name__)
    
    
def unregister():
    #
    nodeitems_utils.unregister_node_categories("THEBOUNTY_MATERIAL_NODES")
    nodeitems_utils.unregister_node_categories("THEBOUNTY_LIGHT_NODES")
    bpy.utils.unregister_module(__name__)

if __name__ == '__main__':
    register()
