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
import yafrayinterface
#from bpy_types import NodeTree


def proj2int(val):
    if val == 'NONE':
        return 0
    elif val == 'X':
        return 1
    elif val == 'Y':
        return 2
    elif val == 'Z':
        return 3
    
switchTextureCoordinates = {
    'UV': 'uv',
    'GLOBAL': 'global',
    'ORCO': 'orco',
    'WINDOW': 'window',
    'NORMAL': 'normal',
    'REFLECTION': 'reflect',
    'STICKY': 'stick',
    'STRESS': 'stress',
    'TANGENT': 'tangent',
    'OBJECT': 'transformed',
}

switchBlendMode = {
    'MIX': 0,
    'ADD': 1,
    'MULTIPLY': 2,
    'SUBTRACT': 3,
    'SCREEN': 4,
    'DIVIDE': 5,
    'DIFFERENCE': 6,
    'DARKEN': 7,
    'LIGHTEN': 8,
}

switchMappingCoords = {
    'FLAT': 'plain',
    'CUBE': 'cube',
    'TUBE': 'tube',
    'SPHERE': 'sphere',
}

shinyLayers = ['Diffuse', 'Transparency', 'Translucency', 'Mirror', 'Specular', 'Bumpmap']
glossyLayers =['Diffuse', 'Glossy', 'Specular', 'Bumpmap']
glassLayers =['Mirror', 'Bumpmap']

validMaterialTypes=['shinydiffusemat', 'glossy', 'coated_glossy', 'glass', 'rough_glass', 'translucent', 'blend']

