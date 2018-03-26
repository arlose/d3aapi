import numpy as np
import cv2
import sys
from time import time
import json
# from numba import jit

# constant
NUM_SECTOR = 9
FLT_EPSILON = 1e-07

def func1(dx, dy, boundary_x, boundary_y, height, width, numChannels):
    r = np.zeros((height, width), np.float32)
    alfa = np.zeros((height, width, 2), np.int)

    for j in xrange(1, height-1):
        for i in xrange(1, width-1):
            c = 0
            x = dx[j, i, c]
            y = dy[j, i, c]
            r[j, i] = np.sqrt(x*x + y*y)

            for ch in xrange(1, numChannels):
                tx = dx[j, i, ch]
                ty = dy[j, i, ch]
                magnitude = np.sqrt(tx*tx + ty*ty)
                if(magnitude > r[j, i]):
                    r[j, i] = magnitude
                    c = ch
                    x = tx
                    y = ty

            mmax = boundary_x[0]*x + boundary_y[0]*y
            maxi = 0

            for kk in xrange(0, NUM_SECTOR):
                dotProd = boundary_x[kk]*x + boundary_y[kk]*y
                if(dotProd > mmax):
                    mmax = dotProd
                    maxi = kk
                elif(-dotProd > mmax):
                    mmax = -dotProd
                    maxi = kk + NUM_SECTOR

            alfa[j, i, 0] = maxi % NUM_SECTOR
            alfa[j, i, 1] = maxi
    return r, alfa

def func2(dx, dy, boundary_x, boundary_y, r, alfa, nearest, w, k, height, width, sizeX, sizeY, p, stringSize):
    mapp = np.zeros((sizeX*sizeY*p), np.float32)
    for i in xrange(sizeY):
        for j in xrange(sizeX):
            for ii in xrange(k):
                for jj in xrange(k):
                    if((i * k + ii > 0) and (i * k + ii < height - 1) and (j * k + jj > 0) and (j * k + jj < width  - 1)):
                        mapp[i*stringSize + j*p + alfa[k*i+ii,j*k+jj,0]] +=  r[k*i+ii,j*k+jj] * w[ii,0] * w[jj,0]
                        mapp[i*stringSize + j*p + alfa[k*i+ii,j*k+jj,1] + NUM_SECTOR] +=  r[k*i+ii,j*k+jj] * w[ii,0] * w[jj,0]
                        if((i + nearest[ii] >= 0) and (i + nearest[ii] <= sizeY - 1)):
                            mapp[(i+nearest[ii])*stringSize + j*p + alfa[k*i+ii,j*k+jj,0]] += r[k*i+ii,j*k+jj] * w[ii,1] * w[jj,0]
                            mapp[(i+nearest[ii])*stringSize + j*p + alfa[k*i+ii,j*k+jj,1] + NUM_SECTOR] += r[k*i+ii,j*k+jj] * w[ii,1] * w[jj,0]
                        if((j + nearest[jj] >= 0) and (j + nearest[jj] <= sizeX - 1)):
                            mapp[i*stringSize + (j+nearest[jj])*p + alfa[k*i+ii,j*k+jj,0]] += r[k*i+ii,j*k+jj] * w[ii,0] * w[jj,1]
                            mapp[i*stringSize + (j+nearest[jj])*p + alfa[k*i+ii,j*k+jj,1] + NUM_SECTOR] += r[k*i+ii,j*k+jj] * w[ii,0] * w[jj,1]
                        if((i + nearest[ii] >= 0) and (i + nearest[ii] <= sizeY - 1) and (j + nearest[jj] >= 0) and (j + nearest[jj] <= sizeX - 1)):
                            mapp[(i+nearest[ii])*stringSize + (j+nearest[jj])*p + alfa[k*i+ii,j*k+jj,0]] += r[k*i+ii,j*k+jj] * w[ii,1] * w[jj,1]
                            mapp[(i+nearest[ii])*stringSize + (j+nearest[jj])*p + alfa[k*i+ii,j*k+jj,1] + NUM_SECTOR] += r[k*i+ii,j*k+jj] * w[ii,1] * w[jj,1]
    return mapp

