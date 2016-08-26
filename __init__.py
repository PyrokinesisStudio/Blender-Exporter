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
        # c:\TheBounty.. or /home/user/app/TheBounty in unix 
        BIN_PATH = os.path.join(HOME)
    else:
        # keep the old way: the binaries inside the scripts/addons/folder
        PLUGIN_PATH = os.path.join(__path__[0], 'bin', 'plugins')
        BIN_PATH = os.path.join(__path__[0], 'bin')
        
    return BIN_PATH
#
BIN_PATH = find_bounty_path()
# if bin path is valid..
# you also can use if BIN_PATH is not "none":
if os.path.exists(BIN_PATH):
    PLUGIN_PATH = BIN_PATH + "/plugins"
    sys.path.append(BIN_PATH)

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
#---------------------------------------------------------------        
# The order of libs is very importante. Please do not alter it.
#---------------------------------------------------------------
if sys.platform == 'win32':
    for file in os.listdir(BIN_PATH):
        # load dll's from a MSVC build's
        if file in {'yafaraycore.dll'}:
            dllArray = ['zlib', 'libiconv', 'zlib', 'libpng16', 'libxml2', 'Half', 'Iex', \
                        'Imath', 'IlmThread', 'IlmImf', 'yafaraycore', 'yafarayplugin','opencl_wrapper']
            break
        # load dll's from a GCC build's
        else:
            dllArray = ['zlib', 'libxml2-2', 'libgcc_s_sjlj-1', 'Half', 'Iex', 'Imath', \
                        'IlmThread', 'IlmImf', 'libjpeg-8', 'libpng14', 'libtiff-3', \
                        'libfreetype-6', 'libstdc++-6', 'libyafaraycore', 'libyafarayplugin']

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

#---------------------------------------------
# this code is only for development purposes
# a bit hardcoded design, but work in al OS
#---------------------------------------------
EXP_BRANCH = (("master"),("custom_nodes"),('opencl'),)

for file in os.listdir(PLUGIN_PATH):
    if file[:13]=='libGridVolume' or file[:10]=='GridVolume':
        EXP_BRANCH +=(("volumegrid"),)
        
    if file[:14]=='libtranslucent' or file[:11]=='translucent':
        EXP_BRANCH +=(("merge_SSS"),)
        
    if file[:8]=='photonic' or file[:8]=='directic':
        EXP_BRANCH +=(("irrcache"),)

if 'custom_nodes' in EXP_BRANCH:
    import nodeitems_utils

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
    from bpy.app.handlers import persistent
    from . import prop
    from . import io
    from . import ui
    from . import ot

    #-------------------------------------------------------------------------------------
    # add path option on 'User Preferences', inspired on Corona Exporter and LuxBlend
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

'''
@persistent
def load_handler(dummy):
    for tex in bpy.data.textures:
        if tex is not None:
            # set the correct texture type on file load....
            # converts old files, where propertie yaf_tex_type wasn't defined
            print("Load Handler: Convert old texture \"{0}\" with texture type: \"{1}\" to \"{2}\"".format(tex.name, tex.yaf_tex_type, tex.type))
            tex.yaf_tex_type = tex.type
    # convert image output file type setting from blender to yafaray's file type setting on file load, so that both are the same...
    if bpy.context.scene.render.image_settings.file_format is not bpy.context.scene.bounty.img_output:
        bpy.context.scene.bounty.img_output = bpy.context.scene.render.image_settings.file_format

'''
def register():
    #
    prop.register()
    bpy.utils.register_module(__name__)
    if "custom_nodes" in EXP_BRANCH:
        nodeitems_utils.register_node_categories("TheBountyMaterial", ui.prop_custom_nodes.TheBountyNodeCategories)    
    
    #bpy.app.handlers.load_post.append(load_handler)
    #------------------------------------
    # register keys for own render modes
    #------------------------------------
    km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name='TheBounty')
    kmi = km.keymap_items.new('bounty.render_view', 'F12', 'PRESS', False, False, False, True)
    kmi = km.keymap_items.new('bounty.render_animation', 'F12', 'PRESS', False, False, True, False)
    kmi = km.keymap_items.new('bounty.render_still', 'F12', 'PRESS', False, False, False, False)    
    

def unregister():
    #--------------------------------------   
    # unregister keys for own render modes
    #--------------------------------------
    kma = bpy.context.window_manager.keyconfigs.addon.keymaps['TheBounty']
    print("#---- Unregister keymaps ----")
    for kmi in kma.keymap_items:
        print(kmi.idname)
        kma.keymap_items.remove(kmi)
    print("#----------------------------")
            
    #bpy.app.handlers.load_post.remove(load_handler)
    
    if "custom_nodes" in EXP_BRANCH:
        nodeitems_utils.unregister_node_categories("TheBountyMaterial")
    
    prop.unregister()  
    bpy.utils.unregister_module(__name__)


if __name__ == '__main__':
    register()
