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
from mathutils import Vector
from math import degrees, pi, sin, cos
from bpy.path import abspath

class yafLight:
    def __init__(self, interface, preview):
        self.yi = interface
        self.lightMat = None
        self.preview = preview

    def makeSphere(self, nu, nv, x, y, z, rad, mat):
        yi = self.yi

        # get next free id from interface
        ID = yi.getNextFreeID()

        yi.startGeometry()

        if not yi.startTriMesh(ID, 2 + (nu - 1) * nv, 2 * (nu - 1) * nv, False, False):
            yi.printError("Couldn't start trimesh!")

        yi.addVertex(x, y, z + rad)
        yi.addVertex(x, y, z - rad)
        for v in range(0, nv):
            t = v / float(nv)
            sin_v = sin(2.0 * pi * t)
            cos_v = cos(2.0 * pi * t)
            for u in range(1, nu):
                s = u / float(nu)
                sin_u = sin(pi * s)
                cos_u = cos(pi * s)
                yi.addVertex(x + cos_v * sin_u * rad, y + sin_v * sin_u * rad, z + cos_u * rad)

        for v in range(0, nv):
            yi.addTriangle(0, 2 + v * (nu - 1), 2 + ((v + 1) % nv) * (nu - 1), mat)
            yi.addTriangle(1, ((v + 1) % nv) * (nu - 1) + nu, v * (nu - 1) + nu, mat)
            for u in range(0, nu - 2):
                yi.addTriangle(2 + v * (nu - 1) + u, 2 + v * (nu - 1) + u + 1, 2 + ((v + 1) % nv) * (nu - 1) + u, mat)
                yi.addTriangle(2 + v * (nu - 1) + u + 1, 2 + ((v + 1) % nv) * (nu - 1) + u + 1, 2 + ((v + 1) % nv) * (nu - 1) + u, mat)

        yi.endTriMesh()
        yi.endGeometry()

        return ID

    def createLight(self, yi, lamp_object, matrix=None):
        # for use Blender properties
        lamp_data = lamp_object.data
        lamp_name = lamp_object.name
        
        # use exporter properties..
        lamp = lamp_object.data.bounty

        if matrix is None:
            matrix = lamp_object.matrix_world.copy()
        # matrix indexing (row, colums) changed in Blender rev.42816, for explanation see also:
        # http://wiki.blender.org/index.php/User:TrumanBlending/Matrix_Indexing
        pos = matrix.col[3]
        direct = matrix.col[2]
        # up = matrix[1]  /* UNUSED */
        to = pos - direct

        lampType = lamp.lamp_type
        power = lamp.yaf_energy
        color = lamp_data.color

        if self.preview:
            if lamp_name == "Lamp":
                pos = (-6, -4, 8, 1.0)
                power = 5
            elif lamp_name == "Lamp.001":
                pos = (6, -6, -2, 1.0)
                power = 6
            elif lamp_name == "Lamp.002":
                pos = (-2.9123109, -7.270790733, 4.439187765, 1.0)
                to = (-0.0062182024121284485, 0.6771485209465027, 1.8015732765197754, 1.0)
                power = 5
            elif lamp_name == "Lamp.008":
                lampType = "SUN"
                power = 0.8

        yi.paramsClearAll()

        yi.printInfo("Exporting Lamp: {0} [{1}]".format(lamp_name, lampType))

        if lamp.create_geometry:
            yi.paramsClearAll()
            yi.paramsSetColor("color", color[0], color[1], color[2])  # color for spherelight and area light geometry
            yi.paramsSetString("type", "light_mat")
            self.lightMat = self.yi.createMaterial(lamp_name)
            self.yi.paramsClearAll()

        if lampType == "POINT":
            yi.paramsSetString("type", "pointlight")
            yi.paramsSetBool("useGeometry", lamp.create_geometry)
            power = 0.5 * power * power
            #
            if lamp.use_sphere:
                yi.paramsSetString("type", "spherelight")
                yi.paramsSetInt("samples", lamp.yaf_samples)
                yi.paramsSetFloat("radius", lamp.yaf_sphere_radius)
                # use sphere light attenuation  
                power /= lamp.yaf_sphere_radius * lamp.yaf_sphere_radius
                #
                if lamp.create_geometry:
                    ID = self.makeSphere(24, 48, pos[0], pos[1], pos[2], lamp.yaf_sphere_radius, self.lightMat)
                    yi.paramsSetInt("object", ID)

        elif lampType == "SPOT":
            if self.preview and lamp_name == "Lamp.002":
                angle = 50
            else:
                #-------------------------------------------------------
                # Blender reports the angle of the full cone in radians
                # and we need half of the apperture angle in degrees
                #-------------------------------------------------------
                angle = degrees(lamp_data.spot_size) * 0.5

            yi.paramsSetString("type", "spotlight")
            ''' 
            fix issue when some spot_blend >= 0.70 with caustic photons
            ERROR: Index out of bounds in pdf1D_t::Sample: index, u, ptr, cdf = -1, 0, 00000000082D7840, 00000000082D7840
            '''
            if lamp_data.spot_blend > 0.650:
                lamp_data.spot_blend = 0.650
            yi.paramsSetFloat("cone_angle", angle)
            yi.paramsSetFloat("blend", lamp_data.spot_blend)
            yi.paramsSetPoint("to", to[0], to[1], to[2])
            yi.paramsSetBool("soft_shadows", lamp.spot_soft_shadows)
            yi.paramsSetFloat("shadowFuzzyness", lamp.shadow_fuzzyness)
            yi.paramsSetBool("photon_only", lamp.photon_only)
            yi.paramsSetInt("samples", lamp.yaf_samples)

        elif lampType == "SUN":
            yi.paramsSetString("type", "sunlight")
            yi.paramsSetInt("samples", lamp.yaf_samples)
            yi.paramsSetFloat("angle", lamp.angle)
            yi.paramsSetPoint("direction", direct[0], direct[1], direct[2])

        elif lampType == "DIRECTIONAL":
            yi.paramsSetString("type", "directional")
            yi.paramsSetPoint("direction", direct[0], direct[1], direct[2])
            yi.paramsSetBool("infinite", lamp.infinite)
            if not lamp.infinite:
                yi.paramsSetFloat("radius", lamp_data.shadow_soft_size)
                yi.paramsSetPoint("from", pos[0], pos[1], pos[2])

        elif lampType == "IES":
            yi.paramsSetString("type", "ieslight")
            yi.paramsSetPoint("to", to[0], to[1], to[2])
            ies_file = abspath(lamp.ies_file)
            if not any(ies_file) and not os.path.exists(ies_file):
                yi.printWarning("IES file not found for {0}".format(lamp_name))
                return False
            yi.paramsSetString("file", ies_file)
            yi.paramsSetInt("samples", lamp.yaf_samples)
            yi.paramsSetBool("soft_shadows", lamp.ies_soft_shadows)

        elif lampType == "AREA":
            sizeX = lamp_data.size
            sizeY = lamp_data.size
            if lamp_data.shape == 'RECTANGLE':
                sizeY = lamp_data.size_y
            matrix = lamp_object.matrix_world.copy()

            # generate an untransformed rectangle in the XY plane
            # with the light's position as the centerpoint and
            # transform it using its transformation matrix
            point = Vector((-sizeX / 2, -sizeY / 2, 0))
            corner1 = Vector((-sizeX / 2, sizeY / 2, 0))
            corner2 = Vector((sizeX / 2, sizeY / 2, 0))
            corner3 = Vector((sizeX / 2, -sizeY / 2, 0))

            point = matrix * point      # ----------------------------------
            corner1 = matrix * corner1  # use reverse vector multiply order
            corner2 = matrix * corner2  # API changed with rev. 38674
            corner3 = matrix * corner3  # ----------------------------------

            yi.paramsClearAll()
            if lamp.create_geometry:
                ID = yi.getNextFreeID()
                yi.startGeometry()
                yi.startTriMesh(ID, 4, 2, False, False, 0)

                yi.addVertex(point[0], point[1], point[2])
                yi.addVertex(corner1[0], corner1[1], corner1[2])
                yi.addVertex(corner2[0], corner2[1], corner2[2])
                yi.addVertex(corner3[0], corner3[1], corner3[2])
                yi.addTriangle(0, 1, 2, self.lightMat)
                yi.addTriangle(0, 2, 3, self.lightMat)
                yi.endTriMesh()
                yi.endGeometry()
                yi.paramsSetInt("object", ID)

            yi.paramsSetString("type", "arealight")
            yi.paramsSetInt("samples", lamp.yaf_samples)
            yi.paramsSetPoint("corner", point[0], point[1], point[2])
            yi.paramsSetPoint("point1", corner1[0], corner1[1], corner1[2])
            yi.paramsSetPoint("point2", corner3[0], corner3[1], corner3[2])

        # sunlight and directional light don't use 'from' parameter
        if lampType not in {"SUN", "DIRECTIONAL"}:
            yi.paramsSetPoint("from", pos[0], pos[1], pos[2])
        
        #
        yi.paramsSetColor("color", color[0], color[1], color[2])
        yi.paramsSetFloat("power", power)
        yi.createLight(lamp_name)

        return True
