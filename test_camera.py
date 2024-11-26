import cv2

cap = cv2.VideoCapture(1)  # Access the default webcam

if not cap.isOpened():
    print("Camera not accessible!")
else:
    print("Camera is working!")
    while True:
        ret, frame = cap.read()  # Read a frame from the camera
        if not ret:
            print("Failed to grab frame!")
            break
        
        cv2.imshow("Camera Feed", frame)  # Display the frame in a window
        
        # Break the loop if the user presses 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()  # Release the camera resource
cv2.destroyAllWindows()  # Close any OpenCV windows