def func3(partOfNorm, mappmap, sizeX, sizeY, p, xp, pp):
	newData = np.zeros((sizeY*sizeX*pp), np.float32)
	for i in xrange(1, sizeY+1):
		for j in xrange(1, sizeX+1):
			pos1 = i * (sizeX+2) * xp + j * xp
			pos2 = (i-1) * sizeX * pp + (j-1) * pp

			valOfNorm = np.sqrt(partOfNorm[(i    )*(sizeX + 2) + (j    )] +
                				partOfNorm[(i    )*(sizeX + 2) + (j + 1)] +
                				partOfNorm[(i + 1)*(sizeX + 2) + (j    )] +
                				partOfNorm[(i + 1)*(sizeX + 2) + (j + 1)]) + FLT_EPSILON
			newData[pos2:pos2+p] = mappmap[pos1:pos1+p] / valOfNorm
			newData[pos2+4*p:pos2+6*p] = mappmap[pos1+p:pos1+3*p] / valOfNorm

			valOfNorm = np.sqrt(partOfNorm[(i    )*(sizeX + 2) + (j    )] +
				                partOfNorm[(i    )*(sizeX + 2) + (j + 1)] +
				                partOfNorm[(i - 1)*(sizeX + 2) + (j    )] +
				                partOfNorm[(i - 1)*(sizeX + 2) + (j + 1)]) + FLT_EPSILON
			newData[pos2+p:pos2+2*p] = mappmap[pos1:pos1+p] / valOfNorm
			newData[pos2+6*p:pos2+8*p] = mappmap[pos1+p:pos1+3*p] / valOfNorm

			valOfNorm = np.sqrt(partOfNorm[(i    )*(sizeX + 2) + (j    )] +
				                partOfNorm[(i    )*(sizeX + 2) + (j - 1)] +
				                partOfNorm[(i + 1)*(sizeX + 2) + (j    )] +
				                partOfNorm[(i + 1)*(sizeX + 2) + (j - 1)]) + FLT_EPSILON
			newData[pos2+2*p:pos2+3*p] = mappmap[pos1:pos1+p] / valOfNorm
			newData[pos2+8*p:pos2+10*p] = mappmap[pos1+p:pos1+3*p] / valOfNorm

			valOfNorm = np.sqrt(partOfNorm[(i    )*(sizeX + 2) + (j    )] +
				                partOfNorm[(i    )*(sizeX + 2) + (j - 1)] +
				                partOfNorm[(i - 1)*(sizeX + 2) + (j    )] +
				                partOfNorm[(i - 1)*(sizeX + 2) + (j - 1)]) + FLT_EPSILON
			newData[pos2+3*p:pos2+4*p] = mappmap[pos1:pos1+p] / valOfNorm
			newData[pos2+10*p:pos2+12*p] = mappmap[pos1+p:pos1+3*p] / valOfNorm
	return newData

def func4(mappmap, p, sizeX, sizeY, pp, yp, xp, nx, ny):
	newData = np.zeros((sizeX*sizeY*pp), np.float32)
	for i in xrange(sizeY):
		for j in xrange(sizeX):
			pos1 = (i*sizeX + j) * p
			pos2 = (i*sizeX + j) * pp

			for jj in xrange(2 * xp):  # 2*9
				newData[pos2 + jj] = np.sum(mappmap[pos1 + yp*xp + jj : pos1 + 3*yp*xp + jj : 2*xp]) * ny
			for jj in xrange(xp):  # 9
				newData[pos2 + 2*xp + jj] = np.sum(mappmap[pos1 + jj : pos1 + jj + yp*xp : xp]) * ny
			for ii in xrange(yp):  # 4
				newData[pos2 + 3*xp + ii] = np.sum(mappmap[pos1 + yp*xp + ii*xp*2 : pos1 + yp*xp + ii*xp*2 + 2*xp]) * nx
	return newData



