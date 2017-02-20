#-------------------------------------------------------------------------#
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
# -------------------------------------------------------------------------#


import bpy
from bpy.types import Panel, Menu

class TheBountySceneButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    COMPAT_ENGINES = {'THEBOUNTY'}
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.scene and (engine in cls.COMPAT_ENGINES)

class TheBounty_PT_project(TheBountySceneButtonsPanel, Panel):
    bl_label = "TheBounty Project settings"
    #COMPAT_ENGINES = {'THEBOUNTY'}

    def draw(self, context):
        layout = self.layout

        #scene = context.scene
        bounty = context.scene.bounty
        layout.label("Project settings values (W.I.P)")
        row=layout.row()
        row.prop(bounty, "gs_gamma_input")
        row.prop(bounty, "gs_gamma", text='Gamma Out')
        sub = layout.row()
        sub.enabled = bounty.gs_gamma_input > 1.0
        sub.prop(bounty, "sc_apply_gammaInput", text="Apply Gamma correction", toggle=True)

from bl_ui import properties_scene as prop_scene
for member in dir(prop_scene):  # add all "object" panels from blender
    subclass = getattr(prop_scene, member)
    try:
        subclass.COMPAT_ENGINES.add('THEBOUNTY')
        subclass.bl_options = {'DEFAULT_CLOSED'}
    except:
        pass
del prop_scene


if __name__ == "__main__":  # only for live edit.
    bpy.utils.register_module(__name__)