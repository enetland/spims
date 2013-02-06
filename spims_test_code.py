import Image, numpy, scipy
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-s', dest="subimg", help='Pattern Image')
parser.add_option('-p', dest="subimg", help='Other Image')
(options, args) = parser.parse_args()

def subimg(img1,img2):
    img1 = numpy.asarray(img1)
    img2 = numpy.asarray(img2) 

    img1y = img1.shape[0]
    img1x = img1.shape[1]

    img2y = img2.shape[0]
    img2x = img2.shape[1]

    stopy = img2y-img1y+1
    stopx = img2x-img1x+1

    for x1 in range(0,stopx):
        for y1 in range(0,stopy):
            x2 = x1+img1x
            y2 = y1+img1y

            pic = img2[y1:y2,x1:x2]
            test = pic == img1

            if test.all():
                return x1, y1

    return False

img1 = Image.open('pattern.png')
img2 = Image.open('source.png')
#img1 = Image.open('tree.jpg')
#img2 = Image.open('tree.png')
#img2 = Image.open('aa0010.png')
print subimg(img1, img2)

