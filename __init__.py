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
    "version": (0, 1, 6, 0),
    "blender": (2, 7, 2),
    "location": "Info Header > Engine dropdown menu",
    "wiki_url": "https://github.com/TheBounty/Blender-Exporter/wiki",
    "tracker_url": "https://github.com/TheBounty/Blender-Exporter/issues",
    "category": "Render"
}

import sys
import os
import ctypes

#------------------------------------
# find environment for install path
#------------------------------------
def find_bounty_path():
    from os import getenv
    #
    BIN_PATH = "none"
    HOME = getenv('BOUNTY_ROOT','none' )

    if HOME != 'none' and os.path.exists(HOME):
        # c:\TheBounty.. or /home/user/app/TheBounty in Unix 
        BIN_PATH = os.path.join(HOME)
    else:
        # keep the old way: the binaries inside the scripts/addons/folder
        PLUGIN_PATH = os.path.join(__path__[0], 'bin', 'plugins')
        BIN_PATH = os.path.join(__path__[0], 'bin')
        
    return BIN_PATH
#
BIN_PATH = find_bounty_path()

# if bin path is valid..
# you also can use 'if BIN_PATH is not "none"' way
if os.path.exists(BIN_PATH):
    PLUGIN_PATH = BIN_PATH + "/plugins"
    sys.path.append(BIN_PATH)


#---------------------------------------------------------------        
# The order of libs is very important. Please do not alter it.
#---------------------------------------------------------------
if sys.platform == 'win32':
    for file in os.listdir(BIN_PATH):
        # load dll's from a MSVC build's
        if file in {'yafaraycore.dll'}:
            dllArray = ['zlib', 'libiconv', 'libpng16', 'jpeg8','libxml2', \
                        'Half', 'Iex', 'Imath', 'IlmThread', 'IlmImf', \
                        'yafaraycore', 'yafarayplugin']
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

    #-------------------------------------------------------------------------------------
    # add path option on 'User Preferences', based on Corona Exporter and LuxBlend
    #-------------------------------------------------------------------------------------
    class TheBountyAddonPreferences(bpy.types.AddonPreferences):
        # don't remove!! ----------
        bl_idname = __name__
        #--------------------------
        
        install_path = bpy.props.StringProperty(
                name="Path to TheBounty binaries", description="", 
                subtype='DIR_PATH', default=find_bounty_path(),
        )
                
        def draw(self, context):
            layout = self.layout
            layout.prop(self, "install_path")


def register():
    #
    prop.register()
    bpy.utils.register_module(__name__)
    
    
def unregister():   
    
    prop.unregister()  
    bpy.utils.unregister_module(__name__)


if __name__ == '__main__':
    register()
