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
glassLayers = ['Mirror', 'Bumpmap']
validDiffuseNodes=['Image']

validMaterialTypes=['shinydiffusemat', 'glossy', 'coated_glossy', 'glass', 'rough_glass', 'translucent', 'blend']

class TheBountyMaterialWrite:
    def __init__(self, interface, mMap, texMap, expMat):
        self.yi = interface
        self.materialMap = mMap
        self.textureMap = texMap
        self.exportMats= expMat

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
    def layerParams(self, layernode, mtex):
        #
        node = layernode is not None
        tex = mtex.texture
        # 'negative': False,           'texture_coord': 'UV',    'mapping_x': 'X', 'blend': 'mix', 
        # 'offset'  : [0.0, 0.0, 0.0], 'scale': [1.0, 1.0, 1.0], 'no_rgb': False,  'stencil': True, 
        # 'projection_type': 'FLAT',   'mapping_z': 'Z',         'mapping_y': 'Y'}
        textureLayerParams = {
            "name":'', 
            "input":'mapname', 
            "mode"          : switchBlendMode.get(layernode.get('blend')    if node else tex.bounty.blend, 0),
            "stencil"       : layernode.get('stencil')  if node else mtex.use_stencil, 
            "negative"      : layernode.get('negative') if node else mtex.invert, 
            "noRGB"         : layernode.get('no_rgb')   if node else mtex.use_rgb_to_intensity, 
            "def_col"       : (1,1,1), 
            "def_val"       : 1.0, 
            "color_input"   : False, 
            "use_alpha"     : False, 
            "upper_color"   : (1,1,1), 
            "upper_value"   : 0.0, 
            "upper_layer"   :'', 
            "colfac"        : 1.0, 
            "valfac"        : 1.0, 
            "do_color"      : False, 
            "do_scalar"     : True
        }
        return textureLayerParams
    
    def writeTexLayer(self, name, mapName, ulayer, mtex, dcol, factor, layer_node=None):
        #
        if mtex.name not in self.textureMap:
            return False
        # test
        tex = mtex.texture
        params = self.layerParams(layer_node, mtex)

        yi = self.yi
        yi.paramsPushList()
        yi.paramsSetString("element", "shader_node")
        yi.paramsSetString("type", "layer")
        yi.paramsSetString("name", name)

        yi.paramsSetString("input", mapName)

        # set texture blend mode, if not a supported mode then set it to 'MIX'
        #mode = switchBlendMode.get(tex.bounty.blend, 0)
        mode = params.get('mode')
        print('mode: ', mode)
        yi.paramsSetInt("mode", mode)
        yi.paramsSetBool("stencil", params.get('stencil')) #, mtex.use_stencil))

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
        "element":"shader_node", "type":"texture_mapper", "name":"map0", 
        "texture":"", "texco":"orco", "proj_x":0, "proj_y":1, "proj_z":2, 
        "mapping":"plain", "offset":0.0, "scale":1, "bump_strength":0.0         
    }
    def writeMappingNode(self, mapname, mtex):
        # test
        self.textureMappingParams.get('type','texture_mapper')
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
            
    
    def glassParams(self, material, node, with_nodes):
        #
        nodemat = with_nodes and node is not None
        mat = material.bounty
        materialParams = {                
            "mirror_color"      : node.inputs['Mirror'].glass_mir_col if nodemat else mat.glass_mir_col,
            "dispersion_power"  : node.dispersion_power if nodemat else mat.dispersion_power,
            "absorption_dist"   : node.absorption_dist  if nodemat else mat.absorption_dist,
            "transmit_filter"   : node.glass_transmit   if nodemat else mat.glass_transmit,
            "IOR"               : node.IOR_refraction   if nodemat else mat.IOR_refraction,
            "alpha"             : node.refr_roughness   if nodemat else mat.refr_roughness,
            "filter_color"      : node.filter_color     if nodemat else mat.filter_color,
            "fake_shadows"      : node.fake_shadows     if nodemat else mat.fake_shadows,
            "absorption"        : node.absorption       if nodemat else mat.absorption,
        }
        return materialParams
    
    def writeGlassShader(self, mat, node, with_nodes):

        yi = self.yi
        yi.paramsClearAll()
        #
        params = self.glassParams( mat, node, with_nodes)
        #
        yi.paramsSetString("type", mat.bounty.mat_type)
        if mat.bounty.mat_type == "rough_glass":
            yi.paramsSetFloat("alpha", params.get('alpha'))            
        yi.paramsSetFloat("IOR", params.get('IOR'))       
        
        filt_col = params.get('filter_color')
        yi.paramsSetColor("filter_color", filt_col[0], filt_col[1], filt_col[2])
        mir_col = params.get('mirror_color')
        yi.paramsSetColor("mirror_color", mir_col[0], mir_col[1], mir_col[2])
        yi.paramsSetFloat("transmit_filter", params.get('transmit_filter'))
        abs_col = params.get('absorption')
        yi.paramsSetColor("absorption", abs_col[0], abs_col[1], abs_col[2])
        yi.paramsSetFloat("absorption_dist", params.get('absorption_dist'))
        yi.paramsSetFloat("dispersion_power", params.get('dispersion_power'))
        yi.paramsSetBool("fake_shadows", params.get('fake_shadows'))

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
    
    def glossyParams(self, material, node, with_nodes):
        #
        nodemat = (with_nodes and node is not None)
        mat = material.bounty
        #
        matParams = {
            "diffuse_color"     : node.inputs['Diffuse'].diff_color         if nodemat else material.diffuse_color,
            "color"             : node.inputs['Glossy'].glossy_color        if nodemat else mat.glossy_color,
            "glossy_reflect"    : node.inputs['Specular'].glossy_reflect    if nodemat else mat.glossy_reflect,
            "IOR_reflection"    : node.IOR_reflection   if nodemat else mat.IOR_reflection,
            "diffuse_reflect"   : node.diffuse_reflect  if nodemat else mat.diffuse_reflect,
            "coat_mir_col"      : node.coat_mir_col     if nodemat else mat.coat_mir_col,
            "anisotropic"       : node.anisotropic      if nodemat else mat.anisotropic,
            "as_diffuse"        : node.as_diffuse       if nodemat else mat.as_diffuse,
            "brdf_type"         : node.brdf_type        if nodemat else mat.brdf_type,
            "exponent"          : node.exponent         if nodemat else mat.exponent,
            "exp_u"             : node.exp_u            if nodemat else mat.exp_u,
            "exp_v"             : node.exp_v            if nodemat else mat.exp_v,      
            "sigma"             : node.sigma            if nodemat else mat.sigma,
        }
        return matParams
            
    def writeGlossyShader(self, mat, node, with_nodes):
        yi = self.yi
        yi.paramsClearAll()
        #
        params = self.glossyParams(mat, node, with_nodes)
        #-------------------------------------------
        # Add IOR and mirror color for coated glossy
        #-------------------------------------------
        if mat.bounty.mat_type == "coated_glossy":
            yi.paramsSetFloat("IOR", params.get('IOR_reflection'))
            mir_col = params.get('coat_mir_col')
            yi.paramsSetColor("mirror_color", mir_col[0], mir_col[1], mir_col[2])
        
        diffuse_color = params.get('diffuse_color')
        glossy_color = params.get('color')
        glossy_reflect = params.get("glossy_reflect")

        yi.paramsSetColor("diffuse_color",  diffuse_color[0], diffuse_color[1], diffuse_color[2])
        yi.paramsSetColor("color", glossy_color[0], glossy_color[1], glossy_color[2])
        yi.paramsSetFloat("glossy_reflect", glossy_reflect)
        yi.paramsSetFloat("exponent", params.get('exponent'))
        yi.paramsSetFloat("diffuse_reflect", params.get('diffuse_reflect'))
        yi.paramsSetBool("as_diffuse", params.get('as_diffuse'))
        yi.paramsSetBool("anisotropic", params.get('anisotropic'))
        yi.paramsSetFloat("exp_u", params.get('exp_u'))
        yi.paramsSetFloat("exp_v", params.get('exp_v'))
        #
        brdf = 'lambert'
        if params.get('brdf_type') == "oren_nayar":  # oren-nayar fix for glossy
            brdf = 'Oren-Nayar'
            yi.paramsSetString("diffuse_brdf", brdf)
            yi.paramsSetFloat("sigma", params.get('sigma'))
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
    
    
    def sssParams(self, material, node, with_nodes):
        #
        nodemat = with_nodes and node is not None
        mat = material.bounty
        
        materialParams = {
            "color"             : node.inputs['Diffuse'].diff_color         if nodemat else material.diffuse_color,
            "glossy_color"      : node.inputs['Glossy'].glossy_color        if nodemat else mat.glossy_color,
            "glossy_reflect"    : node.inputs['Specular'].glossy_reflect    if nodemat else mat.glossy_reflect,
            #"specular_color"    : node.inputs['Specular'].mirror_color      if nodemat else mat.sssSpecularColor,
            "sigmaS_factor"     : node.sssSigmaS_factor if nodemat else mat.sssSigmaS_factor,
            "diffuse_reflect"   : node.diffuse_reflect  if nodemat else mat.diffuse_reflect,
            "sss_transmit"      : node.sss_transmit     if nodemat else mat.sss_transmit,
            "g"                 : node.phaseFuction     if nodemat else mat.phaseFuction,
            "sigmaA"            : node.sssSigmaA        if nodemat else mat.sssSigmaA,
            "sigmaS"            : node.sssSigmaS        if nodemat else mat.sssSigmaS,
            "exponent"          : node.exponent         if nodemat else mat.exponent,
            "IOR"               : node.sssIOR           if nodemat else mat.sssIOR,
        }
        return materialParams
    
    def writeTranslucentShader(self, mat, node, with_nodes):
        yi = self.yi
        yi.paramsClearAll()
        #
        params = self.sssParams(mat, node, with_nodes)
        
        diffColor   = params.get('color')
        glossyColor = params.get('glossy_color')
        specColor   = params.get('specular_color', mat.bounty.sssSpecularColor)
        sigmaA      = params.get('sigmaA')
        sigmaS      = params.get('sigmaS')
        
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
        yi.paramsSetFloat("g", mat.bounty.phaseFuction)
        
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
    
    
    def shinyParams(self, material, node, with_nodes):
        #
        nodemat = with_nodes and node is not None
        mat = material.bounty
        #
        params = {
            "color"             : node.inputs['Diffuse'].diff_color         if nodemat else material.diffuse_color,
            "specular_reflect"  : node.inputs['Specular'].specular_reflect  if nodemat else mat.specular_reflect,
            "transparency"      : node.inputs['Transparency'].transparency  if nodemat else mat.transparency,
            "translucency"      : node.inputs['Translucency'].translucency  if nodemat else mat.translucency,
            "mirror_color"      : node.inputs['Mirror'].mirror_color        if nodemat else mat.mirror_color,
            "diffuse_reflect"   : node.diffuse_reflect  if nodemat else mat.diffuse_reflect,
            "transmit_filter"   : node.transmit         if nodemat else mat.transmit_filter,
            "fresnel_effect"    : node.fresnel_effect   if nodemat else mat.fresnel_effect,
            "IOR"               : node.IOR_reflection   if nodemat else mat.IOR_reflection,
            "emit"              : node.emittance        if nodemat else mat.emittance,
            "diffuse_brdf"      : node.diffuse_brdf     if nodemat else mat.brdf_type,
            "sigma"             : node.sigma            if nodemat else mat.sigma,                                        
        }
        return params
       
    def writeShinyDiffuseShader(self, mat, node, with_nodes):
        
        yi = self.yi
        yi.paramsClearAll()
                
        params = self.shinyParams(mat, node, with_nodes)
        
        diffColor        = params.get('color')
        mirCol           = params.get('mirror_color')        
        specular_reflect = params.get('specular_reflect')
        transparency     = params.get('transparency')
        translucency     = params.get('translucency')
        brdf_model       = params.get('diffuse_brdf')

        yi.paramsSetString("type", 'shinydiffusemat')
        
        ##
        yi.paramsSetColor("color", diffColor[0], diffColor[1], diffColor[2])
        yi.paramsSetFloat("transparency", transparency)
        yi.paramsSetFloat("translucency", translucency)
        yi.paramsSetFloat("diffuse_reflect", params.get('diffuse_reflect'))
        yi.paramsSetFloat("emit", params.get('emit'))
        yi.paramsSetFloat("transmit_filter", params.get('transmit_filter'))

        yi.paramsSetFloat("specular_reflect", specular_reflect)
        yi.paramsSetColor("mirror_color", mirCol[0], mirCol[1], mirCol[2])
        yi.paramsSetBool("fresnel_effect", params.get('fresnel_effect'))
        yi.paramsSetFloat("IOR", params.get('IOR'))
        
        yi.paramsSetString("diffuse_brdf", brdf_model)
        if brdf_model == "oren_nayar":
            yi.paramsSetFloat("sigma", params.get('sigma'))
        #
        diff_layer_node = None
        if node is not None and node.inputs['Diffuse'].is_linked:
            #
            lparams = node.inputs['Diffuse'].getParams()['DiffuseLayer']
            print('params', lparams)
            diff_layer_node = lparams
        
        
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
            if mtex.use_map_color_diffuse or diff_layer_node is not None:
                lname = "diff_layer%x" % i
                factor = mtex.diffuse_color_factor
                #                     name,  mapName,    ulayer,   mtex, dcol,      factor, layer_node=None
                if self.writeTexLayer(lname, mappername, diffRoot, mtex, diffColor, factor, diff_layer_node):
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

    
    def blendParams(self, mat, node, with_nodes):
        #
        nodemat = with_nodes and node is not None
        materialParams = {
            'material1'   : node.BlendOne if nodemat else mat.bounty.blendOne,
            'material2'   : node.BlendTwo if nodemat else mat.bounty.blendTwo,
            'blend_value' : node.blend_amount if nodemat else mat.bounty.blend_value
        }          
        return materialParams
    
    def writeBlendShader(self, mat, node, with_nodes):
        yi = self.yi
        yi.paramsClearAll()
        #
        params = self.blendParams(mat, node, with_nodes)

        yi.paramsSetString("type", "blend_mat")
        # mat one
        mat1 = bpy.data.materials[params.get('material1', 'blendone')]
        blendone = self.namehash(mat1)        
        yi.paramsSetString("material1", blendone)
        
        # mat two
        mat2 = bpy.data.materials[params.get('material2', 'blendtwo')]
        blendtwo = self.namehash(mat2)
        yi.paramsSetString("material2", blendtwo)
        
        # mask texture        
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
        blendValue = params.get('blend_value')
        if maskRoot.startswith("mask_"):
            yi.paramsSetString("mask", maskRoot)
            blendValue = 0
        #
        yi.paramsSetFloat("blend_value", blendValue)
        #print('blending ', blendValue)
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
    
    def getNodeOutName(self, mat):
        #
        nodeOutName = 'None'
        if mat.bounty.nodetree != "":
            ntree = bpy.data.node_groups[mat.bounty.nodetree]
            for nodeOut in ntree.nodes:
                if nodeOut.bl_idname == 'MaterialOutputNode' and nodeOut.inputs['Surface'].is_linked:
                    nodeOutName = nodeOut.name
                    #print('out: ', nodeOutName)
                    break                    
                
        return nodeOutName
    
    def withNodes(self, mat):
        with_nodes = False
        outNodeName = self.getNodeOutName(mat)
        linked_node = None
        # test
        if mat.bounty.nodetree == "" or outNodeName == 'None':
            return with_nodes, linked_node
        # Checking if is linked
        #if mat.bounty.nodetree != "" and outNodeName is not 'None':
        ntree = bpy.data.node_groups[mat.bounty.nodetree]           
        inputNodeOut = ntree.nodes[outNodeName].inputs['Surface']
        # check nodetree
        if inputNodeOut.is_linked:
            # short version of handleBlendMat function
            # you need made double checking to 'materialMap' and 'exportedMaterials'
            if inputNodeOut.links[0].from_node.bl_label == 'blend':
                nodelink = inputNodeOut.links[0].from_node
                # one
                if nodelink.BlendOne in {"", mat.name}:
                    self.yi.printWarning("Not valid material for blend component. Using default 'blendone'")
                    nodelink.BlendOne = "blendone"
                mat1 = bpy.data.materials[nodelink.BlendOne]
                if mat1 not in self.exportMats and mat1 not in self.materialMap:
                    self.writeMaterial(mat1)
                    # add here only to export materials list, 
                    # to material map are added inside write material function
                    self.exportMats.add(mat1)
                    
                # two
                if nodelink.BlendTwo in {"", mat.name, mat1.name}:
                    self.yi.printWarning("Not valid material for blend component. Using default 'blendtwo'")
                    nodelink.BlendTwo = "blendtwo"
                mat2 = bpy.data.materials[nodelink.BlendTwo]
                if mat2 not in self.exportMats and mat2 not in self.materialMap:
                    self.writeMaterial(mat2)
                    self.exportMats.add(mat2)
                        
                with_nodes= True                             
            # check a valid node type
            if inputNodeOut.links[0].from_node.bl_label not in validMaterialTypes:
                #                
                ntree.links.remove(inputNodeOut.links[0])
                # Trying to connect a valid node among those that compose the node tree
                linked = False
                for n in ntree.nodes:
                    if n.bl_label in validMaterialTypes: # validReplaceNodes:
                        ntree.links.new(inputNodeOut, n.outputs[0])
                        linked = True
                        break                            
                # If no nodes are supported, one is created
                if not linked:
                    n = ntree.nodes.new("ShinyDiffuseShaderNode")
                    n.location = [-200, 0]
                    ntree.links.new(inputNodeOut, n.outputs[0])
                #
                with_nodes= True
                self.yi.printWarning('An invalid node has been connected. Changing to a valid one')
            #
            linked_node = inputNodeOut.links[0].from_node
            mat.bounty.mat_type = linked_node.bl_label
        #
        return with_nodes, linked_node
                
                
    def writeMaterial(self, mat, preview=False): 
        #
        self.preview = preview
        #self.yi.printInfo("Exporter: Creating Material: \"" + self.namehash(mat) + "\"")
        ymat = None
        with_nodes, linked_node = self.withNodes(mat)
        #
        if mat.name == "y_null":
            ymat = self.writeNullMat(mat)
            
        elif mat.bounty.mat_type in {"glass", "rough_glass"}:
            ymat = self.writeGlassShader(mat, linked_node, with_nodes)
            
        elif mat.bounty.mat_type in {"glossy", "coated_glossy"}:
            ymat = self.writeGlossyShader(mat, linked_node, with_nodes)
            
        elif mat.bounty.mat_type == "shinydiffusemat":            
            ymat = self.writeShinyDiffuseShader(mat, linked_node, with_nodes)
            
        elif mat.bounty.mat_type == "blend":            
            ymat = self.writeBlendShader(mat, linked_node, with_nodes)
        #
        elif mat.bounty.mat_type == "translucent":
            ymat = self.writeTranslucentShader(mat, linked_node, with_nodes)
        #
        else:
            ymat = self.writeNullMat(mat)

        self.materialMap[mat] = ymat
