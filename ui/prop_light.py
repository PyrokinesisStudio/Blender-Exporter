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

# povman:  try to use same method than material panels
class TheBountyLightTypePanel(TheBountyDataButtonsPanel):
    COMPAT_ENGINES = {'THEBOUNTY'}

    @classmethod
    def poll(cls, context):
        lamp = context.lamp
        
        if context.scene.render.engine not in cls.COMPAT_ENGINES:
            return False
        #
        #return (check_material(mat) and (mat.bounty.mat_type in cls.material_type) and (context.lamp.bounty.nodetree == ""))
        return (lamp and lamp.type in cls.lamp_type) # and (context.lamp.bounty.nodetree == "")

#----------------------------------------------------------
#
def panel_node_draw(layout, lamp, output_type): #, input_name):
    node = find_node(lamp, output_type)
    if node == None:
        return False
    else:
        if lamp.bounty.lightree:
            ntree = bpy.data.node_groups[lamp.bounty.lightree]
            #input = find_node_input(node, input_name)
            #layout.template_node_view(ntree, node, input)

    return True

def find_node(lamp, nodetypes):
    if not (lamp and lamp.bounty and lamp.bounty.lightree):
        return None
        
    light_tree =  lamp.bounty.lightree
    
    if light_tree == '':
        return None
    #
    ltree = bpy.data.node_groups[light_tree]
    
    for node in ltree.nodes:
        nt = getattr(node, "bl_idname", None)
        if nt in nodetypes:
            return node
    return None

def node_tree_selector_draw(layout, lamp, output_type):
    # 
    try:
        layout.prop_search(lamp.bounty, "lightree", bpy.data, "node_groups")
    except:
        return False

    #node = find_node(lamp, output_type)
    #if not node:
    if not find_node(lamp, output_type):
        if not lamp.bounty.lightree:
            layout.operator('bounty.add_lightnodetree', icon='NODETREE')
            return False
    return True
#-------------------------------------------------------------------------------------------