def getFeatureMaps(image, k, mapp):
	kernel = np.array([[-1.,  0., 1.]], np.float32)

	height = image.shape[0]
	width = image.shape[1]
	assert(image.ndim==3 and image.shape[2])
	numChannels = 3 #(1 if image.ndim==2 else image.shape[2])

	sizeX = width / k
	sizeY = height / k
	px = 3 * NUM_SECTOR
	p = px
	stringSize = sizeX * p

	mapp['sizeX'] = sizeX
	mapp['sizeY'] = sizeY
	mapp['numFeatures'] = p
	mapp['map'] = np.zeros((mapp['sizeX']*mapp['sizeY']*mapp['numFeatures']), np.float32)

	dx = cv2.filter2D(np.float32(image), -1, kernel)   # np.float32(...) is necessary
	dy = cv2.filter2D(np.float32(image), -1, kernel.T)

	arg_vector = np.arange(NUM_SECTOR+1).astype(np.float32) * np.pi / NUM_SECTOR
	boundary_x = np.cos(arg_vector) 
	boundary_y = np.sin(arg_vector)

	'''
	### original implementation
	r, alfa = func1(dx, dy, boundary_x, boundary_y, height, width, numChannels) #func1 without @jit  ### 

	### 40x speedup
	magnitude = np.sqrt(dx**2 + dy**2)
	r = np.max(magnitude, axis=2)
	c = np.argmax(magnitude, axis=2)
	idx = (np.arange(c.shape[0])[:,np.newaxis], np.arange(c.shape[1]), c)
	x, y = dx[idx], dy[idx]

	dotProd = x[:,:,np.newaxis] * boundary_x[np.newaxis,np.newaxis,:] + y[:,:,np.newaxis] * boundary_y[np.newaxis,np.newaxis,:]
	dotProd = np.concatenate((dotProd, -dotProd), axis=2)
	maxi = np.argmax(dotProd, axis=2)
	alfa = np.dstack((maxi % NUM_SECTOR, maxi)) ###
	'''
	### 200x speedup
	r, alfa = func1(dx, dy, boundary_x, boundary_y, height, width, numChannels) #with @jit
	### ~0.001s

	nearest = np.ones((k), np.int)
	nearest[0:k/2] = -1

	w = np.zeros((k, 2), np.float32)
	a_x = np.concatenate((k/2 - np.arange(k/2) - 0.5, np.arange(k/2,k) - k/2 + 0.5)).astype(np.float32)
	b_x = np.concatenate((k/2 + np.arange(k/2) + 0.5, -np.arange(k/2,k) + k/2 - 0.5 + k)).astype(np.float32)
	w[:, 0] = 1.0 / a_x * ((a_x*b_x) / (a_x+b_x))
	w[:, 1] = 1.0 / b_x * ((a_x*b_x) / (a_x+b_x))

	'''
	### original implementation
	mapp['map'] = func2(dx, dy, boundary_x, boundary_y, r, alfa, nearest, w, k, height, width, sizeX, sizeY, p, stringSize) #func2 without @jit  ###
	'''
	### 500x speedup
	mapp['map'] = func2(dx, dy, boundary_x, boundary_y, r, alfa, nearest, w, k, height, width, sizeX, sizeY, p, stringSize) #with @jit
	### ~0.001s

	return mapp


def normalizeAndTruncate(mapp, alfa):
	sizeX = mapp['sizeX']
	sizeY = mapp['sizeY']

	p = NUM_SECTOR
	xp = NUM_SECTOR * 3
	pp = NUM_SECTOR * 12

	'''
	### original implementation
	partOfNorm = np.zeros((sizeY*sizeX), np.float32)

	for i in xrange(sizeX*sizeY):
		pos = i * mapp['numFeatures']
		partOfNorm[i] = np.sum(mapp['map'][pos:pos+p]**2) ###
	'''
	### 50x speedup
	idx = np.arange(0, sizeX*sizeY*mapp['numFeatures'], mapp['numFeatures']).reshape((sizeX*sizeY, 1)) + np.arange(p)
	partOfNorm = np.sum(mapp['map'][idx] ** 2, axis=1) ### ~0.0002s

	sizeX, sizeY = sizeX-2, sizeY-2
	

	'''
	### original implementation
	newData = func3(partOfNorm, mapp['map'], sizeX, sizeY, p, xp, pp) #func3 without @jit  ###
	
	### 30x speedup
	newData = np.zeros((sizeY*sizeX*pp), np.float32)
	idx = (np.arange(1,sizeY+1)[:,np.newaxis] * (sizeX+2) + np.arange(1,sizeX+1)).reshape((sizeY*sizeX, 1))   # much faster than it's List Comprehension counterpart (see next line)
	#idx = np.array([[i*(sizeX+2) + j] for i in xrange(1,sizeY+1) for j in xrange(1,sizeX+1)])
	pos1 = idx * xp
	pos2 = np.arange(sizeY*sizeX)[:,np.newaxis] * pp
	
	valOfNorm1 = np.sqrt(partOfNorm[idx] + partOfNorm[idx+1] + partOfNorm[idx+sizeX+2] + partOfNorm[idx+sizeX+2+1]) + FLT_EPSILON
	valOfNorm2 = np.sqrt(partOfNorm[idx] + partOfNorm[idx+1] + partOfNorm[idx-sizeX-2] + partOfNorm[idx+sizeX-2+1]) + FLT_EPSILON
	valOfNorm3 = np.sqrt(partOfNorm[idx] + partOfNorm[idx-1] + partOfNorm[idx+sizeX+2] + partOfNorm[idx+sizeX+2-1]) + FLT_EPSILON
	valOfNorm4 = np.sqrt(partOfNorm[idx] + partOfNorm[idx-1] + partOfNorm[idx-sizeX-2] + partOfNorm[idx+sizeX-2-1]) + FLT_EPSILON

	map1 = mapp['map'][pos1 + np.arange(p)]
	map2 = mapp['map'][pos1 + np.arange(p,3*p)]

	newData[pos2 + np.arange(p)] = map1 / valOfNorm1
	newData[pos2 + np.arange(4*p,6*p)] = map2 / valOfNorm1
	newData[pos2 + np.arange(p,2*p)] = map1 / valOfNorm2
	newData[pos2 + np.arange(6*p,8*p)] = map2 / valOfNorm2
	newData[pos2 + np.arange(2*p,3*p)] = map1 / valOfNorm3
	newData[pos2 + np.arange(8*p,10*p)] = map2 / valOfNorm3
	newData[pos2 + np.arange(3*p,4*p)] = map1 / valOfNorm4
	newData[pos2 + np.arange(10*p,12*p)] = map2 / valOfNorm4 ###
	'''
	### 30x speedup
	newData = func3(partOfNorm, mapp['map'], sizeX, sizeY, p, xp, pp) #with @jit
	###

	# truncation
	newData[newData > alfa] = alfa

	mapp['numFeatures'] = pp
	mapp['sizeX'] = sizeX
	mapp['sizeY'] = sizeY
	mapp['map'] = newData

	return mapp


