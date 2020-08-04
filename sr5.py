import struct
from OBJ import obj
import ops as op
def char(c):
    # 1 byte
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    # 2 bytes
    return struct.pack('=h',w)

def dword(d):
    # 4 bytes
    return struct.pack('=l',d)

def color(r, g, b):
    return bytes([b, g, r])

#def baricentricas()

clear = color(0,0,0)

class Bitmap(object):
    def __init__(self, width, height):
        self.width = width 
        self.height = height 
        self.inicialColor = clear 
        self.glClear()
        self.Clear(0,0,0)
        self.__VPStartX = 0
        self.__VPStartY = 0
        self.__VPSizeX = 0
        self.__VPSizeY = 0
        self.__name = "image.bmp"
    def glClear(self):
        self.pixel = [
            [clear for x in range(self.width)]
            for y in range(self.height)
        ]
    def Clear(self,r,g,b):
        self.pixel = [
            [clear for x in range(self.width)]
            for y in range(self.height)
        ]

    def write(self, filename):
        archivo = open(filename, 'wb')

        archivo.write(bytes('B'.encode('ascii')))
        archivo.write(bytes('M'.encode('ascii')))

        archivo.write(dword(14 + 40 + self.width * self.height * 3))
        archivo.write(dword(0))
        archivo.write(dword(14 + 40))

        archivo.write(dword(40))
        archivo.write(dword(self.width))
        archivo.write(dword(self.height))
        archivo.write(word(1))
        archivo.write(word(24))
        archivo.write(dword(0))
        archivo.write(dword(self.width * self.height * 3))
        archivo.write(dword(0))
        archivo.write(dword(0))
        archivo.write(dword(0))
        archivo.write(dword(0))

        for x in range(self.height):
            for y in range(self.width):
                archivo.write(self.pixel[x][y])


        archivo.close()
    
    def glViewPort(self,x,y,width,height):
        self.__VPStartX = x
        self.__VPStartY = y
        self.__VPSizeX = width
        self.__VPSizeY = height

    
    def glClearColor(self,r,g,b):
        self.Clear(int(r*255),int(g*255),int(b*255))
    
    def point(self, x, y):
        self.pixel[y][x] = self.inicialColor    
    
    def glVertex(self,x,y):
        VPX = int(self.__VPSizeX*(x+1)*(1/2)+self.__VPStartX)
        VPY = int(self.__VPSizeY*(y+1)*(1/2)+self.__VPStartY)
        self.point(VPX,VPY)
    def glLine(self,x1,y1,x2,y2):
        x1 = int(self.__VPSizeX*(x1+1)*(1/2)+self.__VPStartX)
        y1 = int(self.__VPSizeY*(y1+1)*(1/2)+self.__VPStartY)
        x2 = int(self.__VPSizeX*(x2+1)*(1/2)+self.__VPStartX)
        y2 = int(self.__VPSizeY*(y2+1)*(1/2)+self.__VPStartY)
        dy = abs(y2 - y1)
        dx = abs(x2 - x1)
        pendiente = dy > dx
        if pendiente:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        if (x1 > x2):
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        dy = abs(y2 - y1)
        dx = abs(x2 - x1)
        offset = 0
        umbral = dx
        y = y1
        for x in range(x1, x2 + 1):
            if pendiente:
                self.point(y,x)
            else:
                self.point(x,y)

            offset += dy * 2
            if offset >= umbral:
                y +=1 if y1 < y2 else -1
                umbral += 2 * dx
    def glLineWin(self,x1,y1,x2,y2):
        dy = abs(y2 - y1)
        dx = abs(x2 - x1)
        pendiente = dy > dx
        if pendiente:
            x1, y1 = y1, x1
            x2, y2 = y2, x2
        if (x1 > x2):
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        dy = abs(y2 - y1)
        dx = abs(x2 - x1)
        offset = 0
        umbral = dx
        y = y1
        for x in range(x1, x2 + 1):
            if pendiente:
                self.point(y,x)
            else:
                self.point(x,y)

            offset += dy * 2
            if offset >= umbral:
                y +=1 if y1 < y2 else -1
                umbral += 2 * dx
    def glColor(self,r,g,b):
        self.inicialColor = color(int(r*255),int(g*255),int(b*255))
    
    def glFinish(self):
        self.write(self.__name)
    def loadModel(self, filename, translate, scale,normobj = False):
        model = obj(filename)

        for face in model.faces:

            vertCount = len(face)
            if normobj:
                for vert in range(vertCount):
                    
                    v0 = model.vertices[ int(face[vert][0]) - 1 ]
                    v1 = model.vertices[ int(face[(vert + 1) % vertCount][0]) - 1]

                    x0 = round(v0[0] * scale[0]  + translate[0])
                    y0 = round(v0[1] * scale[1]  + translate[1])
                    x1 = round(v1[0] * scale[0]  + translate[0])
                    y1 = round(v1[1] * scale[1]  + translate[1])

                    self.glLineWin(x0, y0, x1, y1)
    def IsInside(self,x,y,poly):
        num = len(poly)
        i = 0
        j = num - 1
        c = False
        for i in range(num):
            if ((poly[i][1] > y) != (poly[j][1] > y)) and \
                    (x < poly[i][0] + (poly[j][0] - poly[i][0]) * (y - poly[i][1]) /
                                    (poly[j][1] - poly[i][1])):
                c = not c
            j = i
        return c
    
    def FillPolygon(self,poly):
        for x in range(self.width):
            for y in range(self.height):
                In = self.IsInside(x,y,poly)
                if In:
                    self.point(x,y)


poly = [(165, 380),(185, 360),(180, 330),(207, 345),(233, 330),(230, 360),(250, 380),(220, 385),(205, 410),(193, 383)]
poly4 = [(413, 177),(448, 159), (502, 88), (553, 53),(535, 36), (676, 37), (660, 52),
(750, 145), (761, 179), (672, 192), (659, 214), (615, 214), (632, 230), (580, 230),
(597, 215), (552, 214), (517, 144), (466, 180)]
poly5 = [(682, 175), (708, 120), (735, 148), (739, 170)]
poly2 = [(321, 335), (288, 286), (339, 251), (374, 302)]
poly3 = [(377, 249), (411, 197), (436, 249)]

r = Bitmap(1280,720)
r.glColor(0.5,0.2,0.5)
r.glViewPort(20,20,640,480)
#r.loadModel('monkey.obj', (400,200 ), (10,30) )
r.FillPolygon(poly4)
r.glColor(0.9,0.2,0.0)
r.FillPolygon(poly)
r.glColor(0.2,0.9,0.0)
r.FillPolygon(poly2)
r.glColor(0.0,0.9,0.8)
r.FillPolygon(poly3)
r.glColor(0.0,0.0,0.0)
r.FillPolygon(poly5)
r.glFinish()