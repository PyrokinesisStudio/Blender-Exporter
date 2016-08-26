# -------------------------------------------------------------------------#
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
#from bl_ui.properties_scene import SceneButtonsPanel


class TheBountySceneButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    COMPAT_ENGINES = {'THEBOUNTY'}

    @classmethod
    def poll(cls, context):
        rd = context.scene.render
        return context.scene and (rd.engine in cls.COMPAT_ENGINES)

class TheBounty_PT_project(TheBountySceneButtonsPanel, Panel):
    bl_label = "TheBounty Project settings"
    COMPAT_ENGINES = {'THEBOUNTY'}

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

class TheBounty_PT_scene(TheBountySceneButtonsPanel, Panel):
    bl_label = "Scene"
    COMPAT_ENGINES = {'THEBOUNTY'}

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        layout.prop(scene, "camera")
        #layout.prop(scene, "background_set", text="Background")
        layout.prop(scene, "active_clip", text="Active Clip")

class TheBounty_PT_unit(TheBountySceneButtonsPanel, Panel):
    bl_label = "Units"
    COMPAT_ENGINES = {'THEBOUNTY'}

    def draw(self, context):
        layout = self.layout

        unit = context.scene.unit_settings

        col = layout.column()
        col.row().prop(unit, "system", expand=True)
        col.row().prop(unit, "system_rotation", expand=True)

        if unit.system != 'NONE':
            row = layout.row()
            row.prop(unit, "scale_length", text="Scale")
            row.prop(unit, "use_separate")
            

class TheBounty_PT_color_management(TheBountySceneButtonsPanel, Panel):
    bl_label = "Color Management"
    bl_options = {'DEFAULT_CLOSED'}
    COMPAT_ENGINES = {'THEBOUNTY'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        #rd = scene.render
        col = layout.column()
        col.label(text="Display color space:")
        col.prop(scene.display_settings, "display_device", text= "Device")

        col = layout.column()
        col.separator()
        col.label(text="Render:")
        col.template_colormanaged_view_settings(scene, "view_settings")

        col = layout.column()
        col.separator()
        col.label(text="Sequencer color space:")
        col.prop(scene.sequencer_colorspace_settings, "name")


if __name__ == "__main__":  # only for live edit.
    bpy.utils.register_module(__name__)