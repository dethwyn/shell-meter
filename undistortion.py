from __future__ import print_function
import numpy as np
import cv2
import glob

img_names_undistort = [img for img in
                       glob.glob("*.png")]
new_path = ""

camera_matrix = np.array([[884.35974334, 0., 951.63631164],
                          [0., 851.30228182, 478.29760615],
                          [0., 0., 1.]])
dist_coefs = np.array(
    [-0.06448633, - 0.21519168, 0.00610189, 0.00060811, 0.22811069])

i = 0

# for img_found in img_names_undistort:
while i < len(img_names_undistort):
    img = cv2.imread(img_names_undistort[i])
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    print(img_names_undistort[i])
    h, w = img.shape[:2]
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(camera_matrix,
                                                      dist_coefs,
                                                      (w, h), 1, (w, h))

    dst = cv2.undistort(img, camera_matrix, dist_coefs, None, newcameramtx)

    dst = cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)

    # crop and save the image
    x, y, w, h = roi
    dst = dst[y:y + h - 50, x + 70:x + w - 20]
    # outfile = img_names_undistort + '_undistorte.png'
    print('Undistorted image written to: %s' % str(i))
    cv2.imwrite(str(i) + '.jpg', dst)
    i = i + 1
