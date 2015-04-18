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

class TheBountyMaterialWrite:
    def __init__(self, interface, mMap, texMap):
        self.yi = interface
        self.materialMap = mMap
        self.textureMap = texMap

    def namehash(self, obj):
        nh = obj.name + "-" + str(obj.__hash__())
        return nh

    def getUsedTextures(self, material):
        used_textures = []
        for tex_slot in material.texture_slots:
            if tex_slot and tex_slot.use and tex_slot.texture:
                used_textures.append(tex_slot)

        return used_textures

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
        isImage = tex.yaf_tex_type == 'IMAGE'

        isColored = False
        if (isImage or (tex.yaf_tex_type == 'VORONOI' and tex.color_mode not in 'INTENSITY')):
            isColored = True
        yi.paramsSetBool("color_input", isColored)
        
        useAlpha = False        
        if isImage:
            useAlpha = (tex.yaf_use_alpha) and not(tex.use_calculate_alpha)

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

    def writeMappingNode(self, name, texname, mtex):
        yi = self.yi
        yi.paramsPushList()

        yi.paramsSetString("element", "shader_node")
        yi.paramsSetString("type", "texture_mapper")
        yi.paramsSetString("name", name)
        yi.paramsSetString("texture", texname)
        
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

    def writeGlassShader(self, mat):

        yi = self.yi
        yi.paramsClearAll()
        
        # add refraction roughness for roughglass material
        if mat.bounty.mat_type == "rough_glass":
            yi.paramsSetString("type", "rough_glass")
            yi.paramsSetFloat("alpha", mat.bounty.refr_roughness)
        else:
            yi.paramsSetString("type", "glass")

        yi.paramsSetFloat("IOR", mat.bounty.IOR_refraction)  # added IOR for refraction
        filt_col = mat.bounty.filter_color
        mir_col = mat.bounty.glass_mir_col
        tfilt = mat.bounty.glass_transmit
        abs_col = mat.bounty.absorption

        yi.paramsSetColor("filter_color", filt_col[0], filt_col[1], filt_col[2])
        yi.paramsSetColor("mirror_color", mir_col[0], mir_col[1], mir_col[2])
        yi.paramsSetFloat("transmit_filter", tfilt)

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
                self.writeMappingNode(mappername, mtex.texture.name, mtex)
                i += 1

        yi.paramsEndList()
        if len(mcolRoot) > 0:
            yi.paramsSetString("mirror_color_shader", mcolRoot)
        if len(bumpRoot) > 0:
            yi.paramsSetString("bump_shader", bumpRoot)

        return yi.createMaterial(self.namehash(mat))

    def writeGlossyShader(self, mat):
        yi = self.yi
        yi.paramsClearAll()

        #-------------------------------------------
        # Add IOR and mirror color for coated glossy
        #-------------------------------------------
        if mat.bounty.mat_type == "coated_glossy":
            #
            yi.paramsSetString("type", "coated_glossy")
            yi.paramsSetFloat("IOR", mat.bounty.IOR_reflection)
            mir_col = mat.bounty.coat_mir_col
            yi.paramsSetColor("mirror_color", mir_col[0], mir_col[1], mir_col[2])
        else:
            yi.paramsSetString("type", "glossy")

        #diffuse_color = mat.diffuse_color
        diffuse_color = mat.bounty.diff_color
        glossy_color = mat.bounty.glossy_color

        yi.paramsSetColor("diffuse_color", diffuse_color[0], diffuse_color[1], diffuse_color[2])
        yi.paramsSetColor("color", glossy_color[0], glossy_color[1], glossy_color[2])
        yi.paramsSetFloat("glossy_reflect", mat.bounty.glossy_reflect)
        yi.paramsSetFloat("exponent", mat.bounty.exponent)
        yi.paramsSetFloat("diffuse_reflect", mat.bounty.diffuse_reflect)
        yi.paramsSetBool("as_diffuse", mat.bounty.as_diffuse)
        yi.paramsSetBool("anisotropic", mat.bounty.anisotropic)
        yi.paramsSetFloat("exp_u", mat.bounty.exp_u)
        yi.paramsSetFloat("exp_v", mat.bounty.exp_v)

        # init shader values..
        diffRoot = glossRoot = glRefRoot = bumpRoot = ''
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
                if self.writeTexLayer(lname, mappername, glRefRoot, mtex, [mat.bounty.glossy_reflect], mtex.specular_factor):
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
                self.writeMappingNode(mappername, mtex.texture.name, mtex)
            i += 1

        yi.paramsEndList()
        
        if len(diffRoot) > 0:
            yi.paramsSetString("diffuse_shader", diffRoot)
        if len(glossRoot) > 0:
            yi.paramsSetString("glossy_shader", glossRoot)
        if len(glRefRoot) > 0:
            yi.paramsSetString("glossy_reflect_shader", glRefRoot)
        if len(bumpRoot) > 0:
            yi.paramsSetString("bump_shader", bumpRoot)

        if mat.bounty.brdf_type == "oren-nayar":  # oren-nayar fix for glossy
            yi.paramsSetString("diffuse_brdf", "Oren-Nayar")
            yi.paramsSetFloat("sigma", mat.bounty.sigma)

        return yi.createMaterial(self.namehash(mat))
    
    def writeTranslucentShader(self, mat):
        yi = self.yi
        yi.paramsClearAll()
        yi.paramsSetString("type", "translucent")
        yi.paramsSetFloat("IOR", mat.bounty.sssIOR)
        
        #diffColor   = mat.diffuse_color #sssColor
        diffColor   = mat.bounty.diff_color #sssColor
        glossyColor = mat.bounty.glossy_color;
        specColor   = mat.bounty.sssSpecularColor
        sigmaA      = mat.bounty.sssSigmaA
        sigmaS      = mat.bounty.sssSigmaS
        
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
        diffRoot = glossRoot = glRefRoot = transpRoot = translRoot = bumpRoot = ''
        
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
                self.writeMappingNode(mappername, mtex.texture.name, mtex)
            i +=1
        
        yi.paramsEndList()
        if len(diffRoot) > 0:   yi.paramsSetString("diffuse_shader", diffRoot)
        if len(glossRoot) > 0:  yi.paramsSetString("glossy_shader", glossRoot)
        if len(glRefRoot) > 0:  yi.paramsSetString("glossy_reflect_shader", glRefRoot)
        if len(bumpRoot) > 0:   yi.paramsSetString("bump_shader", bumpRoot)
        if len(transpRoot) > 0: yi.paramsSetString("sigmaA_shader", transpRoot)
        if len(translRoot) > 0: yi.paramsSetString("sigmaS_shader", translRoot)

        return yi.createMaterial(self.namehash(mat))
    #-------->
    
    def writeShinyDiffuseShader(self, mat):
        yi = self.yi
        yi.paramsClearAll()

        yi.paramsSetString("type", "shinydiffusemat")
        #---------------------------------------------------
        # know issue with the use of own variable diff_color
        # and the background texture on material preview
        #---------------------------------------------------
        #bCol = mat.bounty.diff_color
        bCol = mat.diffuse_color
        mirCol = mat.bounty.mirr_color
        bSpecr = mat.bounty.specular_reflect
        bTransp = mat.bounty.transparency
        bTransl = mat.translucency
        bEmit = mat.bounty.emittance
        
        # for fix dark preview
        if self.preview:
            if mat.name.startswith("checker"):
                bEmit = 2.50

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
                if self.writeTexLayer(lname, mappername, diffRoot, mtex, bCol, mtex.diffuse_color_factor):
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
                if self.writeTexLayer(lname, mappername, transpRoot, mtex, [bTransp], mtex.alpha_factor):
                    used = True
                    transpRoot = lname
            #
            if mtex.use_map_translucency:
                lname = "translu_layer%x" % i
                if self.writeTexLayer(lname, mappername, translRoot, mtex, [bTransl], mtex.translucency_factor):
                    used = True
                    translRoot = lname
            #
            if mtex.use_map_raymir:
                lname = "mirr_layer%x" % i
                if self.writeTexLayer(lname, mappername, mirrorRoot, mtex, [bSpecr], mtex.raymir_factor):
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
                self.writeMappingNode(mappername, mtex.texture.name, mtex)
            i += 1

        yi.paramsEndList()
        if len(diffRoot) > 0:
            yi.paramsSetString("diffuse_shader", diffRoot)
        if len(mcolRoot) > 0:
            yi.paramsSetString("mirror_color_shader", mcolRoot)
        if len(transpRoot) > 0:
            yi.paramsSetString("transparency_shader", transpRoot)
        if len(translRoot) > 0:
            yi.paramsSetString("translucency_shader", translRoot)
        if len(mirrorRoot) > 0:
            yi.paramsSetString("mirror_shader", mirrorRoot)
        if len(bumpRoot) > 0:
            yi.paramsSetString("bump_shader", bumpRoot)

        yi.paramsSetColor("color", bCol[0], bCol[1], bCol[2])
        yi.paramsSetFloat("transparency", bTransp)
        yi.paramsSetFloat("translucency", bTransl)
        yi.paramsSetFloat("diffuse_reflect", mat.bounty.diffuse_reflect)
        yi.paramsSetFloat("emit", bEmit)
        yi.paramsSetFloat("transmit_filter", mat.bounty.transmit_filter)

        yi.paramsSetFloat("specular_reflect", bSpecr)
        yi.paramsSetColor("mirror_color", mirCol[0], mirCol[1], mirCol[2])
        yi.paramsSetBool("fresnel_effect", mat.bounty.fresnel_effect)
        yi.paramsSetFloat("IOR", mat.bounty.IOR_reflection)

        if mat.bounty.brdf_type == "oren-nayar":  # oren-nayar fix for shinydiffuse
            yi.paramsSetString("diffuse_brdf", "oren_nayar")
            yi.paramsSetFloat("sigma", mat.bounty.sigma)

        return yi.createMaterial(self.namehash(mat))

    def writeBlendShader(self, mat):
        yi = self.yi
        yi.paramsClearAll()

        yi.printInfo("Exporter: Blend material with: [" + mat.bounty.blendmaterial1 + "] [" + mat.bounty.blendmaterial2 + "]")
        yi.paramsSetString("type", "blend_mat")
        yi.paramsSetString("material1", self.namehash(bpy.data.materials[mat.bounty.blendmaterial1]))
        yi.paramsSetString("material2", self.namehash(bpy.data.materials[mat.bounty.blendmaterial2]))

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
                self.writeMappingNode(mappername, mtex.texture.name, mtex)
            i += 1

        yi.paramsEndList()

        # if we have a blending map, disable the blend_value
        if len(maskRoot) > 0:
            yi.paramsSetString("mask", maskRoot)
            yi.paramsSetFloat("blend_value", 0)
        else:
            yi.paramsSetFloat("blend_value", mat.bounty.blend_value)

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
        #ymat = self.yi.createMaterial("defaultMat")
        #self.materialMap["default"] = ymat
        return yi.createMaterial("defaultMat")

    def writeMaterial(self, mat, preview=False): # test
        self.preview = preview
        self.yi.printInfo("Exporter: Creating Material: \"" + self.namehash(mat) + "\"")
        ymat = None
        if mat.name == "y_null":
            ymat = self.writeNullMat(mat)
            
        elif mat.bounty.mat_type in {"glass", "rough_glass"}:
            ymat = self.writeGlassShader(mat)
            
        elif mat.bounty.mat_type in {"glossy", "coated_glossy"}:
            ymat = self.writeGlossyShader(mat)
            
        elif mat.bounty.mat_type == "shinydiffusemat":
            ymat = self.writeShinyDiffuseShader(mat)
            
        elif mat.bounty.mat_type == "blend":
            ymat = self.writeBlendShader(mat)
        #
        elif mat.bounty.mat_type == "translucent":
            ymat = self.writeTranslucentShader(mat)
        #
        else:
            ymat = self.writeNullMat(mat)

        self.materialMap[mat] = ymat
