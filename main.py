import cv2 

# Yolo Model (Object Detection)
from ultralytics import YOLO 

# Bounding Boxes (Annotating Frames)
import supervision as sv 

# To communicate between scripts
import socket

HOST = "127.0.0.1"  # Localhost
PORT = 65432        # Port to listen on

is_music_playing = False

def main():
    # Capturing Video from Default Mac Camera
    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return

    # Importing Pretrained Model
    model = YOLO("yolov8l.pt")


    # Setting up supervision annotator
    # https://stackoverflow.com/questions/78287307/boxannotator-is-deprecated
    bounding_box_annotator = sv.BoxAnnotator(
        thickness=2
    )

    label_annotator = sv.LabelAnnotator(
        text_scale=1,
        text_thickness=2,
        text_padding=5
    )


    # Stream video
    while True:
        ret, frame = cap.read()
        
        # Running YOLOv8 on the frame
        # This prints out the information onto terminal 
        results = model(frame)

        for result in results:
            # This converts the results from YOLOv8 into bounding box detection
            detections = sv.Detections.from_ultralytics(result)

            # This gets the object labels and confidence of objects 
            labels = [
                f"{model.model.names[class_id]} {confidence:0.2f}"
                for _, _, confidence, class_id, _, _
                in detections
            ]
            
            # Filtering for object confidence > 0.6
            confident_detections = detections[detections.confidence > 0.6] 

            # If confident about finding a person
            if any(confident_detections.class_id == 0):
                is_music_playing = True
            else:
                is_music_playing = False
                

            # This annotates the current frame with the detection bounding box
            frame = bounding_box_annotator.annotate(scene=frame, detections=detections)

            # This annotates the current frame with a label
            frame = label_annotator.annotate(scene=frame,labels=labels, detections=detections)

        # Window name is yolov8
        cv2.imshow("yolov8", frame)

        # Press Escape (27 ASCII) to Break
        # 30 indicates the number of ms per frame that OpenCV will wait for key press
        if (cv2.waitKey(30) == 27):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()