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

import os
import bpy
import time
import math
import mathutils
import yafrayinterface


def multiplyMatrix4x4Vector4(matrix, vector):
    result = mathutils.Vector((0.0, 0.0, 0.0, 0.0))
    for i in range(4):
        result[i] = vector * matrix[i]  # use reverse vector multiply order, API changed with rev. 38674
        
    return result


class exportObject(object):
    def __init__(self, yi, mMap, preview):
        self.yi = yi
        self.materialMap = mMap
        self.is_preview = preview

    def setScene(self, scene):

        self.scene = scene

    def createCamera(self):

        yi = self.yi
        yi.printInfo("Exporting Camera")

        camera = self.scene.camera
        render = self.scene.render
        cam = camera.data
        
        # get cam worldspace transformation matrix, e.g. if cam is parented matrix_local does not work
        matrix = camera.matrix_world.copy()
        # matrix indexing (row, colums) changed in Blender rev.42816, for explanation see also:
        # http://wiki.blender.org/index.php/User:TrumanBlending/Matrix_Indexing
        pos = matrix.col[3]
        direction = matrix.col[2]
        up = pos + matrix.col[1]

        to = pos - direction

        x = int(render.resolution_x * render.resolution_percentage * 0.01)
        y = int(render.resolution_y * render.resolution_percentage * 0.01)

        yi.paramsClearAll() 

        yi.paramsSetString("type", cam.bounty.camera_type)

        if cam.bounty.use_clipping:
            yi.paramsSetFloat("nearClip", cam.clip_start)
            yi.paramsSetFloat("farClip", cam.clip_end)

        if cam.bounty.camera_type == "orthographic":
            yi.paramsSetFloat("scale", cam.ortho_scale)

        elif cam.bounty.camera_type in {"perspective", "architect"}:
            # Blenders GSOC 2011 project "tomato branch" merged into trunk.
            # Check for sensor settings and use them in yafaray exporter also.
            if cam.sensor_fit == 'AUTO':
                horizontal_fit = (x > y)
                sensor_size = cam.sensor_width
            elif cam.sensor_fit == 'HORIZONTAL':
                horizontal_fit = True
                sensor_size = cam.sensor_width
            else:
                horizontal_fit = False
                sensor_size = cam.sensor_height

            if horizontal_fit:
                f_aspect = 1.0
            else:
                f_aspect = x / y

            yi.paramsSetFloat("focal", cam.lens / (f_aspect * sensor_size))

            # DOF params, only valid for real camera
            # use DOF object distance if present or fixed DOF
            if cam.dof_object is not None:
                # use DOF object distance
                #dist = (pos.xyz - cam.dof_object.location.xyz).length
                dof_distance = (pos.xyz - cam.dof_object.location.xyz).length #dist
            else:
                # use fixed DOF distance
                dof_distance = cam.dof_distance

            yi.paramsSetFloat("dof_distance", dof_distance)
            yi.paramsSetFloat("aperture", cam.bounty.aperture)
            # bokeh params
            yi.paramsSetString("bokeh_type", cam.bounty.bokeh_type)
            yi.paramsSetString("bokeh_bias", cam.bounty.bokeh_bias)
            yi.paramsSetFloat("bokeh_rotation", cam.bounty.bokeh_rotation)

        elif cam.bounty.camera_type == "angular":
            yi.paramsSetBool("circular", cam.bounty.circular)
            yi.paramsSetBool("mirrored", cam.bounty.mirrored)
            yi.paramsSetFloat("max_angle", cam.bounty.max_angle)
            yi.paramsSetFloat("angle", cam.bounty.angular_angle)

        yi.paramsSetInt("resx", x)
        yi.paramsSetInt("resy", y)

        yi.paramsSetPoint("from", pos[0], pos[1], pos[2])
        yi.paramsSetPoint("up", up[0], up[1], up[2])
        yi.paramsSetPoint("to", to[0], to[1], to[2])
        yi.createCamera("cam")

    def getBBCorners(self, obj):
        bb = obj.bound_box   # look bpy.types.Object if there is any problem

        bbmin = [1e10, 1e10, 1e10]
        bbmax = [-1e10, -1e10, -1e10]

        for corner in bb:
            for i in range(3):
                if corner[i] < bbmin[i]:
                    bbmin[i] = corner[i]
                if corner[i] > bbmax[i]:
                    bbmax[i] = corner[i]

        return bbmin, bbmax

    def get4x4Matrix(self, matrix):

        ret = yafrayinterface.matrix4x4_t()

        for i in range(4):
            for j in range(4):
                ret.setVal(i, j, matrix[i][j])

        return ret

    def writeObject(self, obj, matrix=None):

        if not matrix:
            matrix = obj.matrix_world.copy()

        if obj.bounty.geometry_type == "volume_region":
            self.writeVolumeObject(obj, matrix)

        elif obj.bounty.geometry_type == "mesh_light":
            self.writeMeshLight(obj, matrix)

        elif obj.bounty.geometry_type == "portal_light":
            self.writeBGPortal(obj, matrix)

        elif obj.particle_systems:  # Particle Hair system
            self.writeParticleStrands(obj, matrix)

        else:  # The rest of the object types
            self.writeMesh(obj, matrix)

    def writeInstanceBase(self, object):

        # Generate unique object ID
        ID = self.yi.getNextFreeID()

        self.yi.printInfo("Exporting Base Mesh: {0} with ID: {1:d}".format(object.name, ID))

        obType = 512  # Create this geometry object as a base object for instances

        self.writeGeometry(ID, object, None, obType)  # We want the vertices in object space

        return ID

    def writeInstance(self, oID, obj2WorldMatrix, name):

        self.yi.printInfo("Exporting Instance of {0} [ID = {1:d}]".format(name, oID))

        mat4 = obj2WorldMatrix.to_4x4()
        # mat4.transpose() --> not needed anymore: matrix indexing changed with Blender rev.42816

        o2w = self.get4x4Matrix(mat4)

        self.yi.addInstance(oID, o2w)
        del mat4
        del o2w

    def writeMesh(self, object, matrix):

        self.yi.printInfo("Exporting Mesh: {0}".format(object.name))

        # Generate unique object ID
        ID = self.yi.getNextFreeID()

        self.writeGeometry(ID, object, matrix)  # obType in 0, default, the object is rendered

    def writeBGPortal(self, object, matrix):
        # use object subclass properties
        obj = object.bounty

        self.yi.printInfo("Exporting Background Portal Light: {0}".format(object.name))

        # Generate unique object ID
        ID = self.yi.getNextFreeID()

        self.yi.paramsClearAll()
        self.yi.paramsSetString("type", "bgPortalLight")
        self.yi.paramsSetFloat("power", obj.bgp_power)
        self.yi.paramsSetInt("samples", obj.bgp_samples)
        self.yi.paramsSetInt("object", ID)
        self.yi.paramsSetBool("with_caustic", obj.bgp_with_caustic)
        self.yi.paramsSetBool("with_diffuse", obj.bgp_with_diffuse)
        self.yi.paramsSetBool("photon_only", obj.bgp_photon_only)
        self.yi.createLight(object.name)

        obType = 256  # Makes object invisible to the renderer (doesn't enter the kdtree)

        self.writeGeometry(ID, object, matrix, obType)

    def writeMeshLight(self, object, matrix):
        # use object subclass properties
        obj = object.bounty        

        self.yi.printInfo("Exporting Meshlight: {0}".format(object.name))

        # Generate unique object ID
        ID = self.yi.getNextFreeID()

        ml_matname = "ML_"
        ml_matname += object.name + "." + str(object.__hash__())

        self.yi.paramsClearAll()
        self.yi.paramsSetString("type", "light_mat")
        self.yi.paramsSetBool("double_sided", obj.ml_double_sided)
        c = obj.ml_color
        self.yi.paramsSetColor("color", c[0], c[1], c[2])
        self.yi.paramsSetFloat("power", obj.ml_power)
        ml_mat = self.yi.createMaterial(ml_matname)

        self.materialMap[ml_matname] = ml_mat

        # Export mesh light
        self.yi.paramsClearAll()
        self.yi.paramsSetString("type", "meshlight")
        self.yi.paramsSetBool("double_sided", obj.ml_double_sided)
        c = obj.ml_color
        self.yi.paramsSetColor("color", c[0], c[1], c[2])
        self.yi.paramsSetFloat("power", obj.ml_power)
        self.yi.paramsSetInt("samples", obj.ml_samples)
        self.yi.paramsSetInt("object", ID)
        self.yi.createLight(object.name)

        self.writeGeometry(ID, object, matrix, 0, ml_mat)  # obType in 0, default, the object is rendered

    def writeVolumeObject(self, object, matrix):
        # use object subclass properties
        obj = object.bounty

        self.yi.printInfo("Exporting Volume Region: {0}".format(object.name))

        yi = self.yi
        # me = obj.data  /* UNUSED */
        # me_materials = me.materials  /* UNUSED */

        yi.paramsClearAll()

        if obj.vol_region == 'ExpDensity Volume':
            yi.paramsSetString("type", "ExpDensityVolume")
            yi.paramsSetFloat("a", obj.vol_height)
            yi.paramsSetFloat("b", obj.vol_steepness)

        elif obj.vol_region == 'Uniform Volume':
            yi.paramsSetString("type", "UniformVolume")

        elif obj.vol_region == 'Noise Volume':
            if not object.active_material:
                yi.printError("Volume object ({0}) is missing the materials".format(object.name))
            elif not object.active_material.active_texture:
                yi.printError("Volume object's material ({0}) is missing the noise texture".format(object.name))
            else:
                texture = object.active_material.active_texture

                yi.paramsSetString("type", "NoiseVolume")
                yi.paramsSetFloat("sharpness", obj.vol_sharpness)
                yi.paramsSetFloat("cover", obj.vol_cover)
                yi.paramsSetFloat("density", obj.vol_density)
                yi.paramsSetString("texture", texture.name)
            
        # common parameters
        yi.paramsSetFloat("sigma_a", obj.vol_absorp)
        yi.paramsSetFloat("sigma_s", obj.vol_scatter)
        yi.paramsSetInt("attgridScale", self.scene.world.bounty.v_int_attgridres)

        # Calculate BoundingBox: get the low corner (minx, miny, minz)
        # and the up corner (maxx, maxy, maxz) then apply object scale,
        # also clamp the values to min: -1e10 and max: 1e10

        mesh = object.to_mesh(self.scene, True, 'RENDER')
        mesh.transform(matrix)

        vec = [j for v in mesh.vertices for j in v.co]

        yi.paramsSetFloat("minX", max(min(vec[0::3]), -1e10))
        yi.paramsSetFloat("minY", max(min(vec[1::3]), -1e10))
        yi.paramsSetFloat("minZ", max(min(vec[2::3]), -1e10))
        yi.paramsSetFloat("maxX", min(max(vec[0::3]), 1e10))
        yi.paramsSetFloat("maxY", min(max(vec[1::3]), 1e10))
        yi.paramsSetFloat("maxZ", min(max(vec[2::3]), 1e10))

        yi.createVolumeRegion("VR.{0}-{1}".format(obj.name, str(obj.__hash__())))
        bpy.data.meshes.remove(mesh)

    def writeGeometry(self, ID, obj, matrix, obType=0, oMat=None):

        mesh = obj.to_mesh(self.scene, True, 'RENDER')
        isSmooth = False
        hasOrco = False
        # test for UV Map after BMesh API changes
        uv_texture = mesh.tessface_uv_textures if 'tessface_uv_textures' in dir(mesh) else mesh.uv_textures
        # test for faces after BMesh API changes
        face_attr = 'faces' if 'faces' in dir(mesh) else 'tessfaces'
        hasUV = len(uv_texture) > 0  # check for UV's

        if face_attr == 'tessfaces':
            if not mesh.tessfaces and mesh.polygons:
                # BMesh API update, check for tessellated faces, if needed calculate them...
                mesh.update(calc_tessface=True)

            if not mesh.tessfaces:
                # if there are no faces, no need to write geometry, remove mesh data then...
                bpy.data.meshes.remove(mesh)
                return
        else:
            if not mesh.faces:
                # if there are no faces, no need to write geometry, remove mesh data then...
                bpy.data.meshes.remove(mesh)
                return

        # Check if the object has an orco mapped texture
        for mat in [mmat for mmat in mesh.materials if mmat is not None]:
            for m in [mtex for mtex in mat.texture_slots if mtex is not None]:
                if m.texture_coords == 'ORCO':
                    hasOrco = True
                    break
            if hasOrco:
                break

        # normalized vertex positions for orco mapping
        ov = []

        if hasOrco:
            # Keep a copy of the untransformed vertex and bring them
            # into a (-1 -1 -1) (1 1 1) bounding box
            bbMin, bbMax = self.getBBCorners(obj)

            delta = []

            for i in range(3):
                delta.append(bbMax[i] - bbMin[i])
                if delta[i] < 0.0001:
                    delta[i] = 1

            # use untransformed mesh's vertices
            for v in mesh.vertices:
                normCo = []
                for i in range(3):
                    normCo.append(2 * (v.co[i] - bbMin[i]) / delta[i] - 1)

                ov.append([normCo[0], normCo[1], normCo[2]])

        # Transform the mesh after orcos have been stored and only if matrix exists
        if matrix is not None:
            mesh.transform(matrix)

        self.yi.paramsClearAll()
        self.yi.startGeometry()

        self.yi.startTriMesh(ID, len(mesh.vertices), len(getattr(mesh, face_attr)), hasOrco, hasUV, obType)

        for ind, v in enumerate(mesh.vertices):
            if hasOrco:
                self.yi.addVertex(v.co[0], v.co[1], v.co[2], ov[ind][0], ov[ind][1], ov[ind][2])
            else:
                self.yi.addVertex(v.co[0], v.co[1], v.co[2])

        for index, f in enumerate(getattr(mesh, face_attr)):
            if f.use_smooth:
                isSmooth = True

            if oMat:
                ymaterial = oMat
            else:
                ymaterial = self.getFaceMaterial(mesh.materials, f.material_index, obj.material_slots)

            co = None
            if hasUV:

                if self.is_preview:
                    co = uv_texture[0].data[index].uv
                else:
                    co = uv_texture.active.data[index].uv

                uv0 = self.yi.addUV(co[0][0], co[0][1])
                uv1 = self.yi.addUV(co[1][0], co[1][1])
                uv2 = self.yi.addUV(co[2][0], co[2][1])

                self.yi.addTriangle(f.vertices[0], f.vertices[1], f.vertices[2], uv0, uv1, uv2, ymaterial)
            else:
                self.yi.addTriangle(f.vertices[0], f.vertices[1], f.vertices[2], ymaterial)

            if len(f.vertices) == 4:
                if hasUV:
                    uv3 = self.yi.addUV(co[3][0], co[3][1])
                    self.yi.addTriangle(f.vertices[0], f.vertices[2], f.vertices[3], uv0, uv2, uv3, ymaterial)
                else:
                    self.yi.addTriangle(f.vertices[0], f.vertices[2], f.vertices[3], ymaterial)

        self.yi.endTriMesh()

        if isSmooth and mesh.use_auto_smooth:
            self.yi.smoothMesh(0, math.degrees(mesh.auto_smooth_angle))
        elif isSmooth and obj.type == 'FONT':  # getting nicer result with smooth angle 60 degr. for text objects
            self.yi.smoothMesh(0, 60)
        elif isSmooth:
            self.yi.smoothMesh(0, 181)

        self.yi.endGeometry()

        bpy.data.meshes.remove(mesh)

    def getFaceMaterial(self, meshMats, matIndex, matSlots):

        ymaterial = self.materialMap["default"]

        if self.scene.bounty.gs_clay_render:
            ymaterial = self.materialMap["clay"]
        elif len(meshMats) and meshMats[matIndex]:
            mat = meshMats[matIndex]
            if mat in self.materialMap:
                ymaterial = self.materialMap[mat]
        else:
            for mat_slots in [ms for ms in matSlots if ms.material in self.materialMap]:
                ymaterial = self.materialMap[mat_slots.material]

        return ymaterial
    
    def defineStrandValues(self, material):
        #
        if material.strand.use_blender_units:
            strandStart = material.strand.root_size
            strandEnd = material.strand.tip_size
            strandShape = material.strand.shape
        else:  # Blender unit conversion
            strandStart = material.strand.root_size / 100
            strandEnd = material.strand.tip_size / 100
            strandShape = material.strand.shape
        return strandStart, strandEnd, strandShape
    
    def writeParticleStrands(self, obj, matrix):

        yi = self.yi
        totalNumberOfHairs = 0
        
        renderEmitter = False
        if hasattr(obj, 'particle_systems') == False:
            return
        # Check for hair particles:
        for pSys in obj.particle_systems:
            for mod in [m for m in obj.modifiers if (m is not None) and (m.type == 'PARTICLE_SYSTEM')]:
                if (pSys.settings.render_type == 'PATH') and mod.show_render and (pSys.name == mod.particle_system.name):
                    yi.printInfo("Exporter: Creating Hair Particle System {!r}".format(pSys.name))
                    tstart = time.time()
                    #-----------------------------------------------
                    # set particle material values. if don't have
                    # material assigned in blender, use default one
                    #-----------------------------------------------
                    strandStart = 0.01
                    strandEnd = 0.01
                    strandShape = 0.0                    
                    hairMat = "default"  
                                        
                    if obj.active_material is not None:
                        hairMat = obj.active_material
                        strandStart, strandEnd, strandShape = self.defineStrandValues(hairMat)
                    # exception: if clay render is activated
                    if self.scene.bounty.gs_clay_render:
                        hairMat = "clay"
                    #
                    pSys.set_resolution(self.scene, obj, 'RENDER')    
                    steps = pSys.settings.draw_step
                    steps = 3 ** steps # or (power of 2 rather than 3) + 1 # Formerly : len(particle.hair_keys)
                    #print(steps)
                            
                    totalNumberOfHairs = ( len(pSys.particles) + len(pSys.child_particles) )
                    #
                    prtvis = True # False
                    #for particle in pSys.particles:
                    #    if particle.is_exist and particle.is_visible:
                    #        prtvis = True
                    for particleIdx in range(0, totalNumberOfHairs):
                        #
                        #initCo = obj.matrix_world.inverted()*(pSys.co_hair(obj, pindex, 0))
                        # move here
                        CID = yi.getNextFreeID()
                        yi.paramsClearAll()
                        yi.startGeometry()
                        yi.startCurveMesh(CID, prtvis)
                        #
                        for step in range(0, steps):
                            co = pSys.co_hair(obj, particleIdx, step)
                            if not co.length_squared == 0:
                                yi.addVertex(co[0], co[1], co[2])                            
                        #
                        yi.endCurveMesh(self.materialMap[hairMat], strandStart, strandEnd, strandShape)
                        # TODO: keep object smooth
                        #yi.smoothMesh(CID, 60.0)
                        yi.endGeometry()
                    yi.printInfo("Exporter: Particle creation time: {0:.3f}".format(time.time() - tstart))
                    
                    #---------------------------------------------------------------------------------------
                    if pSys.settings.use_render_emitter:
                        renderEmitter = True
                else:
                    self.writeMesh(obj, matrix)
            
            # total hair's for each particle system              
            yi.printInfo("Exporter: Total hair's created: {0} ".format(totalNumberOfHairs))
            
        # We only need to render emitter object once
        if renderEmitter:
            self.writeMesh(obj, matrix)