def PCAFeatureMaps(mapp):
	sizeX = mapp['sizeX']
	sizeY = mapp['sizeY']

	p = mapp['numFeatures']
	pp = NUM_SECTOR * 3 + 4
	yp = 4
	xp = NUM_SECTOR

	nx = 1.0 / np.sqrt(xp*2)
	ny = 1.0 / np.sqrt(yp)

	'''
	### original implementation
	newData = func4(mapp['map'], p, sizeX, sizeY, pp, yp, xp, nx, ny) #func without @jit  ###

	### 7.5x speedup
	newData = np.zeros((sizeX*sizeY*pp), np.float32)
	idx1 = np.arange(2*xp).reshape((2*xp, 1)) + np.arange(xp*yp, 3*xp*yp, 2*xp)
	idx2 = np.arange(xp).reshape((xp, 1)) + np.arange(0, xp*yp, xp)
	idx3 = np.arange(0, 2*xp*yp, 2*xp).reshape((yp, 1)) + np.arange(xp*yp, xp*yp+2*xp)

	for i in xrange(sizeY):
		for j in xrange(sizeX):
			pos1 = (i*sizeX + j) * p
			pos2 = (i*sizeX + j) * pp
						
			newData[pos2 : pos2+2*xp] = np.sum(mapp['map'][pos1 + idx1], axis=1) * ny
			newData[pos2+2*xp : pos2+3*xp] = np.sum(mapp['map'][pos1 + idx2], axis=1) * ny
			newData[pos2+3*xp : pos2+3*xp+yp] = np.sum(mapp['map'][pos1 + idx3], axis=1) * nx ###

	### 120x speedup 
	newData = np.zeros((sizeX*sizeY*pp), np.float32)
	idx01 = (np.arange(0,sizeX*sizeY*pp,pp)[:,np.newaxis] + np.arange(2*xp)).reshape((sizeX*sizeY*2*xp))
	idx02 = (np.arange(0,sizeX*sizeY*pp,pp)[:,np.newaxis] + np.arange(2*xp,3*xp)).reshape((sizeX*sizeY*xp))
	idx03 = (np.arange(0,sizeX*sizeY*pp,pp)[:,np.newaxis] + np.arange(3*xp,3*xp+yp)).reshape((sizeX*sizeY*yp))

	idx11 = (np.arange(0,sizeX*sizeY*p,p)[:,np.newaxis] + np.arange(2*xp)).reshape((sizeX*sizeY*2*xp, 1)) + np.arange(xp*yp, 3*xp*yp, 2*xp)
	idx12 = (np.arange(0,sizeX*sizeY*p,p)[:,np.newaxis] + np.arange(xp)).reshape((sizeX*sizeY*xp, 1)) + np.arange(0, xp*yp, xp)
	idx13 = (np.arange(0,sizeX*sizeY*p,p)[:,np.newaxis] + np.arange(0, 2*xp*yp, 2*xp)).reshape((sizeX*sizeY*yp, 1)) + np.arange(xp*yp, xp*yp+2*xp)

	newData[idx01] = np.sum(mapp['map'][idx11], axis=1) * ny
	newData[idx02] = np.sum(mapp['map'][idx12], axis=1) * ny
	newData[idx03] = np.sum(mapp['map'][idx13], axis=1) * nx ###
	'''
	### 190x speedup
	newData = func4(mapp['map'], p, sizeX, sizeY, pp, yp, xp, nx, ny) #with @jit
	###

	mapp['numFeatures'] = pp
	mapp['map'] = newData

	return mapp

