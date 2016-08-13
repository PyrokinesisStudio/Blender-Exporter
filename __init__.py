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
import ctypes


PLUGIN_PATH = os.path.join(__path__[0], 'bin', 'plugins')
BIN_PATH = os.path.join(__path__[0], 'bin')
#sys.path.append(BIN_PATH)
sys.path.insert(0,BIN_PATH)
sys.path.insert(0, BIN_PATH)

#---------------------------------------------------------------        
# The order of libs is very important. Please do not alter it.
#---------------------------------------------------------------
if sys.platform == 'win32':
    for file in os.listdir(BIN_PATH):
        # load dll's from a MSVC build's
        if file in {'yafaraycore.dll'}:
                        'Imath', 'IlmThread', 'IlmImf', 'yafaraycore', 'yafarayplugin']
            break
        # load dll's from a GCC build's
        else:
            dllArray = ['libzlib', 'libiconv-2', 'libxml2', 'libjpeg-8', 'libpng16', 'libtiff-5', \
                        'libfreetype', 'libHalf', 'libIex', 'libIlmThread', 'libImath', \
                        'libIlmImf', 'libyafaraycore', 'libyafarayplugin']

elif sys.platform == 'darwin':
    dllArray = ['libyafaraycore.dylib', 'libyafarayplugin.dylib']

else: # linux
    dllArray = ['libyafaraycore.so', 'libyafarayplugin.so']

# load libraries
for dll in dllArray:
    try:
        ctypes.cdll.LoadLibrary(os.path.join(BIN_PATH, dll))
    except Exception as e:
        print("ERROR: Failed to load library {0}, {1}".format(dll, repr(e)))

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
    prop.register()
    bpy.utils.register_module(__name__)
    
    
def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == '__main__':
    register()
