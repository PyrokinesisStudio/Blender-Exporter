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
from ..ui.ior_values import ior_list
from bpy.types import Panel, Menu
from bl_ui.properties_material import (active_node_mat, check_material)

#
def find_node_input(node, name):
    for input in node.inputs:
        if input.name == name:
            return input
    return None

def panel_node_draw(layout, material, output_type, input_name):
    node = find_node(material, output_type)
    if node:
        if material.bounty.nodetree:
            ntree = bpy.data.node_groups[material.bounty.nodetree]
            input = find_node_input(node, input_name)
            layout.template_node_view(ntree, node, input)
            #draw_nodes_properties_ui(layout, material, ntree) #context, ntree)
    else:
        return False

    return True

def find_node(material, nodetype):
    if material and material.bounty and material.bounty.nodetree:    
        ntree = bpy.data.node_groups[material.bounty.nodetree]    
        for node in ntree.nodes:
            if getattr(node, "bl_idname", None) == nodetype:
                return node
    return None

def node_tree_selector_draw(layout, mat, nodetype):
    #
    try:
        layout.prop_search(mat.bounty, "nodetree", bpy.data, "node_groups")
        
    except:
        return False
    #
    node = find_node(mat, nodetype)
    if not node:
        if not mat.bounty.nodetree:
            layout.operator('bounty.add_nodetree', icon='NODETREE')
            return False
    return True

def blend_one_draw(layout, mat):
    #
    try:
        layout.prop_search(mat.bounty, "blendOne", bpy.data, "materials")
    except:
        return False    
    return True

def blend_two_draw(layout, mat):
    #
    try:
        layout.prop_search(mat.bounty, "blendTwo", bpy.data, "materials")
    except:
        return False
    return True

def draw_nodes_properties_ui(layout, context, nt, input_name='Surface', output_node_type="MaterialOutputNode"):
    output_node = next((n for n in nt.nodes
                        if hasattr(n, 'bl_idname') and 
                        n.bl_idname == output_node_type), None)
    if output_node is None:
        return

    socket = output_node.inputs[input_name]
    node = socket_node_input(nt, socket)

    layout.context_pointer_set("nodetree", nt)
    layout.context_pointer_set("node", output_node)
    layout.context_pointer_set("socket", socket)

    split = layout.split(0.35)
    split.label(socket.name + ':')

    if socket.is_linked:
        # for lights draw the shading rate ui.
        split.operator_menu_enum("node.add_%s" % input_name.lower(), "node_type", text=node.bl_idname) #label)
    else:
        split.operator_menu_enum("node.add_%s" % input_name.lower(), "node_type", text='None')

    #if node is not None:
    #    draw_node_properties_recursive(layout, context, nt, node)
    
def socket_node_input(nt, socket):
    return next((l.from_node for l in nt.links if l.to_socket == socket), None)

def draw_node_properties_recursive(layout, context, nt, node, level=0):

    def indented_label(layout):
        for i in range(level):
            layout.label('',icon='BLANK1')

    layout.context_pointer_set("nodetree", nt)
    layout.context_pointer_set("node", node)
    
    # draw socket property in panel
    def draw_props(node, layout):
        # node properties
        node.draw_props(context,layout,indented_label)

        # inputs
        for socket in node.inputs:
            layout.context_pointer_set("socket", socket)

            if socket.is_linked:
                input_node = nodes.socket_node_input(nt, socket)
                ui_open = socket.ui_open
                icon = 'DISCLOSURE_TRI_DOWN' if ui_open else 'DISCLOSURE_TRI_RIGHT'
                split = layout.split(common.label_percentage)
                row = split.row()
                indented_label(row)
                row.prop(socket, "ui_open", icon=icon, text='', icon_only=True, emboss=False)
                row.label(socket.name+":")
                split.operator_menu_enum("node.add_surface" , "node_type", text=input_node.bl_idname , icon= 'DOT')
                if socket.ui_open:
                    draw_node_properties_recursive(layout, context, nt, input_node, level=level+1)
            else:
                split = layout.split()
                row = split.row()
                indented_label(row)
                row.label(socket.name)
                prop_panel = split.row( align=True )
                if socket.default_value is not None:
                    prop_panel.prop(socket,'default_value',text="")
                prop_panel.operator_menu_enum("node.add_surface" , "node_type", text='',icon='DOT')

    draw_props(node, layout)
    layout.separator()
