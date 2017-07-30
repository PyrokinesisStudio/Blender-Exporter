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
    "version": (0, 1, 7, 0),
    "blender": (2, 78, 0),
    "location": "Info Header > Engine dropdown menu",
    "wiki_url": "https://github.com/TheBounty/Blender-Exporter/wiki",
    "tracker_url": "https://github.com/TheBounty/Blender-Exporter/issues",
    "category": "Render",
    "branch": "0.1.7.dev"
}

import sys
import os



BIN_PATH = os.path.join(__path__[0], 'bin') # os.environ['BOUNTY_ROOT']
sys.path.insert(0,BIN_PATH)
    
os.environ['PATH'] = BIN_PATH + ';' + os.environ['PATH']
    
PLUGIN_PATH = BIN_PATH + '/plugins'
   

#--------------------------
# import exporter modules
#--------------------------
if "prop" in locals():
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
    prop.register()
    bpy.utils.register_module(__name__)


def unregister():

    prop.unregister()
    bpy.utils.unregister_module(__name__)


if __name__ == '__main__':
    register()