class THEBOUNTY_PT_preview(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_label = "Preview"
    COMPAT_ENGINES = {'THEBOUNTY'}

    @classmethod
    def poll(self, context):
        engine = context.scene.render.engine
        return context.lamp and (engine in self.COMPAT_ENGINES)

    def draw(self, context):
        self.layout.template_preview(context.lamp)

class THEBOUNTY_PT_lamp(TheBountyDataButtonsPanel, Panel):
    bl_label = "Lamp"
    bl_context= 'data'
    COMPAT_ENGINES = {'THEBOUNTY'}
    
    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return context.lamp and (engine in cls.COMPAT_ENGINES)
    
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
        #if lamp.show_dist_clip:
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
        #
        layout = self.layout
        lamp = context.lamp
        #----------------------------------------------------
        # show nodetree button
        #----------------------------------------------------
        #if not 
        panel_node_draw(layout, lamp, 'LightOutputNode')
        layout.prop(lamp, "type", expand=True)
        node_tree_selector_draw(layout, lamp, 'LightOutputNode')
            
        layout.prop(lamp, "color")
        layout.prop(lamp.bounty, "energy", text="Power")  
        self.draw_panels(context, layout, lamp)
                 
            
        
    def draw_panels(self, context, layout, lamp):    
        # commons values
        #layout.prop(lamp, "type", expand=True)
        
        if lamp.type == "AREA":
            # move here
            # commons values
            #layout.prop(lamp, "color")
            #layout.prop(lamp.bounty, "energy", text="Power")
            #
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
            layout.label("TheBounty 'directional' light type")
            layout.prop(lamp.bounty, "infinite")
            if not lamp.bounty.infinite:
                layout.prop(lamp.bounty, "shadows_size", text="Radius of directional cone")
        else:
            #elif lamp.type == "POINT":
            col = layout.column(align=True)
            col.prop(lamp.bounty, "use_sphere", toggle=True)
            if lamp.use_sphere:
                col.prop(lamp.bounty, "sphere_radius")
                col.prop(lamp.bounty, "samples")
                col.prop(lamp.bounty, "create_geometry", toggle=True)
'''

#
class THEBOUNTY_PT_Directional_lamp(TheBountyLightTypePanel, Panel):
    bl_label = "Hemi Lamp"
    lamp_type = 'HEMI'    
    
    def draw(self, context):
        #
        layout = self.layout
        lamp = context.lamp
        layout.label("TheBounty 'directional' light type")
        layout.prop(lamp, "color")
        layout.prop(lamp.bounty, "energy", text="Power")
        layout.prop(lamp.bounty, "infinite")
        if not lamp.bounty.infinite:
            layout.prop(lamp.bounty, "shadows_size", text="Radius of directional cone")
            
#
class THEBOUNTY_PT_Sun_lamp(TheBountyLightTypePanel, Panel):
    bl_label = "Sun Lamp"
    lamp_type = 'SUN'    
    
    def draw(self, context):
        #
        layout = self.layout
        lamp = context.lamp
        #
        layout.prop(lamp, "color")
        layout.prop(lamp.bounty, "energy", text="Power")        
        layout.prop(lamp.bounty, "samples")
        layout.prop(lamp.bounty, "angle")
#
class THEBOUNTY_PT_Point_lamp(TheBountyLightTypePanel, Panel):
    bl_label = "Point Lamp"
    lamp_type = 'POINT'    
    
    def draw(self, context):
        #
        layout = self.layout
        lamp = context.lamp
        #
        layout.prop(lamp, "color")
        layout.prop(lamp.bounty, "energy", text="Power")
        #
        col = layout.column(align=True)
        col.prop(lamp.bounty, "use_sphere", toggle=True)
        if lamp.use_sphere:
            col.prop(lamp.bounty, "sphere_radius")
            col.prop(lamp.bounty, "samples")
            col.prop(lamp.bounty, "create_geometry", toggle=True)
            
#
class THEBOUNTY_PT_Area_lamp(TheBountyLightTypePanel, Panel):
    bl_label = "Area Lamp"
    lamp_type = 'AREA'    
    
    def draw(self, context):
        #
        layout = self.layout
        lamp = context.lamp
        layout.prop(lamp, "color")
        layout.prop(lamp.bounty, "energy", text="Power")
        #
        layout.prop(lamp.bounty, "samples")
        layout.prop(lamp.bounty, "create_geometry", toggle=True)
        #
        dr = self.draw_area_shape(context)
    #
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
        
#
class THEBOUNTY_PT_Spot_lamp(TheBountyLightTypePanel, Panel):
    bl_label = "Spot Lamp"
    lamp_type = 'SPOT'
    
    
    def draw(self, context):
        #
        layout = self.layout
        lamp = context.lamp
        # commons values
        layout.prop(lamp, "color")
        layout.prop(lamp.bounty, "energy", text="Power")
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
    #
    def draw_spot_shape(self, context):
        layout = self.layout
        lamp = context.lamp #.bounty
        
        layout.label("Spot shape settings:")
        
        row = layout.row()
        row.prop(lamp, "spot_size", text="Size")
        row.prop(lamp, "spot_blend", text="Blend", slider=True)
        
        split = layout.split()
        col = split.column(align=True)
        col.prop(lamp.bounty, "show_dist_clip", toggle=True)
        if lamp.bounty.show_dist_clip:
            col.prop(lamp, "distance")
            col.prop(lamp, "shadow_buffer_clip_start", text="Clip Start")
            col.prop(lamp, "shadow_buffer_clip_end", text=" Clip End")

        col = split.column()
        col.prop(lamp, "show_cone", toggle=True)

# end type panel test -----------------------------------------------------------------

'''      


if __name__ == "__main__":  # only for live edit.
    import bpy
    bpy.utils.register_module(__name__)