################################################################################################################
class TheBountyMaterialButtonsPanel():
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    COMPAT_ENGINES = {'THEBOUNTY'}
    
    @classmethod
    def poll(cls, context):
        mat = context.material
        return mat and (context.scene.render.engine in cls.COMPAT_ENGINES)


class TheBountyMaterialPresets(Menu):
    bl_label = "Material Presets"
    preset_subdir = "thebounty/material"
    preset_operator = "script.execute_preset"
    COMPAT_ENGINES = {'THEBOUNTY'}
    draw = Menu.draw_preset


class TheBountyMaterialTypePanel(TheBountyMaterialButtonsPanel):
    COMPAT_ENGINES = {'THEBOUNTY'}

    @classmethod
    def poll(cls, context):
        mat = context.material
        
        if context.scene.render.engine not in cls.COMPAT_ENGINES:
            return False
        #
        return (check_material(mat) 
                and (mat.bounty.mat_type in cls.material_type) 
                and (context.material.bounty.nodetree == ""))


class TheBountyContextMaterial(TheBountyMaterialButtonsPanel, Panel):
    bl_label = "Material"
    bl_options = {'HIDE_HEADER'}
    COMPAT_ENGINES = {'THEBOUNTY'}
    
    @classmethod
    def poll(cls, context):
        #
        engine = context.scene.render.engine
        return ((context.material or context.object) and (engine in cls.COMPAT_ENGINES))

    def draw(self, context):
        layout = self.layout

        mat = context.material
        ob = context.object
        slot = context.material_slot
        space = context.space_data

        if ob:
            row = layout.row()
            row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=2)

            col = row.column(align=True)
            col.operator("object.material_slot_add", icon='ZOOMIN', text="")
            col.operator("object.material_slot_remove", icon='ZOOMOUT', text="")

            # TODO: code own operators to copy yaf material settings...
            col.menu("MATERIAL_MT_specials", icon='DOWNARROW_HLT', text="")

            if ob.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")

        split = layout.split(percentage=0.75)

        if ob:
            split.template_ID(ob, "active_material", new="material.new")
            row = split.row()
            #---------------------------------------------------------
            # for disable nodes are used from other render engines
            #---------------------------------------------------------
            if mat and mat.use_nodes: 
                row.prop(mat, "use_nodes", icon='NODETREE', text="")
            #
            if slot:
                row.prop(slot, "link", text="")
            else:
                row.label()

        elif mat:
            split.template_ID(space, "pin_id")               
            split.separator()
                        
        if mat:
            row = layout.row(align=True)
            row.menu("TheBountyMaterialPresets", text=bpy.types.TheBountyMaterialPresets.bl_label)
            row.operator("bounty.material_preset_add", text="", icon='ZOOMIN')
            row.operator("bounty.material_preset_add", text="", icon='ZOOMOUT').remove_active = True
            
        #----------------------------------------------------
        # show nodetree button
        #----------------------------------------------------
        #if not 
        node_tree_selector_draw(layout, mat, 'MaterialOutputNode')#:
        if not panel_node_draw(layout, mat, 'MaterialOutputNode', 'Surface'): 
            #row = self.layout.row(align=True)
            if slot is not None and slot.name:
                layout.prop(mat.bounty, "mat_type")             

class TheBountyMaterialPreview(TheBountyMaterialButtonsPanel, Panel):
    bl_label = "Preview" 
    bl_options = {"DEFAULT_CLOSED"} 
    
    @classmethod
    def poll(cls, context):
        return context.material and TheBountyMaterialButtonsPanel.poll(context)

    def draw(self, context):
        self.layout.template_preview(context.material)


def draw_generator(ior_n):
    def draw(self, context):
        sl = self.layout
        for values in ior_n:
            ior_name, ior_index = values
            props = sl.operator('material.set_ior_preset', text=ior_name)
            # two values given to ior preset operator
            props.index = ior_index
            props.name = ior_name
    return draw

submenus = []

