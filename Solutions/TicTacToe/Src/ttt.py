import sys
import os
import cv2
import os
import numpy as np

# Utility functions

def check_input():
    """
    Checks input parameters.

    Prints usage and exits if invalid input.
    """
    if len(sys.argv) != 3:
        # Print usage
        print "Check input parameters! Usage: ttt.py inputImagePath outputTextPath"
        sys.exit()

def line_intersection(line1, line2):
    """
    Given two points for each of two lines, get me an intersection point
    """
    x1 = line1[0][0]
    y1 = line1[0][1]
    x2 = line1[1][0]
    y2 = line1[1][1]
    x3 = line2[0][0]
    y3 = line2[0][1]
    x4 = line2[1][0]
    y4 = line2[1][1]

    x = ((x1*y2 - y1*x2) * (x3 - x4) - (x1 - x2) * (x3*y4 - y3*x4)) / ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))
    y = ((x1*y2 - y1*x2) * (y3 - y4) - (y1 - y2) * (x3*y4 - y3*x4)) / ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))

    return (x, y)

def get_positions(intersections):
    """
    Given 4 points, return me top left, top right, bottom left, bottom right
    """

    vertical = sorted(intersections, key=lambda tup: tup[1])
    horizontal = sorted(intersections, key=lambda tup: tup[0], reverse = True)

    top = vertical[:2]
    bottom = vertical[-2:]
    left = horizontal[-2:]
    right = horizontal[:2]

    topLeft = min(set.intersection(set(top), set(left)))
    topRight = min(set.intersection(set(top), set(right)))
    bottomLeft = min(set.intersection(set(bottom), set(left)))
    bottomRight = min(set.intersection(set(bottom), set(right)))

    return (topLeft, topRight, bottomLeft, bottomRight)

def parse_lines(houghLines):
    """
    Reads hough lines, removes duplicates, extracts intersections
    """
    lines = []
    intersections = []

    for line in houghLines:
        for rho, theta in line:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))

            duplicates = [l for l in lines if abs(abs(l[2]) - abs(rho)) < 25 and (abs(l[3] - theta) < np.pi/6 or abs(l[3] - theta) > 5*np.pi/6)]
            if not duplicates:
                intersectionLines = [l for l in lines if abs(theta - l[3]) > np.pi/6 and abs(theta - l[3]) < 5*np.pi/6]
                for line in intersectionLines:    
                    intersections.append(line_intersection(line, ((x1, y1), (x2, y2))))

                lines.append(((x1, y1), (x2, y2), rho, theta))

    return (lines, intersections)

def recognize_symbol(img):
    # Crop bounding box a bit
    height, width = img.shape[:2]
    img = img[2:height-2, 2:width-2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Check for O
    blur = cv2.medianBlur(gray,5)
    circles = cv2.HoughCircles(blur,cv2.HOUGH_GRADIENT,1,20, param1=50,param2=20,minRadius=0,maxRadius=0)

    if circles is not None:
        return 'O'

    # Check for X
    edges = cv2.Canny(image = gray, threshold1 = 50, threshold2 = 150, apertureSize = 3)
    houghLines = cv2.HoughLines(image = edges, rho = 1, theta = np.pi/180, threshold = 20)   
   
    if houghLines is not None and len(houghLines) >= 0:
        lines, intersections = parse_lines(houghLines)
        #for line in lines:
            #cv2.line(img, line[0], line[1], (255,0,0), 3)
            
        for intersection in intersections:
            #cv2.circle(img, intersection, 3, (0,255,0), 5)
            # Check if intersection is somewhere in the middle of ROI, if it is we have an X:
            x = intersection[0]
            y = intersection[1]
            height, width = img.shape[:2]
            if x > 10 and x < width - 10 and y > 10 and y < height - 10:
                return 'X'

    #cv2.imshow('houghlines3.jpg', img)
    #cv2.waitKey(0)

    # Nothing found, return '-'
    return '-'

def store_to_file(content, output_file):
    """ 
    Stores content into file

    param content: content to be stored to file
    param output_file: path/filename to the output file (folders will be created)
    """

    # Check if we need to create output folders
    if ('\\' in output_file or '/' in output_file) and \
            not os.path.exists(os.path.dirname(output_file)):
    
        try:
            os.makedirs(os.path.dirname(output_file))
        except OSError as exc: # Guard agains race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(output_file, 'w') as f:
        f.write(content)


# Main
check_input()
inputImagePath = sys.argv[1]
outputTextPath = sys.argv[2]

file_list = [x for x in os.listdir(inputImagePath) if x.endswith(".bmp")]

for filename in file_list:
    try:
        filepath = inputImagePath + "\{0}".format(filename)
        img = cv2.imread(filepath)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(image = gray, threshold1 = 50, threshold2 = 150, apertureSize = 3)

        houghLines = cv2.HoughLines(image = edges, rho = 1, theta = np.pi/180, threshold = 90)

        # Get lines and intersections
        lines, intersections = parse_lines(houghLines)

        # Filter 4 main positions (intersections)
        topLeft, topRight, bottomLeft, bottomRight = get_positions(intersections)
    
        # Get ROIs (9 total) extracted from 4 main points (intersections)
        topLeftROI = img[0:topLeft[1], 0:topLeft[0]]
        topMiddleROI = img[0:(topLeft[1] + topRight[1])/2, topLeft[0]:topRight[0]]
        topRightROI = img[0:topRight[1], topRight[0]:255]

        centerLeftROI = img[topLeft[1]:bottomLeft[1], 0:(topLeft[0] + bottomLeft[0])/2]
        centerMiddleROI = img[(topLeft[1] + topRight[1])/2 : (bottomLeft[1] + bottomRight[1])/2, (topLeft[0] + bottomLeft[0])/2 : (topRight[0] + bottomRight[0])/2]
        centerRightROI = img[topRight[1]:bottomRight[1], (topRight[0] + bottomRight[0])/2 : 255]

        bottomLeftROI = img[bottomLeft[1]:255, 0:bottomLeft[0]]
        bottomMiddleROI = img[(bottomLeft[1] + bottomRight[1])/2 : 255, bottomLeft[0]:bottomRight[0]]
        bottomRightROI = img[bottomRight[1]:255, bottomRight[0]:255]

        result = "{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}".format(recognize_symbol(topLeftROI), recognize_symbol(topMiddleROI), recognize_symbol(topRightROI), os.linesep, recognize_symbol(centerLeftROI), recognize_symbol(centerMiddleROI), recognize_symbol(centerRightROI), os.linesep, recognize_symbol(bottomLeftROI), recognize_symbol(bottomMiddleROI), recognize_symbol(bottomRightROI))

        output_filename = filename.replace("bmp", "txt")
        store_to_file(result, outputTextPath + "\{0}".format(output_filename))
    except Exception:
        pass

#cv2.destroyAllWindows()  