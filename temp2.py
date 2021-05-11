import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib import cm
from numba import jit

def mandelbrot_image(xmin,xmax,ymin,ymax,c=2,width=3,height=3,maxiter=80,cmap='hot',imgname='None'):
    dpi = 72
    img_width = dpi * width
    img_height = dpi * height
    x,y,z = mandelbrot_set(xmin,xmax,ymin,ymax,c,img_width,img_height,maxiter)
    norm = colors.PowerNorm(0.3)
    
    # fig, ax = plt.subplots(figsize=(width, height),dpi=72)
    # ticks = np.arange(0,img_width,3*dpi)
    # x_ticks = xmin + (xmax-xmin)*ticks/img_width
    # plt.xticks(ticks, x_ticks)
    # y_ticks = ymin + (ymax-ymin)*ticks/img_width
    # plt.yticks(ticks, y_ticks)
    # ax.imshow(z.T,cmap=cmap,origin='lower',norm=norm)

    cmap = plt.cm.jet
    cmap = cm.cmap_d['flag_r']
    img = cmap(norm(z.T))
    plt.imsave('{}.png'.format(imgname), img)

@jit
def mandelbrot(creal,cimag,c,maxiter):
    real = creal
    imag = cimag
    for n in range(maxiter):
        real2 = real*real
        imag2 = imag*imag
        if real2 + imag2 > c**2:
            return n
        imag = 2* real*imag + cimag
        real = real2 - imag2 + creal       
    return 0


@jit
def mandelbrot_set(xmin,xmax,ymin,ymax,c,width,height,maxiter):
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    n3 = np.empty((width,height))
    for i in range(width):
        for j in range(height):
            n3[i,j] = mandelbrot(r1[i],r2[j],c,maxiter)
    return (r1,r2,n3)


xmin, xmax, ymin, ymax = -2.0, 0.5, -1.25, 1.25
# xmin, xmax, ymin, ymax = -0.74875, -0.74870, 0.06505, 0.06510
width, height = 20, 20
maxiter = 2048

sizeX = abs(xmax - xmin)
sizeY = abs(ymax - ymin)

zoom_level = 1
factor = 1.2

c = 0.279

centerX, centerY = 0, 0

for zoom in range(zoom_level):
  sizeX = factor**(-zoom) * sizeX
  sizeY = factor**(-zoom) * sizeY
  
  if zoom != 0:
    centerX = (xmax + xmin) / 2
    centerY = (ymax + ymin) / 2
  
  xmin = centerX - (sizeX / 2)
  xmax = centerX + (sizeX / 2)

  ymin = centerY - (sizeY / 2)
  ymax = centerY + (sizeY / 2)
  
  print(zoom)
  
  mandelbrot_image(xmin,xmax,ymin,ymax,c=c,width=width,height=height,maxiter=maxiter,cmap='hot',imgname=zoom)