# ffttools
def fftd(img, backwards=False):	
	# shape of img can be (m,n), (m,n,1) or (m,n,2)	
	# in my test, fft provided by numpy and scipy are slower than cv2.dft
	return cv2.dft(np.float32(img), flags = ((cv2.DFT_INVERSE | cv2.DFT_SCALE) if backwards else cv2.DFT_COMPLEX_OUTPUT))   # 'flags =' is necessary!
	
def real(img):
	return img[:,:,0]
	
def imag(img):
	return img[:,:,1]
		
def complexMultiplication(a, b):
	res = np.zeros(a.shape, a.dtype)
	
	res[:,:,0] = a[:,:,0]*b[:,:,0] - a[:,:,1]*b[:,:,1]
	res[:,:,1] = a[:,:,0]*b[:,:,1] + a[:,:,1]*b[:,:,0]
	return res

def complexDivision(a, b):
	res = np.zeros(a.shape, a.dtype)
	divisor = 1. / (b[:,:,0]**2 + b[:,:,1]**2)
	
	res[:,:,0] = (a[:,:,0]*b[:,:,0] + a[:,:,1]*b[:,:,1]) * divisor
	res[:,:,1] = (a[:,:,1]*b[:,:,0] + a[:,:,0]*b[:,:,1]) * divisor
	return res

def rearrange(img):
	#return np.fft.fftshift(img, axes=(0,1))
	assert(img.ndim==2)
	img_ = np.zeros(img.shape, img.dtype)
	xh, yh = img.shape[1]/2, img.shape[0]/2
	img_[0:yh,0:xh], img_[yh:img.shape[0],xh:img.shape[1]] = img[yh:img.shape[0],xh:img.shape[1]], img[0:yh,0:xh]
	img_[0:yh,xh:img.shape[1]], img_[yh:img.shape[0],0:xh] = img[yh:img.shape[0],0:xh], img[0:yh,xh:img.shape[1]]
	return img_


# recttools
def x2(rect):
	return rect[0] + rect[2]

def y2(rect):
	return rect[1] + rect[3]

def limit(rect, limit):
	if(rect[0]+rect[2] > limit[0]+limit[2]):
		rect[2] = limit[0]+limit[2]-rect[0]
	if(rect[1]+rect[3] > limit[1]+limit[3]):
		rect[3] = limit[1]+limit[3]-rect[1]
	if(rect[0] < limit[0]):
		rect[2] -= (limit[0]-rect[0])
		rect[0] = limit[0]
	if(rect[1] < limit[1]):
		rect[3] -= (limit[1]-rect[1])
		rect[1] = limit[1]
	if(rect[2] < 0):
		rect[2] = 0
	if(rect[3] < 0):
		rect[3] = 0
	return rect

def getBorder(original, limited):
	res = [0,0,0,0]
	res[0] = limited[0] - original[0]
	res[1] = limited[1] - original[1]
	res[2] = x2(original) - x2(limited)
	res[3] = y2(original) - y2(limited)
	assert(np.all(np.array(res) >= 0))
	return res

def subwindow(img, window, borderType=cv2.BORDER_CONSTANT):
	cutWindow = [x for x in window]
	limit(cutWindow, [0,0,img.shape[1],img.shape[0]])   # modify cutWindow
	assert(cutWindow[2]>0 and cutWindow[3]>0)
	border = getBorder(window, cutWindow)
	res = img[cutWindow[1]:cutWindow[1]+cutWindow[3], cutWindow[0]:cutWindow[0]+cutWindow[2]]

	if(border != [0,0,0,0]):
		res = cv2.copyMakeBorder(res, border[1], border[3], border[0], border[2], borderType)
	return res



