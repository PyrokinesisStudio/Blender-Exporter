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
from bpy.types import Panel

class TheBountyDataButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    COMPAT_ENGINES = {'THEBOUNTY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.lamp and (engine in cls.COMPAT_ENGINES)

# Inherit Lamp data block
from bl_ui import properties_data_lamp
properties_data_lamp.DATA_PT_context_lamp.COMPAT_ENGINES.add('THEBOUNTY')
del properties_data_lamp

class THEBOUNTY_PT_preview(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_label = "Preview"
    COMPAT_ENGINES = {'THEBOUNTY'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.lamp and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        self.layout.template_preview(context.lamp)


class THEBOUNTY_PT_lamp(TheBountyDataButtonsPanel, Panel):
    bl_label = "Lamp"
    COMPAT_ENGINES = {'THEBOUNTY'}
    '''
    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.lamp and (engine in cls.COMPAT_ENGINES)
    '''
    def draw_spot_shape(self, context):
        layout = self.layout
        lamp = context.lamp.bounty
        
        layout.label("Spot shape settings:")
        
        row = layout.row()
        row.prop(context.lamp, "spot_size", text="Size")
        row.prop(context.lamp, "spot_blend", text="Blend", slider=True)
        
        split = layout.split()
        col = split.column(align=True)
        col.prop(lamp, "show_dist_clip", toggle=True)
        if lamp.show_dist_clip:
            col.prop(context.lamp, "distance")
            col.prop(context.lamp, "shadow_buffer_clip_start", text="Clip Start")
            col.prop(context.lamp, "shadow_buffer_clip_end", text=" Clip End")

        col = split.column()
        col.prop(context.lamp, "show_cone", toggle=True)

    def draw_area_shape(self, context):
        layout = self.layout
        lamp = context.object.data #.lamp
        
        layout.label("Area shape settings:")
        col = layout.column()
        col.row().prop(lamp, "shape", expand=True)
        sub = col.row(align=True)

        if lamp.shape == 'SQUARE':
            sub.prop(lamp, "size")
        elif lamp.shape == 'RECTANGLE':
            sub.prop(lamp, "size", text="Size X")
            sub.prop(lamp, "size_y", text="Size Y")
        col = layout.row()
        col.prop(lamp, "distance")
        
    def draw(self, context):
        layout = self.layout
        # exporter own Lamp properties
        lamp = context.lamp
        
        # commons values
        layout.prop(lamp, "type", expand=True)
        layout.prop(lamp, "color")
        layout.prop(lamp, "energy", text="Power")

        if lamp.type == "AREA":
            layout.prop(lamp.bounty, "samples")
            layout.prop(lamp.bounty, "create_geometry", toggle=True)
            #
            self.draw_area_shape(context)

        elif lamp.type == "SPOT":
            layout.prop(lamp.bounty, "ies_file")
            if lamp.bounty.ies_file =="":
                layout.prop(lamp.bounty, "photon_only", toggle=True)
            col = layout.column(align=True)
            if not lamp.bounty.photon_only:
                col.prop(lamp.bounty, "spot_soft_shadows", toggle=True)
                if lamp.bounty.spot_soft_shadows:
                    col.prop(lamp.bounty, "samples")
                    if lamp.bounty.ies_file =="":
                        col.prop(lamp.bounty, "shadow_fuzzyness")
             
            if lamp.bounty.ies_file =="":
                self.draw_spot_shape(context)            

        elif lamp.type == "SUN":
            layout.prop(lamp.bounty, "samples")
            layout.prop(lamp.bounty, "angle")

        elif lamp.type == "HEMI": #"DIRECTIONAL":
            layout.prop(lamp.bounty, "hemi_type")
            sub = layout.row()
            sub.enabled = not lamp.bounty.hemi_type == 'infinite'   
            sub.prop(lamp.bounty, "shadows_size", text="Radius of directional cone")

        elif lamp.type == "POINT":
            col = layout.column(align=True)
            col.prop(lamp.bounty, "use_sphere", toggle=True)
            if lamp.use_sphere:
                col.prop(lamp.bounty, "sphere_radius")
                col.prop(lamp.bounty, "samples")
                col.prop(lamp.bounty, "create_geometry", toggle=True)
        
        elif lamp.type == "IES":
            layout.prop(lamp, "ies_file")
            col = layout.column(align=True)            
            col.prop(lamp, "ies_soft_shadows", toggle=True)
            if lamp.ies_soft_shadows:
                col.prop(lamp, "samples")
            #
            self.draw_spot_shape(context)
        


if __name__ == "__main__":  # only for live edit.
    import bpy
    bpy.utils.register_module(__name__)