class TheBountyMaterialWrite:
    def __init__(self, interface, mMap, texMap):
        self.yi = interface
        self.materialMap = mMap
        self.textureMap = texMap
        # test
        useMaterialNodes = False
        linked_node = None
        self.nodetreeListNames = []
        self.nodeValues = {}

    def namehash(self, obj):
        nh = obj.name + "-" + str(obj.__hash__())
        return nh

    def getUsedTextures(self, material):
        used_textures = []
        for tex_slot in material.texture_slots:
            if tex_slot and tex_slot.use and tex_slot.texture:
                used_textures.append(tex_slot)

        return used_textures
    #
    textureLayerParams = {
        "element": "shader_node", "type":"layer", "name":'', "input":'mapname', "mode":'MIX',
        "stencil":False, "negative" :False, "noRGB": False, "def_col":(1,1,1), "def_val":1.0, 
        "color_input": False, "use_alpha": False, "upper_color":(1,1,1), "upper_value":0.0, 
        "upper_layer":'', "colfac": 1.0, "valfac":1.0, "do_color":False, "do_scalar": True}
    
    def writeTexLayer(self, name, mapName, ulayer, mtex, dcol, factor):
        #
        if mtex.name not in self.textureMap:
            return False

        yi = self.yi
        yi.paramsPushList()
        yi.paramsSetString("element", "shader_node")
        yi.paramsSetString("type", "layer")
        yi.paramsSetString("name", name)

        yi.paramsSetString("input", mapName)

        # set texture blend mode, if not a supported mode then set it to 'MIX'
        mode = switchBlendMode.get(mtex.blend_type, 0)
        yi.paramsSetInt("mode", mode)
        yi.paramsSetBool("stencil", mtex.use_stencil)

        negative = mtex.invert        
        if factor < 0:  # force 'negative' to True
            factor = factor * -1
            negative = True        
        yi.paramsSetBool("negative", negative)

        # Use float instead rgb data from image or procedural texture
        yi.paramsSetBool("noRGB", mtex.use_rgb_to_intensity)

        yi.paramsSetColor("def_col", mtex.color[0], mtex.color[1], mtex.color[2])
        yi.paramsSetFloat("def_val", mtex.default_value)

        tex = mtex.texture  # texture object instance
        isImage = tex.bounty.tex_type == 'IMAGE'

        isColored = False
        if (isImage or (tex.bounty.tex_type == 'VORONOI' and tex.color_mode not in 'INTENSITY')):
            isColored = True
        yi.paramsSetBool("color_input", isColored)
        
        useAlpha = False        
        if isImage:
            useAlpha = (tex.bounty.use_alpha) and not(tex.use_calculate_alpha)

        yi.paramsSetBool("use_alpha", useAlpha)

        do_color = len(dcol) >= 3  # see defination of dcol later on, watch the remaining parts from now on.

        if ulayer == "":
            if do_color:
                yi.paramsSetColor("upper_color", dcol[0], dcol[1], dcol[2])
                yi.paramsSetFloat("upper_value", 0)
            else:
                yi.paramsSetColor("upper_color", 0, 0, 0)
                yi.paramsSetFloat("upper_value", dcol[0])
        else:
            yi.paramsSetString("upper_layer", ulayer)

        if do_color:
            yi.paramsSetFloat("colfac", factor)
        else:
            yi.paramsSetFloat("valfac", factor)

        yi.paramsSetBool("do_color", do_color)
        yi.paramsSetBool("do_scalar", not do_color)

        return True
    # 
    
    textureMappingParams = {
        "element":"shader_node", "type":"texture_mapper", "name":"", 
        "texture":"", "texco":"", "proj_x":0, "proj_y":1, "proj_z":2, 
        "mapping":"plain", "offset":0.0, "scale":1, "bump_strength":0.0         
    }
    def writeMappingNode(self, mapname, mtex):
        yi = self.yi
        yi.paramsPushList()

        yi.paramsSetString("element", "shader_node")
        yi.paramsSetString("type", "texture_mapper")
        yi.paramsSetString("name", mapname)
        yi.paramsSetString("texture", mtex.texture.name) #texname)
        
        # get texture coords, default is 'orco'
        texco = switchTextureCoordinates.get(mtex.texture_coords, 'orco')
        yi.paramsSetString("texco", texco)

        if mtex.object:
            texmat = mtex.object.matrix_world.inverted()
            rtmatrix = yafrayinterface.new_floatArray(4 * 4)

            for x in range(4):
                for y in range(4):
                    idx = (y + x * 4)
                    yafrayinterface.floatArray_setitem(rtmatrix, idx, texmat[x][y])
            yi.paramsSetMemMatrix("transform", rtmatrix, False)
            yafrayinterface.delete_floatArray(rtmatrix)

        yi.paramsSetInt("proj_x", proj2int(mtex.mapping_x))
        yi.paramsSetInt("proj_y", proj2int(mtex.mapping_y))
        yi.paramsSetInt("proj_z", proj2int(mtex.mapping_z))

        mappingCoords = switchMappingCoords.get(mtex.mapping, 'plain')
        yi.paramsSetString("mapping", mappingCoords)

        yi.paramsSetPoint("offset", mtex.offset[0], mtex.offset[1], mtex.offset[2])
        if self.preview:  # check if it is a texture preview render
            mtex_X = mtex.scale[0] * 8.998  # tex preview fix: scale X value of tex size for the stretched Plane Mesh in preview scene
            mtex_Z = mtex.scale[2] * 0.00001  # and for Z value of texture size also...
            yi.paramsSetPoint("scale", mtex_X, mtex.scale[1], mtex_Z)
        else:
            yi.paramsSetPoint("scale", mtex.scale[0], mtex.scale[1], mtex.scale[2])

        if mtex.use_map_normal:  # || mtex->maptoneg & MAP_NORM )
            # scale up the normal factor, it resembles
            # blender a bit more
            nf = mtex.normal_factor * 2
            yi.paramsSetFloat("bump_strength", nf)
            
    
    def glassParams(self, mat, linked_node):
        #
        materialParams = {}
        nodemat = self.useMaterialNodes and linked_node is not None
        
        materialParams = {                
            "IOR"               : mat.bounty.IOR_refraction,
            "filter_color"      : mat.bounty.filter_color,
            "mirror_color"      : linked_node.inputs['Mirror'].glass_mir_col if nodemat else mat.bounty.glass_mir_col,
            "transmit_filter"   : mat.bounty.glass_transmit,
            "absorption"        : mat.bounty.absorption,
            "absorption_dist"   : mat.bounty.absorption_dist,
            "dispersion_power"  : mat.bounty.dispersion_power,
            "fake_shadows"      : mat.bounty.fake_shadows,
            "alpha"             : mat.bounty.refr_roughness,
        }
        return materialParams
    
    def writeGlassShader(self, mat, linked_node):

        yi = self.yi
        yi.paramsClearAll()
        #
        params = self.glassParams( mat, linked_node)
        
        # add refraction roughness for roughglass material
        if mat.bounty.mat_type == "rough_glass":
            yi.paramsSetFloat("alpha", mat.bounty.refr_roughness)
        yi.paramsSetString("type", mat.bounty.mat_type)

        yi.paramsSetFloat("IOR", mat.bounty.IOR_refraction)  # added IOR for refraction
        filt_col = mat.bounty.filter_color
        mir_col = params.get('mirror_color', mat.bounty.glass_mir_col)
        abs_col = mat.bounty.absorption

        yi.paramsSetColor("filter_color", filt_col[0], filt_col[1], filt_col[2])
        yi.paramsSetColor("mirror_color", mir_col[0], mir_col[1], mir_col[2])
        yi.paramsSetFloat("transmit_filter", mat.bounty.glass_transmit)

        yi.paramsSetColor("absorption", abs_col[0], abs_col[1], abs_col[2])
        yi.paramsSetFloat("absorption_dist", mat.bounty.absorption_dist)
        yi.paramsSetFloat("dispersion_power", mat.bounty.dispersion_power)
        yi.paramsSetBool("fake_shadows", mat.bounty.fake_shadows)

        mcolRoot = ''
        # fcolRoot = '' /* UNUSED */
        bumpRoot = ''

        i = 0
        used_textures = self.getUsedTextures(mat)

        for mtex in used_textures:
            used = False
            mappername = "map%x" % i
            #
            if mtex.use_map_mirror:
                lname = "mircol_layer%x" % i
                if self.writeTexLayer(lname, mappername, mcolRoot, mtex, mir_col, mtex.mirror_factor):
                    used = True
                    mcolRoot = lname
            #
            if mtex.use_map_normal:
                lname = "bump_layer%x" % i
                if self.writeTexLayer(lname, mappername, bumpRoot, mtex, [0], mtex.normal_factor):
                    used = True
                    bumpRoot = lname
                
            if used:
                self.writeMappingNode(mappername, mtex)
                i += 1

        yi.paramsEndList()
        if mcolRoot.startswith('mircol_'):  yi.paramsSetString("mirror_color_shader", mcolRoot)            
        if bumpRoot.startswith('bump_'):    yi.paramsSetString("bump_shader", bumpRoot)

        return yi.createMaterial(self.namehash(mat))
    
    def glossyParams(self, mat, linked_node):
        #
        materialParams = {}
        nodemat = self.useMaterialNodes and linked_node is not None
        #
        materialParams = {

            "diffuse_color"     : linked_node.inputs['Diffuse'].diff_color      if nodemat else mat.diffuse_color,
            "color"             : linked_node.inputs['Glossy'].glossy_color     if nodemat else mat.bounty.glossy_color,
            "glossy_reflect"    : linked_node.inputs['Specular'].glossy_reflect if nodemat else mat.bounty.glossy_reflect,
            "diffuse_reflect"   : linked_node.inputs['Diffuse'].diffuse_reflect if nodemat else mat.bounty.diffuse_reflect,
            #"diffuse_brdf"      : linked_node.inputs['BRDF'].brdf_type          if nodemat else mat.bounty.brdf_type,
            #"sigma"             : linked_node.inputs['BRDF'].sigma              if nodemat else mat.bounty.sigma,                
        }
        return materialParams
            
    def writeGlossyShader(self, mat, linked_node):
        yi = self.yi
        yi.paramsClearAll()
        #
        params = self.glossyParams(mat, linked_node)
        #-------------------------------------------
        # Add IOR and mirror color for coated glossy
        #-------------------------------------------
        if mat.bounty.mat_type == "coated_glossy":
            yi.paramsSetFloat("IOR", mat.bounty.IOR_reflection)
            mir_col = mat.bounty.coat_mir_col
            yi.paramsSetColor("mirror_color", mir_col[0], mir_col[1], mir_col[2])
        
        diffuse_color = params.get('diffuse_color', mat.diffuse_color)
        glossy_color = params.get('color', mat.bounty.glossy_color)
        glossy_reflect = params.get("glossy_reflect", mat.bounty.glossy_reflect)

        yi.paramsSetColor("diffuse_color", diffuse_color[0], diffuse_color[1], diffuse_color[2])
        yi.paramsSetColor("color", glossy_color[0], glossy_color[1], glossy_color[2])
        yi.paramsSetFloat("glossy_reflect", glossy_reflect)
        yi.paramsSetFloat("exponent", mat.bounty.exponent)
        yi.paramsSetFloat("diffuse_reflect", params.get('diffuse_reflect', mat.bounty.diffuse_reflect))
        yi.paramsSetBool("as_diffuse", mat.bounty.as_diffuse)
        yi.paramsSetBool("anisotropic", mat.bounty.anisotropic)
        yi.paramsSetFloat("exp_u", mat.bounty.exp_u)
        yi.paramsSetFloat("exp_v", mat.bounty.exp_v)
        #
        brdf = 'lambert'
        if mat.bounty.brdf_type == "oren-nayar":  # oren-nayar fix for glossy
            brdf = 'Oren-Nayar'
            yi.paramsSetString("diffuse_brdf", brdf)
            yi.paramsSetFloat("sigma", params.get('sigma', mat.bounty.sigma))
        #
        yi.paramsSetString("type", mat.bounty.mat_type)

        # init shader values..
        diffRoot = ''
        glossRoot = ''
        glRefRoot = ''
        bumpRoot = ''
        # mcolRoot = '' is UNUSED ??  TODO: review for coated case */

        i = 0
        used_textures = self.getUsedTextures(mat)

        for mtex in used_textures:
            used = False
            mappername = "map%x" % i

            if mtex.use_map_color_diffuse:
                lname = "diff_layer%x" % i
                if self.writeTexLayer(lname, mappername, diffRoot, mtex, diffuse_color, mtex.diffuse_color_factor):
                    used = True
                    diffRoot = lname
            #
            if mtex.use_map_color_spec:
                lname = "gloss_layer%x" % i
                if self.writeTexLayer(lname, mappername, glossRoot, mtex, glossy_color, mtex.specular_color_factor):
                    used = True
                    glossRoot = lname
            #
            if mtex.use_map_specular:
                lname = "glossref_layer%x" % i
                if self.writeTexLayer(lname, mappername, glRefRoot, mtex, [glossy_reflect], mtex.specular_factor):
                    used = True
                    glRefRoot = lname
            #
            if mtex.use_map_normal:
                lname = "bump_layer%x" % i
                if self.writeTexLayer(lname, mappername, bumpRoot, mtex, [0], mtex.normal_factor):
                    used = True
                    bumpRoot = lname
            #
            if used:
                self.writeMappingNode(mappername, mtex)
            i += 1

        yi.paramsEndList()
        
        if diffRoot.startswith('diff_'):        yi.paramsSetString("diffuse_shader", diffRoot)
        if glossRoot.startswith('gloss_'):      yi.paramsSetString("glossy_shader", glossRoot)
        if glRefRoot.startswith('glossref_'):   yi.paramsSetString("glossy_reflect_shader", glRefRoot)            
        if bumpRoot.startswith('bump_'):        yi.paramsSetString("bump_shader", bumpRoot)

        return yi.createMaterial(self.namehash(mat))
    
    def sssParams(self, mat, linked_node):
        #
        materialParams = {}
        nodemat = self.useMaterialNodes and linked_node is not None
        
        materialParams = {
            "IOR"               : mat.bounty.sssIOR,
            "color"             : mat.diffuse_color, 
            "glossy_color"      : mat.bounty.glossy_color,
            "specular_color"    : mat.bounty.sssSpecularColor,
            "sigmaA"            : mat.bounty.sssSigmaA,
            "sigmaS"            : mat.bounty.sssSigmaS,
            "sigmaS_factor"     : mat.bounty.sssSigmaS_factor,
            "diffuse_reflect"   : mat.bounty.diffuse_reflect,
            "glossy_reflect"    : mat.bounty.glossy_reflect,
            "sss_transmit"      : mat.bounty.sss_transmit,
            "exponent"          : mat.bounty.exponent,
            "g"                 : mat.bounty.phaseFuction
        }
        return materialParams
    
    def writeTranslucentShader(self, mat, linked_node):
        yi = self.yi
        yi.paramsClearAll()
        #
        params = self.sssParams(mat, linked_node)
        
        diffColor   = params.get('color', mat.diffuse_color)
        glossyColor = params.get('glossy_color', mat.bounty.glossy_color)
        specColor   = params.get('specular_color', mat.bounty.sssSpecularColor)
        sigmaA      = params.get('sigmaA', mat.bounty.sssSigmaA)
        sigmaS      = params.get('sigmaS', mat.bounty.sssSigmaS)
        
        yi.paramsSetString("type", "translucent")
        yi.paramsSetFloat("IOR", params.get('IOR', mat.bounty.sssIOR))
        yi.paramsSetColor("color", diffColor[0], diffColor[1], diffColor[2])
        yi.paramsSetColor("glossy_color", glossyColor[0], glossyColor[1], glossyColor[2])
        yi.paramsSetColor("specular_color", specColor[0], specColor[1], specColor[2])
        yi.paramsSetColor("sigmaA", sigmaA[0], sigmaA[1], sigmaA[2])
        yi.paramsSetColor("sigmaS", sigmaS[0], sigmaS[1], sigmaS[2])
        
        yi.paramsSetFloat("sigmaS_factor", mat.bounty.sssSigmaS_factor)
        yi.paramsSetFloat("diffuse_reflect", mat.bounty.diffuse_reflect)
        yi.paramsSetFloat("glossy_reflect", mat.bounty.glossy_reflect)
        yi.paramsSetFloat("sss_transmit", mat.bounty.sss_transmit)
        yi.paramsSetFloat("exponent", mat.bounty.exponent)
        yi.paramsSetFloat("g", mat.bounty.phaseFuction) # fix phase function, report by wizofboz
        
        # init shader values..
        diffRoot = ''
        glossRoot = ''
        glRefRoot = ''
        transpRoot = ''
        translRoot = ''
        bumpRoot = ''
        
        i=0
        used_mtextures = self.getUsedTextures(mat)

        for mtex in used_mtextures:
            used = False
            mappername = "map%x" %i
            #
            if mtex.use_map_color_diffuse:
                lname = "diff_layer%x" % i
                if self.writeTexLayer(lname, mappername, diffRoot, mtex, diffColor, mtex.diffuse_color_factor):
                    used = True
                    diffRoot = lname
            #        
            if mtex.use_map_color_spec:
                lname = "gloss_layer%x" % i
                if self.writeTexLayer(lname, mappername, glossRoot, mtex, glossyColor, mtex.specular_color_factor):
                    used = True
                    glossRoot = lname
            #        
            if mtex.use_map_specular:
                lname = "glossref_layer%x" % i
                if self.writeTexLayer(lname, mappername, glRefRoot, mtex, [mat.bounty.glossy_reflect], mtex.specular_factor):
                    used = True
                    glRefRoot = lname
            #        
            if mtex.use_map_alpha:
                lname = "transp_layer%x" % i
                if self.writeTexLayer(lname, mappername, transpRoot, mtex, sigmaA, mtex.alpha_factor):
                    used = True
                    transpRoot = lname
            #
            if mtex.use_map_translucency:
                lname = "translu_layer%x" % i
                if self.writeTexLayer(lname, mappername, translRoot, mtex, sigmaS, mtex.translucency_factor):
                    used = True
                    translRoot = lname
            #
            if mtex.use_map_normal:
                lname = "bump_layer%x" % i
                if self.writeTexLayer(lname, mappername, bumpRoot, mtex, [0], mtex.normal_factor):
                    used = True
                    bumpRoot = lname
            #
            if used:
                self.writeMappingNode(mappername, mtex) #.texture.name, mtex)
            i +=1
        
        yi.paramsEndList()
        if diffRoot.startswith('diff_'):        yi.paramsSetString("diffuse_shader", diffRoot)
        if glossRoot.startswith('gloss_'):      yi.paramsSetString("glossy_shader", glossRoot)
        if glRefRoot.startswith('glossref'):    yi.paramsSetString("glossy_reflect_shader", glRefRoot)
        if bumpRoot.startswith('bump_'):        yi.paramsSetString("bump_shader", bumpRoot)
        if transpRoot.startswith('transp_'):    yi.paramsSetString("sigmaA_shader", transpRoot)
        if translRoot.startswith('translu_'):   yi.paramsSetString("sigmaS_shader", translRoot)

        return yi.createMaterial(self.namehash(mat))
    
    #-----------------------------------------------------
    # Shiny diffuse material
    #-----------------------------------------------------
    def shinyParams(self, mat, linked_node):
        #
        materialParams = {}
        nodemat = self.useMaterialNodes and linked_node is not None
        #
        materialParams = {
            "type"              : mat.bounty.mat_type,
            "color"             : linked_node.inputs['Diffuse'].diff_color          if nodemat else mat.diffuse_color,
            "diffuse_reflect"   : linked_node.inputs['Diffuse'].diffuse_reflect     if nodemat else mat.bounty.diffuse_reflect,
            "emit"              : linked_node.emittance                             if nodemat else mat.bounty.emittance,
            "diffuse_brdf"      : linked_node.brdf_type                             if nodemat else mat.bounty.brdf_type,
            "sigma"             : linked_node.sigma                                 if nodemat else mat.bounty.sigma,
            "transparency"      : linked_node.inputs['Transparency'].transparency   if nodemat else mat.bounty.transparency,
            "translucency"      : linked_node.inputs['Translucency'].translucency   if nodemat else mat.bounty.translucency,
            "transmit_filter"   : linked_node.transmit                              if nodemat else mat.bounty.transmit_filter,
            "specular_reflect"  : linked_node.inputs['Specular'].specular_reflect   if nodemat else mat.bounty.specular_reflect,
            "mirror_color"      : linked_node.inputs['Mirror'].mirror_color         if nodemat else mat.bounty.mirror_color,
            "fresnel_effect"    : linked_node.fresnel_effect                        if nodemat else mat.bounty.fresnel_effect,
            "IOR"               : linked_node.IOR_reflection                        if nodemat else mat.bounty.IOR_reflection,                            
        }
        return materialParams
       
    def writeShinyDiffuseShader(self, mat, linked_node):
        
        yi = self.yi
        yi.paramsClearAll()
        '''
        chequear los nodos admitidos por cada slot
        '''
        if linked_node is not None:
            diffuse = linked_node.inputs['Diffuse']
            print('\nDiffuse color: ', diffuse.getParams()['color'])
            if diffuse.is_linked:
                print('\nDiffuse layer: ', diffuse.getParams()['DiffuseLayer'].keys())
                
            transparency = linked_node.inputs['Transparency']#['stencil']
            #if linked_node.inputs['Transparency'].is_linked:
            print('\nTransparency parameters: ', transparency.getParams()['transparency'])
                
        params = self.shinyParams(mat, linked_node)
        
        diffColor = params.get('color', mat.diffuse_color)
        mirCol = params.get('mirror_color', mat.bounty.mirror_color)
        
        specular_reflect = params.get('specular_reflect', mat.bounty.specular_reflect)
        transparency = params.get('transparency', mat.bounty.transparency)
        translucency = params.get('translucency', mat.bounty.translucency)
        brdf = params.get('diffuse_brdf', mat.bounty.brdf_type)

        yi.paramsSetString("type", 'shinydiffusemat')
        
        ##
        yi.paramsSetColor("color", diffColor[0], diffColor[1], diffColor[2])
        yi.paramsSetFloat("transparency", transparency)
        yi.paramsSetFloat("translucency", translucency)
        yi.paramsSetFloat("diffuse_reflect", params.get('diffuse_reflect', mat.bounty.diffuse_reflect))
        yi.paramsSetFloat("emit", params.get('emit', mat.bounty.emittance))
        yi.paramsSetFloat("transmit_filter", params.get('transmit_filter', mat.bounty.transmit_filter))

        yi.paramsSetFloat("specular_reflect", specular_reflect)
        yi.paramsSetColor("mirror_color", mirCol[0], mirCol[1], mirCol[2])
        yi.paramsSetBool("fresnel_effect", params.get('fresnel_effect', False))
        yi.paramsSetFloat("IOR", params.get('IOR', mat.bounty.IOR_reflection))
        
        yi.paramsSetString("diffuse_brdf", brdf)
        if brdf == "oren_nayar":
            yi.paramsSetFloat("sigma", params.get('sigma', mat.bounty.sigma))
        #
        
        i = 0
        used_textures = self.getUsedTextures(mat)

        # init values..
        diffRoot = mcolRoot = transpRoot = translRoot = mirrorRoot = bumpRoot = ''

        for mtex in used_textures:
            if not mtex.texture:
                continue
            # done..
            used = False
            mappername = "map%x" % i

            #
            if mtex.use_map_color_diffuse:
                lname = "diff_layer%x" % i
                if self.writeTexLayer(lname, mappername, diffRoot, mtex, diffColor, mtex.diffuse_color_factor):
                    used = True
                    diffRoot = lname
            #
            if mtex.use_map_mirror:
                lname = "mircol_layer%x" % i
                if self.writeTexLayer(lname, mappername, mcolRoot, mtex, mirCol, mtex.mirror_factor):
                    used = True
                    mcolRoot = lname
            #
            if mtex.use_map_alpha:
                lname = "transp_layer%x" % i
                if self.writeTexLayer(lname, mappername, transpRoot, mtex, [transparency], mtex.alpha_factor):
                    used = True
                    transpRoot = lname
            #
            if mtex.use_map_translucency:
                lname = "translu_layer%x" % i
                if self.writeTexLayer(lname, mappername, translRoot, mtex, [translucency], mtex.translucency_factor):
                    used = True
                    translRoot = lname
            #
            if mtex.use_map_raymir:
                lname = "mirr_layer%x" % i
                if self.writeTexLayer(lname, mappername, mirrorRoot, mtex, [specular_reflect], mtex.raymir_factor):
                    used = True
                    mirrorRoot = lname
            #
            if mtex.use_map_normal:
                lname = "bump_layer%x" % i
                if self.writeTexLayer(lname, mappername, bumpRoot, mtex, [0], mtex.normal_factor):
                    used = True
                    bumpRoot = lname
            #
            if used:
                self.writeMappingNode(mappername, mtex)
            i += 1

        yi.paramsEndList()
        if diffRoot.startswith('diff_'):        yi.paramsSetString("diffuse_shader", diffRoot)
        if mcolRoot.startswith('mircol_'):      yi.paramsSetString("mirror_color_shader", mcolRoot)
        if transpRoot.startswith('transp_'):    yi.paramsSetString("transparency_shader", transpRoot)
        if translRoot.startswith('translu_'):   yi.paramsSetString("translucency_shader", translRoot)
        if mirrorRoot.startswith('mirr_'):      yi.paramsSetString("mirror_shader", mirrorRoot)
        if bumpRoot.startswith('bump_'):        yi.paramsSetString("bump_shader", bumpRoot)

        return yi.createMaterial(self.namehash(mat))

    def blendParams(self, mat, linked_node):
        #
        materialParams = {}
        nodemat = self.useMaterialNodes and linked_node is not None
        
        materialParams = {
            'material1'     : linked_node.blendOne      if nodemat else mat.bounty.blendOne,
            'material2'     : linked_node.blendTwo      if nodemat else mat.bounty.blendTwo,
            "blend_value"   : linked_node.blend_amount  if nodemat else mat.bounty.blend_value
        }          
        return materialParams
    #
    def writeBlendShader(self, mat, linked_node):
        yi = self.yi
        yi.paramsClearAll()
        #
        params = self.blendParams(mat, linked_node)

        yi.paramsSetString("type", "blend_mat")
        try:
            mat1 = bpy.data.materials[params.get('material1')]
            blendone = self.namehash(mat1)
        except:
            blendone = 'defaultMat'
        yi.paramsSetString("material1", blendone)
        #
        try:
            mat2 = bpy.data.materials[params.get('material2')]
            blendtwo = self.namehash(mat2)
        except:
            blendtwo = 'defaultMat'
        yi.paramsSetString("material2", blendtwo)
        
        i = 0

        maskRoot = ''
        used_textures = self.getUsedTextures(mat)

        for mtex in used_textures:
            if mtex.texture.type == 'NONE':
                continue

            used = False
            mappername = "map%x" % i

            if mtex.use_map_diffuse:
                layername = "mask_layer%x" % i
                if self.writeTexLayer(layername, mappername, maskRoot, mtex, [0], mtex.diffuse_factor):
                    used = True
                    maskRoot = layername
            #
            if used:
                self.writeMappingNode(mappername, mtex)
            i += 1

        yi.paramsEndList()

        # if we have a blending map, disable the blend_value
        blendValue = params.get('blend_value', mat.bounty.blend_value)
        if maskRoot.startswith("mask_"):
            yi.paramsSetString("mask", maskRoot)
            blendValue = 0
        #
        yi.paramsSetFloat("blend_value", blendValue)
        #
        yi.printInfo("Exporter: Blend material with: [" + blendone + "] [" + blendtwo + "]")
        
        return yi.createMaterial(self.namehash(mat))

    def writeMatteShader(self, mat):
        yi = self.yi
        yi.paramsClearAll()
        yi.paramsSetString("type", "shadow_mat")
        return yi.createMaterial(self.namehash(mat))

    def writeNullMat(self, mat):
        yi = self.yi
        yi.paramsClearAll()
        yi.paramsSetString("type", "null")
        return yi.createMaterial(self.namehash(mat))
    
    def writeDefaultMat(self, mat):
        self.yi.paramsClearAll()
        self.yi.paramsSetString("type", "shinydiffusemat")
        self.yi.paramsSetColor("color", 0.8, 0.8, 0.8)
        self.yi.printInfo("Exporter: Creating Material \"defaultMat\"")
        return yi.createMaterial("defaultMat")
    
    def getNodeOut(self, mat):
        nodeOutName = 'None'
        if mat.bounty.nodetree != "":
            for nodeOut in bpy.data.node_groups[mat.bounty.nodetree].nodes:
                if nodeOut.bl_idname == 'MaterialOutputNode' and nodeOut.inputs[0].is_linked:
                    nodeOutName = nodeOut.name
                    print('out: ', nodeOutName)
                    break
        return nodeOutName
                
    def writeMaterial(self, mat, preview=False): 
        #
        self.preview = preview
        self.yi.printInfo("Exporter: Creating Material: \"" + self.namehash(mat) + "\"")
        ymat = None
        #paramsSet={}
        #
        self.useMaterialNodes = False
        outNodeName = self.getNodeOut(mat)
        linked_node = None
        if mat.bounty.nodetree != "" and outNodeName is not 'None':            
            inputNodeOut = bpy.data.node_groups[mat.bounty.nodetree].nodes[outNodeName].inputs[0]
            print('out name: ', inputNodeOut.name)
            # check nodetree
            if inputNodeOut.is_linked:
                # set linked_node..
                linked_node = inputNodeOut.links[0].from_node
                                  
                # find valid node type
                if linked_node.bl_label in validMaterialTypes:
                    #print('label: ',linked_node.bl_label)
                    mat.bounty.mat_type = linked_node.bl_label
                    self.useMaterialNodes = True
                else:
                    bpy.data.node_groups[mat.bounty.nodetree].links.remove(inputNodeOut.links[0])
                    linked_node = None
                    print('Not valid node has got connected. Ignoring nodetree')
        
        #
        if mat.name == "y_null":
            ymat = self.writeNullMat(mat)
            
        elif mat.bounty.mat_type in {"glass", "rough_glass"}:
            ymat = self.writeGlassShader(mat, linked_node)
            
        elif mat.bounty.mat_type in {"glossy", "coated_glossy"}:
            ymat = self.writeGlossyShader(mat, linked_node)
            
        elif mat.bounty.mat_type == "shinydiffusemat":            
            ymat = self.writeShinyDiffuseShader(mat, linked_node)
            
        elif mat.bounty.mat_type == "blend":            
            ymat = self.writeBlendShader(mat, linked_node)
        #
        elif mat.bounty.mat_type == "translucent":
            ymat = self.writeTranslucentShader(mat, linked_node)
        #
        else:
            ymat = self.writeNullMat(mat)

        self.materialMap[mat] = ymat
