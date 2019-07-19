import os
from flask import Flask, request, redirect, url_for, Blueprint
from flask import send_from_directory, jsonify
from werkzeug.utils import secure_filename
from ..shared.Authentication import Auth
import cv2
import numpy as np
from imutils import paths
import imutils
import pytesseract
from PIL import Image

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

img_proc_api = Blueprint('img_proc', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@img_proc_api.route('/', methods=['POST'])
@Auth.auth_required
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return '<h1>No file part</h1>'
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return '<h1>No selected file...</h1>'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(os.getenv('UPLOAD_FOLDER'), filename))
            return redirect(url_for('img_proc.uploaded_file', filename=filename))
    return '<h1>No file uploaded yet...</h1>'
  
@img_proc_api.route('/uploads/<filename>')
@Auth.auth_required
def uploaded_file(filename):
    # initialize a rectangular and square structuring kernel
    rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
    sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21,21))

    # read in image from folder, resize it and convert to grayscale
    image = cv2.imread(filename)
    image = imutils.resize(image, height=600)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # smooth the image using a 3x3 Gaussian, then apply the blackhat
    # morphological operator to find dark regions on a light background
    gray = cv2.GaussianBlur(gray, (3,3), 0)
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKernel)

    # compute the Scharr gradient of the blackhat image
    # and scale the result into the range [0, 255]
    gradX = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    gradX = np.absolute(gradX)
    (minVal, maxVal) = (np.min(gradX), np.max(gradX))
    gradX = (255 * ((gradX - minVal) / (maxVal - minVal))).astype("uint8")

    # apply a closing operation using the rectangular
    # kernel to close gaps in between letters
    # then apply Otsu's thresholding method
    gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKernel)
    thresh = cv2.threshold(gradX, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # perform another closing operation, this time using
    # the square kernel to close gaps between lines of 
    # the MRZ, then perform a series of erosions to
    # break apart connected components
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)
    thresh = cv2.erode(thresh, None, iterations=4)

    # during thresholding, it's possible that border
    # pixels were included in the thresholding, so lets
    # set 5% of the left and right borders to zero
    p = int(image.shape[1] * 0.05)
    thresh[:, 0:p] = 0
    thresh[:, image.shape[1] - p:] = 0

    # find contours in the threshold image and sort them
    # by their size
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    # cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

    # loop over the contours
    for c in cnts:
        # compute the bounding box of the contour and use
        # the contour to compute the aspect ratio and
        # coverage ratio of the bounding box width to the
        # width of the image
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)

        
        # check to see if the aspect ratio is within acceptable criteria
        if ar > 5:
            # pad the bounding box since we applied erosions
            # and now need the region to re-grow it
            pX = int((x + w) * 0.03)
            pY = int((y + h) * 0.03)
            (x, y) = (x - pX, y - pY)
            (w, h) = (w + (pX * 2), h + (pY * 2))

            # extract the ROI from the image and draw a 
            # bounding box surrounding the MRZ
            roi = image[y:y + h, x:x + w].copy()
            cv2.rectangle(image, (x,y), (x+w, y+h), (0,255,0), 2)
            break
    #cv2.imwrite('images/output.jpg', roi)
    mrz = pytesseract.image_to_string(roi, lang='ocrb') 
    jsonResult = {'state': False, 'detectedMrz': 'None detected yet!'}
    if(mrz == ''):
        jsonResult['detectedMrz'] = ''
    else:
        jsonResult['state'] = True
        jsonResult['detectedMrz'] = mrz
    
    #return send_from_directory(UPLOAD_FOLDER, 'output.jpg')
    return jsonify({'result': jsonResult})