# KCF tracker
class KCFTracker:
	def __init__(self, hog=False, fixed_window=True, multiscale=False):
		self.lambdar = 0.0001   # regularization
		self.padding = 2.5   # extra area surrounding the target
		self.output_sigma_factor = 0.125   # bandwidth of gaussian target

		if(hog):  # HOG feature
			# VOT
			self.interp_factor = 0.012   # linear interpolation factor for adaptation
			self.sigma = 0.6  # gaussian kernel bandwidth
			# TPAMI   #interp_factor = 0.02   #sigma = 0.5
			self.cell_size = 4   # HOG cell size
			self._hogfeatures = True
		else:  # raw gray-scale image # aka CSK tracker
			self.interp_factor = 0.075
			self.sigma = 0.2
			self.cell_size = 1
			self._hogfeatures = False

		if(multiscale):
			self.template_size = 96   # template size
			self.scale_step = 1.05   # scale step for multi-scale estimation
			self.scale_weight = 0.96   # to downweight detection scores of other scales for added stability
		elif(fixed_window):
			self.template_size = 96
			self.scale_step = 1
		else:
			self.template_size = 1
			self.scale_step = 1

		self._tmpl_sz = [0,0]  # cv::Size, [width,height]  #[int,int]
		self._roi = [0.,0.,0.,0.]  # cv::Rect2f, [x,y,width,height]  #[float,float,float,float]
		self.size_patch = [0,0,0]  #[int,int,int]
		self._scale = 1.   # float
		self._alphaf = None  # numpy.ndarray    (size_patch[0], size_patch[1], 2)
		self._prob = None  # numpy.ndarray    (size_patch[0], size_patch[1], 2)
		self._tmpl = None  # numpy.ndarray    raw: (size_patch[0], size_patch[1])   hog: (size_patch[2], size_patch[0]*size_patch[1])
		self.hann = None  # numpy.ndarray    raw: (size_patch[0], size_patch[1])   hog: (size_patch[2], size_patch[0]*size_patch[1])

	def subPixelPeak(self, left, center, right):
		divisor = 2*center - right - left   #float
		return (0 if abs(divisor)<1e-3 else 0.5*(right-left)/divisor)

	def createHanningMats(self):
		hann2t, hann1t = np.ogrid[0:self.size_patch[0], 0:self.size_patch[1]]

		hann1t = 0.5 * (1 - np.cos(2*np.pi*hann1t/(self.size_patch[1]-1)))
		hann2t = 0.5 * (1 - np.cos(2*np.pi*hann2t/(self.size_patch[0]-1)))
		hann2d = hann2t * hann1t

		if(self._hogfeatures):
			hann1d = hann2d.reshape(self.size_patch[0]*self.size_patch[1])
			self.hann = np.zeros((self.size_patch[2], 1), np.float32) + hann1d
		else:
			self.hann = hann2d
		self.hann = self.hann.astype(np.float32)

	def createGaussianPeak(self, sizey, sizex):
		syh, sxh = sizey/2, sizex/2
		output_sigma = np.sqrt(sizex*sizey) / self.padding * self.output_sigma_factor
		mult = -0.5 / (output_sigma*output_sigma)
		y, x = np.ogrid[0:sizey, 0:sizex]
		y, x = (y-syh)**2, (x-sxh)**2
		res = np.exp(mult * (y+x))
		return fftd(res)

	def gaussianCorrelation(self, x1, x2):
		if(self._hogfeatures):
			c = np.zeros((self.size_patch[0], self.size_patch[1]), np.float32)
			for i in xrange(self.size_patch[2]):
				x1aux = x1[i, :].reshape((self.size_patch[0], self.size_patch[1]))
				x2aux = x2[i, :].reshape((self.size_patch[0], self.size_patch[1]))
				caux = cv2.mulSpectrums(fftd(x1aux), fftd(x2aux), 0, conjB = True)
				caux = real(fftd(caux, True))
				#caux = rearrange(caux)
				c += caux
			c = rearrange(c)
		else:
			c = cv2.mulSpectrums(fftd(x1), fftd(x2), 0, conjB = True)   # 'conjB=' is necessary!
			c = fftd(c, True)
			c = real(c)
			c = rearrange(c)

		if(x1.ndim==3 and x2.ndim==3):
			d = (np.sum(x1[:,:,0]*x1[:,:,0]) + np.sum(x2[:,:,0]*x2[:,:,0]) - 2.0*c) / (self.size_patch[0]*self.size_patch[1]*self.size_patch[2])
		elif(x1.ndim==2 and x2.ndim==2):
			d = (np.sum(x1*x1) + np.sum(x2*x2) - 2.0*c) / (self.size_patch[0]*self.size_patch[1]*self.size_patch[2])

		d = d * (d>=0)
		d = np.exp(-d / (self.sigma*self.sigma))

		return d

	def getFeatures(self, image, inithann, scale_adjust=1.0):
		extracted_roi = [0,0,0,0]   #[int,int,int,int]
		cx = self._roi[0] + self._roi[2]/2  #float
		cy = self._roi[1] + self._roi[3]/2  #float

		if(inithann):
			padded_w = self._roi[2] * self.padding
			padded_h = self._roi[3] * self.padding

			if(self.template_size > 1):
				if(padded_w >= padded_h):
					self._scale = padded_w / float(self.template_size)
				else:
					self._scale = padded_h / float(self.template_size)
				self._tmpl_sz[0] = int(padded_w / self._scale)
				self._tmpl_sz[1] = int(padded_h / self._scale)
			else:
				self._tmpl_sz[0] = int(padded_w)
				self._tmpl_sz[1] = int(padded_h)
				self._scale = 1.

			if(self._hogfeatures):
				self._tmpl_sz[0] = int(self._tmpl_sz[0]) / (2*self.cell_size) * 2*self.cell_size + 2*self.cell_size
				self._tmpl_sz[1] = int(self._tmpl_sz[1]) / (2*self.cell_size) * 2*self.cell_size + 2*self.cell_size
			else:
				self._tmpl_sz[0] = int(self._tmpl_sz[0]) / 2 * 2
				self._tmpl_sz[1] = int(self._tmpl_sz[1]) / 2 * 2

		extracted_roi[2] = int(scale_adjust * self._scale * self._tmpl_sz[0])
		extracted_roi[3] = int(scale_adjust * self._scale * self._tmpl_sz[1])
		extracted_roi[0] = int(cx - extracted_roi[2]/2)
		extracted_roi[1] = int(cy - extracted_roi[3]/2)

		z = subwindow(image, extracted_roi, cv2.BORDER_REPLICATE)
		if(z.shape[1]!=self._tmpl_sz[0] or z.shape[0]!=self._tmpl_sz[1]):
			z = cv2.resize(z, tuple(self._tmpl_sz))

		if(self._hogfeatures):
			mapp = {'sizeX':0, 'sizeY':0, 'numFeatures':0, 'map':0}
			mapp = getFeatureMaps(z, self.cell_size, mapp)
			mapp = normalizeAndTruncate(mapp, 0.2)
			mapp = PCAFeatureMaps(mapp)
			self.size_patch = map(int, [mapp['sizeY'], mapp['sizeX'], mapp['numFeatures']])
			FeaturesMap = mapp['map'].reshape((self.size_patch[0]*self.size_patch[1], self.size_patch[2])).T   # (size_patch[2], size_patch[0]*size_patch[1])
		else:
			if(z.ndim==3 and z.shape[2]==3):
				FeaturesMap = cv2.cvtColor(z, cv2.COLOR_BGR2GRAY)   # z:(size_patch[0], size_patch[1], 3)  FeaturesMap:(size_patch[0], size_patch[1])   #np.int8  #0~255
			elif(z.ndim==2):
				FeaturesMap = z   #(size_patch[0], size_patch[1]) #np.int8  #0~255
			FeaturesMap = FeaturesMap.astype(np.float32) / 255.0 - 0.5
			self.size_patch = [z.shape[0], z.shape[1], 1]

		if(inithann):
			self.createHanningMats()  # createHanningMats need size_patch

		FeaturesMap = self.hann * FeaturesMap
		return FeaturesMap

	def detect(self, z, x):
		k = self.gaussianCorrelation(x, z)
		res = real(fftd(complexMultiplication(self._alphaf, fftd(k)), True))

		_, pv, _, pi = cv2.minMaxLoc(res)   # pv:float  pi:tuple of int
		p = [float(pi[0]), float(pi[1])]   # cv::Point2f, [x,y]  #[float,float]

		if(pi[0]>0 and pi[0]<res.shape[1]-1):
			p[0] += self.subPixelPeak(res[pi[1],pi[0]-1], pv, res[pi[1],pi[0]+1])
		if(pi[1]>0 and pi[1]<res.shape[0]-1):
			p[1] += self.subPixelPeak(res[pi[1]-1,pi[0]], pv, res[pi[1]+1,pi[0]])

		p[0] -= res.shape[1] / 2.
		p[1] -= res.shape[0] / 2.

		return p, pv

	def train(self, x, train_interp_factor):
		k = self.gaussianCorrelation(x, x)
		alphaf = complexDivision(self._prob, fftd(k)+self.lambdar)

		self._tmpl = (1-train_interp_factor)*self._tmpl + train_interp_factor*x
		self._alphaf = (1-train_interp_factor)*self._alphaf + train_interp_factor*alphaf


	def init(self, roi, image):
		self._roi = map(float, roi)
		assert(roi[2]>0 and roi[3]>0)
		self._tmpl = self.getFeatures(image, 1)
		self._prob = self.createGaussianPeak(self.size_patch[0], self.size_patch[1])
		self._alphaf = np.zeros((self.size_patch[0], self.size_patch[1], 2), np.float32)
		self.train(self._tmpl, 1.0)

	def update(self, image):
		if(self._roi[0]+self._roi[2] <= 0):  self._roi[0] = -self._roi[2] + 1
		if(self._roi[1]+self._roi[3] <= 0):  self._roi[1] = -self._roi[2] + 1
		if(self._roi[0] >= image.shape[1]-1):  self._roi[0] = image.shape[1] - 2
		if(self._roi[1] >= image.shape[0]-1):  self._roi[1] = image.shape[0] - 2

		cx = self._roi[0] + self._roi[2]/2.
		cy = self._roi[1] + self._roi[3]/2.

		loc, peak_value = self.detect(self._tmpl, self.getFeatures(image, 0, 1.0))

		if(self.scale_step != 1):
			# Test at a smaller _scale
			new_loc1, new_peak_value1 = self.detect(self._tmpl, self.getFeatures(image, 0, 1.0/self.scale_step))
			# Test at a bigger _scale
			new_loc2, new_peak_value2 = self.detect(self._tmpl, self.getFeatures(image, 0, self.scale_step))

			if(self.scale_weight*new_peak_value1 > peak_value and new_peak_value1>new_peak_value2):
				loc = new_loc1
				peak_value = new_peak_value1
				self._scale /= self.scale_step
				self._roi[2] /= self.scale_step
				self._roi[3] /= self.scale_step
			elif(self.scale_weight*new_peak_value2 > peak_value):
				loc = new_loc2
				peak_value = new_peak_value2
				self._scale *= self.scale_step
				self._roi[2] *= self.scale_step
				self._roi[3] *= self.scale_step
		
		self._roi[0] = cx - self._roi[2]/2.0 + loc[0]*self.cell_size*self._scale
		self._roi[1] = cy - self._roi[3]/2.0 + loc[1]*self.cell_size*self._scale
		
		if(self._roi[0] >= image.shape[1]-1):  self._roi[0] = image.shape[1] - 1
		if(self._roi[1] >= image.shape[0]-1):  self._roi[1] = image.shape[0] - 1
		if(self._roi[0]+self._roi[2] <= 0):  self._roi[0] = -self._roi[2] + 2
		if(self._roi[1]+self._roi[3] <= 0):  self._roi[1] = -self._roi[3] + 2
		assert(self._roi[2]>0 and self._roi[3]>0)

		x = self.getFeatures(image, 0, 1.0)
		self.train(x, self.interp_factor)

		return self._roi