for ior_group, ior_n in ior_list:
    submenu_idname = 'YAF_MT_presets_ior_list_cat%d' % len(submenus)
    submenu = type(
        submenu_idname,
        (Menu,),
        {
            'bl_idname': submenu_idname,
            'bl_label': ior_group,
            'draw': draw_generator(ior_n)
        }
    )
    bpy.utils.register_class(submenu)
    submenus.append(submenu)


class TheBounty_presets_ior_list(Menu):
    bl_label = "Glass"

    def draw(self, context):
        sl = self.layout
        for sm in submenus:
            sl.menu(sm.bl_idname)

class TheBountyBlend(TheBountyMaterialTypePanel, Panel):
    bl_label = "Blend material settings"
    material_type = 'blend'

    def draw(self, context):
        layout = self.layout
        mat = active_node_mat(context.material)
        
        layout.separator()
        blend_one_draw(layout, mat)
        
        layout.separator()
        layout.prop(mat.bounty, "blend_value", slider=True)
        
        layout.separator()
        blend_two_draw(layout, mat)
        layout.operator('material.sync_blend')
                    
class TheBountyShinyDiffuse(TheBountyMaterialTypePanel, Panel):
    bl_label = "Shiny Diffuse Material"
    material_type = 'shinydiffusemat'
    
    def draw(self, context):
        layout = self.layout
        mat = active_node_mat(context.material)

        split = layout.split()
        col = split.column()
        col.prop(mat, "diffuse_color")
        col.prop(mat.bounty, "emittance")
        layout.row().prop(mat.bounty, "diffuse_reflect", slider=True)

        col = split.column()
        sub = col.column()
        sub.label(text="Reflectance model:")
        sub.prop(mat.bounty, "brdf_type", text="")
        brdf = sub.column()
        brdf.enabled = mat.bounty.brdf_type == "oren_nayar"
        brdf.prop(mat.bounty, "sigma")

        layout.separator()

        box = layout.box()
        split = box.split()
        col = split.column()
        col.prop(mat.bounty, "transparency", slider=True)
        col = split.column()
        col.prop(mat.bounty, "translucency", slider=True)
        box.row().prop(mat.bounty, "transmit_filter", slider=True)
        
        split = layout.split()
        col = split.column()
        col.label(text="Mirror color:")
        col.prop(mat.bounty, "mirror_color", text="")

        col = split.column()
        col.prop(mat.bounty, "fresnel_effect")
        sub = col.column()
        sub.enabled = mat.bounty.fresnel_effect
        sub.prop(mat.bounty, "IOR_reflection", slider=True)
        layout.row().prop(mat.bounty, "specular_reflect", slider=True)

class TheBountyGlossyDiffuse(TheBountyMaterialTypePanel, Panel):
    bl_label = "Diffuse reflection"
    material_type = 'glossy', 'coated_glossy'

    def draw(self, context):
        layout = self.layout
        mat = active_node_mat(context.material)

        split = layout.split()
        col = split.column()
        col.prop(mat, "diffuse_color")

        col = split.column()
        ref = col.column(align=True)
        ref.label(text="Reflectance model:")
        ref.prop(mat.bounty, "brdf_type", text="")
        sig = col.column()
        sig.enabled = mat.bounty.brdf_type == "oren_nayar"
        sig.prop(mat.bounty, "sigma")
        layout.row().prop(mat.bounty, "diffuse_reflect", slider=True)

class TheBountyGlossySpecular(TheBountyMaterialTypePanel, Panel):
    bl_label = "Specular reflection"
    material_type = 'glossy', 'coated_glossy'

    def draw(self, context):
        layout = self.layout
        mat = active_node_mat(context.material)

        split = layout.split()
        col = split.column()
        col.prop(mat.bounty, "glossy_color")
        exp = col.column()
        exp.enabled = mat.bounty.anisotropic == False
        exp.prop(mat.bounty, "exponent")

        col = split.column()
        sub = col.column(align=True)
        sub.prop(mat.bounty, "anisotropic")
        ani = sub.column()
        ani.enabled = mat.bounty.anisotropic == True
        ani.prop(mat.bounty, "exp_u")
        ani.prop(mat.bounty, "exp_v")
        layout.row().prop(mat.bounty, "glossy_reflect", slider=True)
        layout.row().prop(mat.bounty, "as_diffuse")

        layout.separator()

        if mat.bounty.mat_type == "coated_glossy":
            box = layout.box()
            box.label(text="Coated layer for glossy:")
            split = box.split()
            col = split.column()
            col.prop(mat.bounty, "coat_mir_col")
            col = split.column(align=True)
            col.label(text="Fresnel reflection:")
            col.prop(mat.bounty, "IOR_reflection")
            col.label()

