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

import bpy
from yafaray.ot import yafaray_presets
from bl_ui.properties_render import RenderButtonsPanel
from bpy.types import Panel, Menu

RenderButtonsPanel.COMPAT_ENGINES = {'YAFA_RENDER'}

   
class YAFARAY_MT_render_presets(Menu):
    bl_label = "Render Presets"
    preset_subdir = "yafaray/render"
    preset_operator = "script.execute_preset"
    COMPAT_ENGINES = {'YAFA_RENDER'}
    draw = Menu.draw_preset

# povman: test for next panel distribution
class YAF_PT_pass_settings(RenderButtonsPanel, Panel):
    bl_label = "Render Passes"

    def draw(self, context):
        layout = self.layout
        scene = context.scene.bounty
        #render = scene.render
        #
        split = layout.split()
        col = split.column()
        col.prop(scene, "gs_transp_shad", toggle=True)
        col.prop(scene, "gs_clay_render", toggle=True)
        col.prop(scene, "gs_z_channel", toggle=True)
        col = split.column()
        sub = col.column()
        sub.enabled = scene.gs_transp_shad
        sub.prop(scene, "gs_shadow_depth")
        sub = col.column()
        sub.enabled = scene.gs_clay_render
        sub.prop(scene, "gs_clay_col", text="")

class YAF_PT_general_settings(RenderButtonsPanel, Panel):
    bl_label = "General Settings"

    def draw(self, context):
        layout = self.layout
        render = context.scene.render
        scene = context.scene.bounty
        

        row = layout.row(align=True)
        row.menu("YAFARAY_MT_render_presets", text=bpy.types.YAFARAY_MT_render_presets.bl_label)
        row.operator("yafaray.render_preset_add", text="", icon='ZOOMIN')
        row.operator("yafaray.render_preset_add", text="", icon='ZOOMOUT').remove_active = True

        layout.separator()
        
        split = layout.split(percentage=0.58)
        col = split.column()
        col.prop(scene, "gs_ray_depth")
        #col.prop(scene, "gs_gamma", text="Gamma out")
        col.prop(scene, "gs_type_render")
        sub = col.column()
        sub.enabled = scene.gs_type_render == "into_blender"
        sub.prop(scene, "gs_tile_order")

        col = split.column()
        sub = col.column()
        sub.enabled = scene.gs_transp_shad
        #sub.prop(scene, "gs_shadow_depth")
        col.prop(scene, "gs_gamma_input")
        sub = col.column()
        #sub.enabled = scene.gs_auto_threads == False
        col.prop(scene, "gs_threads")
        sub = col.column()
        sub.enabled = scene.gs_type_render == "into_blender"
        sub.prop(scene, "gs_tile_size")

        layout.separator()

        split = layout.split()
        col = split.column()
        col.prop(scene, "gs_clamp_rgb", toggle=True)
        col.prop(scene, "gs_verbose", toggle=True)

        col = split.column()
        col.prop(render, "use_instances", text="Use instances", toggle=True)
        col.prop(scene, "gs_show_sam_pix", toggle=True)
        #col.prop(scene, "gs_verbose", toggle=True)

        split = layout.split(percentage=0.5)
        col = split.column()
        col.prop(scene, "bg_transp", toggle=True)
        col = split.column()
        sub = col.column()
        sub.enabled = scene.bg_transp
        sub.prop(scene, "bg_transp_refract", toggle=True)
        
        split = layout.split(percentage=0.58)
        col = layout.column()
        col.label('Stamp:')
        col.prop(scene, "gs_draw_params", text="Draw params and custom string")
        
        col = layout.column()
        col.enabled = scene.gs_draw_params
        col.prop(scene, "gs_custom_string", text="")        


if __name__ == "__main__":  # only for live edit.
    #import bpy
    bpy.utils.register_module(__name__)
