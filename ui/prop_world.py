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

from bpy.types import Panel

# Inherit World data block
from bl_ui import properties_world
properties_world.WORLD_PT_context_world.COMPAT_ENGINES.add('THEBOUNTY')
properties_world.WORLD_PT_preview.COMPAT_ENGINES.add('THEBOUNTY')
del properties_world

class WorldButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"
    COMPAT_ENGINES = {'THEBOUNTY'}

    @classmethod
    def poll(cls, context):
        return (context.world and context.scene.render.engine in cls.COMPAT_ENGINES)
    
   
class TheBounty_PT_world(WorldButtonsPanel, Panel):
    bl_label = "Background Settings"
    ibl = True
    bl_context = "world"
    
    @classmethod
    def poll(cls, context):
        return context.world and WorldButtonsPanel.poll(context)


    def draw(self, context):
        layout = self.layout
        world = context.world.bounty

        split = layout.split()
        col = layout.column()
        col.prop(world, "bg_type", text="Background")
        #------------------------------------------
        # Gradient colors background
        #------------------------------------------
        if world.bg_type == "gradientback":

            split = layout.split(percentage=0.40)
            col = split.column()
            col.label(text="Zenith:")
            col.label(text="Horizon:")
            col.label(text="Horizon ground:")
            col.label(text="Zenith ground:")

            col = split.column()
            col.prop(world, "bg_zenith_color", text="")
            col.prop(world, "bg_horizon_color", text="")
            col.prop(world, "bg_horizon_ground_color", text="")
            col.prop(world, "bg_zenith_ground_color", text="")
        
        #------------------------------------------
        # Texture background
        #------------------------------------------
        elif world.bg_type == "textureback":

            tex = context.scene.world.active_texture

            if tex is not None:
                #
                layout.template_ID(context.world, "active_texture")
                # it allows to change the used image
                if  tex.yaf_tex_type == "IMAGE":
                    layout.template_image(tex, "image", tex.image_user, compact=True)
                #else:
                #    # TODO: create message about not allow texture type
                #    pass
            else:
                layout.template_ID(context.world, "active_texture", new="texture.new")
            
            layout.label(text="Background Texture options")
            row = layout.row()
            row.prop(world,"bg_rotation")
            row.prop(world,"bg_mapping_type", text="")
            layout.separator()
            
        #------------------------------------------
        # SunSky models for background
        #------------------------------------------
        elif world.bg_type in {"sunsky", "darksky"}:
            self.ibl = False
            layout.separator()
            sub = layout.column(align=True)
            if world.bg_type == "sunsky":
                sub.prop(world, "bg_turbidity")
            else:
                sub.prop(world, "bg_ds_turbidity")
            sub.prop(world, "bg_a_var")
            sub.prop(world, "bg_b_var")
            sub.prop(world, "bg_c_var")
            sub.prop(world, "bg_d_var")
            sub.prop(world, "bg_e_var")

            self.draw_updateSun(context)
            
            layout.separator()

            split = layout.split()
            col = split.column()
            col.prop(world, "bg_add_sun", toggle=True)
            sub = col.row()
            sub.enabled = world.bg_add_sun
            sub.prop(world, "bg_sun_power")
                        
            col = split.column()
            col.prop(world, "bg_background_light", toggle=True)
            sub = col.row()
            sub.enabled = world.bg_background_light
            sub.prop(world, "bg_power")
            #
            row = layout.row()
            row.enabled = (world.bg_add_sun or world.bg_background_light)
            row.prop(world, "bg_light_samples")
            #
            if world.bg_type == "darksky":
                layout.prop(world, "bg_dsnight", toggle= True)
                self.draw_influence(context)
                
                row = layout.row()
                row.prop(world, "bg_exposure")
                row.prop(world, "bg_dsbright")
            
                layout.prop(world, "bg_color_space", text="")
        #---------------------------------------
        # Color background
        #---------------------------------------    
        elif world.bg_type == "constant":

            split = layout.split(percentage=0.33)

            col = split.column()
            col.label("Color:")
            col = split.column()
            col.prop(world, "bg_single_color", text="")
        
        #------------------------------------------
        # IBL option draw cases..
        #------------------------------------------
        if world.bg_type in {"constant", "gradientback", "textureback"}:
            row = layout.row()
            row.prop(world, "bg_use_ibl", toggle=True)
            
        if world.bg_use_ibl and self.ibl:
            col = layout.row()
            col.prop(world, "bg_ibl_samples")
            col.prop(world, "bg_power", text="Power")
            if world.bg_type == "Texture":
                self.draw_influence(context)
        #
        if world.bg_type == 'textureback' and context.world.active_texture is not None:
            if world.bg_use_ibl:
                self.drawIBL(context)
                self.draw_influence(context)
                    
    #------------------------------------------------
    # Update Sun Light position 'from' or 'to' scene 
    #------------------------------------------------        
    def draw_updateSun(self, context):
        layout = self.layout
        world = context.world.bounty
        split = layout.split()
        col = split.column()
        col.label(text="Set sun position:")
        col.prop(world, "bg_from", text="")            

        col = split.column()
        col.label(text=" ")
        sub = col.column(align=True)
        sub.operator("world.get_position", text="Get from Location")
        sub.operator("world.get_angle", text="Get from Angle")
        sub.operator("world.update_sun", text="Update Lamp in 3D View")
        
    #------------------------------------------
    # Background light influence
    #------------------------------------------
    def draw_influence(self, context):
        layout = self.layout
        world = context.world.bounty
        row = layout.row()
        row.enabled = world.bg_background_light or (world.bg_type == "textureback" and world.bg_use_ibl)
        row.prop(world, "bg_with_diffuse", toggle=True)
        row.prop(world, "bg_with_caustic", toggle=True)
        
    #---------------------------
    # IBL definitions file (wip)
    #---------------------------
    def drawIBL(self, context):
        world = context.world.bounty
        layout = self.layout
        
        row = layout.row()
        row.prop(world,"ibl_file")
        if not world.ibl_file == "":
            # test
            layout.operator("world.parse_ibl")

        
from . import prop_volume_integrator as volum
volum.TheBounty_PT_vol_integrator.draw


if __name__ == "__main__":  # only for live edit.
    import bpy
    bpy.utils.register_module(__name__)