if __name__ == '__main__':
	tracker = KCFTracker(True, False, True)  # hog, fixed_window, multiscale
	img1 = cv2.imread(sys.argv[1])
	h1, w1, _ = img1.shape
	img2 = cv2.imread(sys.argv[2])
	h2, w2, _ = img2.shape
	label1 = sys.argv[1]+'.txt'
	label2 = sys.argv[2]+'.txt'
	labeldata = json.load(open(label1))
	objects = labeldata['objects']
	for obj in objects:
		x0 = int(float(obj['x_start'])*w1)
		y0 = int(float(obj['y_start'])*h1)
		w0 = int(float(obj['x_end'])*w1)-x0
		h0 = int(float(obj['y_end'])*h1)-y0
		tracker.init([x0,y0,w0,h0], img1)
		boundingbox = tracker.update(img2)
		obj['x_start'] = float('%.3f' % (boundingbox[0]/w2))
		obj['y_start'] = float('%.3f' % (boundingbox[1]/h2))
		obj['x_end'] = float('%.3f' % ((boundingbox[0]+boundingbox[2])/w2))
		obj['y_end'] = float('%.3f' % ((boundingbox[1]+boundingbox[3])/h2))
		# print boundingbox
		# cv2.rectangle(img1,(x0,y0), ((x0+w0),(y0+h0)), (0,255,255), 1)
		# cv2.imshow('org', img1)
		# cv2.rectangle(img2,(int(boundingbox[0]),int(boundingbox[1])), (int(boundingbox[0]+boundingbox[2]),int(boundingbox[1]+boundingbox[3])), (0,255,255), 1)
		# cv2.imshow('tracking', img2)
		# c = cv2.waitKey(-1) & 0xFF
		# if c==27 or c==ord('q'):
		# 	break
	with open(label2, "w") as f:
    		f.write(json.dumps(labeldata))
		