class TheBountyRealGlass(TheBountyMaterialTypePanel, Panel):
    bl_label = "Real glass settings"
    material_type = 'glass', 'rough_glass'

    def draw(self, context):
        layout = self.layout
        mat = active_node_mat(context.material)

        layout.label(text="Refraction and Reflections:")
        split = layout.split()
        col = split.column()
        col.prop(mat.bounty, "IOR_refraction")

        col = split.column()
        col.menu("TheBounty_presets_ior_list", text=bpy.types.TheBounty_presets_ior_list.bl_label)

        split = layout.split()
        col = split.column(align=True)
        col.prop(mat.bounty, "absorption")
        layout.prop(mat.bounty, "absorption_dist")

        col = split.column(align=True)
        col.label(text="Dispersion power:")
        col.prop(mat.bounty, "dispersion_power", text="")

        if mat.bounty.mat_type == "rough_glass":
            row = layout.row()
            #box.label(text="Glass roughness:")
            row.prop(mat.bounty, "refr_roughness",text="Roughness exponent", slider=True)

class TheBountyFakeGlass(TheBountyMaterialTypePanel, Panel):
    bl_label = "Fake glass settings"
    material_type = 'glass', 'rough_glass'

    def draw(self, context):
        layout = self.layout
        mat = active_node_mat(context.material)

        split = layout.split()
        col = split.column()
        col.prop(mat.bounty, "filter_color")
        col = split.column()
        col.prop(mat.bounty, "glass_mir_col")
        layout.row().prop(mat.bounty, "glass_transmit", slider=True)
        layout.row().prop(mat.bounty, "fake_shadows")

class TheBountyTranslucent(TheBountyMaterialTypePanel, Panel):
    bl_label = "Translucent Scattering Material"
    material_type = 'translucent'
    
    def draw(self, context):
        #
        layout = self.layout
        mat = active_node_mat(context.material)
        
        self.drawTranslucent(context, layout, mat)
        self.drawSSS(context, layout, mat)
        self.drawScattering(context, layout, mat)

    def drawTranslucent(self, context, layout, mat):
        #        
        split = layout.split()
        col = split.column()
        col.prop(mat, "diffuse_color")
        col.prop(mat.bounty, "diffuse_reflect", text="Diff. Reflect",slider=True)
        col = split.column()     
        col.prop(mat.bounty, "glossy_color")
        col.prop(mat.bounty, "glossy_reflect", text="Gloss. Reflect",slider=True)
        row= layout.row()
        row.prop(mat.bounty, "sssSpecularColor")
        layout.prop(mat.bounty, "exponent", text="Specular Exponent")
        
    def drawSSS(self, context, layout, mat):
        #
        row = layout.row()
        row.label("SSS Presets")
        row.prop(mat.bounty, 'sss_presets', text="")
        
        if not mat.bounty.sss_presets == "custom":
            layout.operator("material.parse_sss")

    def drawScattering(self, context, layout, mat):
        #
        layout.separator()        
        row = layout.row()        
        split = layout.split()
        
        col = split.column()        
        col.prop(mat.bounty, "sssSigmaS", text="Scattering (Sigma S)")
        col.prop(mat.bounty, "sssSigmaS_factor")
        col.prop(mat.bounty, "phaseFuction")
                
        col = split.column()
        col.prop(mat.bounty, "sssSigmaA", text="Absorption (Sigma A)")
        col.prop(mat.bounty, "sss_transmit", text="Translucency")
        col.prop(mat.bounty, "sssIOR")
    
            
if __name__ == "__main__":  # only for live edit.
    #import bpy
    bpy.utils.register_module(__name__)
