import cv2
import imutils
import time
import numpy as np
import rospy
from std_msgs.msg import String

def nothing(x):
    pass

def ball_detection():

    pub = rospy.Publisher('talking_topic', String, queue_size = 10)
    rospy.init_node('publisher_node', anonymous = True)
    rate.rospy.Rate(1)
    rospy.loginfo("S")

    while not rospy.is_shutdown():
        redLower = (160, 90, 90)
        redUpper = (180, 255, 255)

        cap = cv2.VideoCapture(0)
        font = cv2.FONT_HERSHEY_SIMPLEX  # Font style for writing text on video frame
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)         #Set camera resolution
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        time.sleep(2.0)

        Kernal = np.ones((3, 3), np.uint8)

        while True:
            ret, frame = cap.read()
            frame = cv2.flip(frame, +1)  # Mirror image frame

            if not ret:  # If frame is not read then exit
                break

            blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            width, height = frame.shape[:2]
            frame2 = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)  # BGR to HSV

            # hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(frame2, redLower, redUpper)
            # mask = cv2.erode(mask, None, iterations=2)
            # mask = cv2.dilate(mask, None, iterations=2)
            opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, Kernal)  # Morphology
            res = cv2.bitwise_and(frame, frame, mask=opening)  # Apply mask on original image

            # cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
            # cv2.CHAIN_APPROX_SIMPLE)
            # cnts = imutils.grab_contours(cnts)
            # center = None

            contours, hierarchy = cv2.findContours(opening, cv2.RETR_TREE,  ##Find contours
                                                   cv2.CHAIN_APPROX_NONE)

            if len(contours) > 0:
                c = max(contours, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                Cx = int(M['m10'] / M['m00'])
                Cy = int(M['m01'] / M['m00'])
                S = 'Location of object: ' + '(' + str(Cx) + ',' + str(Cy) + ')'
                cv2.putText(frame, S, (10, 50), font, 1, (0, 0, 0), 2,
                            cv2.LINE_AA)  # (image, text, org, font, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]])
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                # To see the centroid clearly
                if radius > 10:
                    cv2.circle(frame, (int(x), int(y)), int(radius), (60, 60, 255),
                               3)  # big circle ((image, center_coordinates, radius, color, thickness))
                    cv2.imwrite("circled_frame.png", cv2.resize(frame, (int(height / 2), int(width / 2))))
                    # cv2.circle(frame, center, 5, (0, 0, 0), -1)                          #small circle

            cv2.imshow("Ball tracking", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    msg = "Coordinates of the object: " + "(" + str(Cx) + "," + str(Cy) + ")"
    pub.publish(msg)
    rate.sleep()


if __name__ == '__main__':
    try:
        ball_detection()
    except rospy.ROSInterruptException:
        pass
