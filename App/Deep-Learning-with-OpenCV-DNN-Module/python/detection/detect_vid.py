import cv2
import time
import numpy as np

# Load the COCO class names
with open('../../input/object_detection_classes_coco.txt', 'r') as f:
    class_names = f.read().split('\n')

# Get a different color array for each of the classes
COLORS = np.random.uniform(0, 255, size=(len(class_names), 3))

# Load the DNN model
model = cv2.dnn.readNet(model='../../input/frozen_inference_graph.pb',
                        config='../../input/ssd_mobilenet_v2_coco_2018_03_29.pbtxt.txt', 
                        framework='TensorFlow')

# Capture the video
cap = cv2.VideoCapture(0)

# Get the video frames' width and height
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# Get screen size
screen_width = 1920  # Adjust to your screen resolution
screen_height = 1080

# Calculate the scale while maintaining the aspect ratio
scale = min(screen_width / frame_width, screen_height / frame_height)
resized_width = int(frame_width * scale)
resized_height = int(frame_height * scale)

# Create the `VideoWriter()` object
out = cv2.VideoWriter('../../outputs/video_result.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, 
                      (resized_width, resized_height))

# Create a full-screen window
cv2.namedWindow('image', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('image', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Detect objects in each frame of the video
while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (resized_width, resized_height))  # Resize while keeping aspect ratio
        image_height, image_width, _ = frame.shape
        
        # Create blob from image
        blob = cv2.dnn.blobFromImage(image=frame, size=(300, 300), mean=(104, 117, 123), swapRB=True)
        
        # Start time to calculate FPS
        start = time.time()
        model.setInput(blob)
        output = model.forward()
        
        # End time after detection
        end = time.time()
        
        # Calculate the FPS for current frame detection
        fps = 1 / (end - start)
        
        # Loop over each of the detections
        for detection in output[0, 0, :, :]:
            # Extract the confidence of the detection
            confidence = detection[2]
            
            # Draw bounding boxes only if confidence is above a certain threshold
            if confidence > 0.4:
                # Get the class id
                class_id = int(detection[1]) - 1
                
                # Map the class id to the class 
                class_name = class_names[class_id] if class_id < len(class_names) else "Unknown"
                color = COLORS[class_id]
                
                # Get the bounding box coordinates
                box_x = int(detection[3] * image_width)
                box_y = int(detection[4] * image_height)
                box_width = int(detection[5] * image_width)
                box_height = int(detection[6] * image_height)
                
                # Draw a rectangle around each detected object
                cv2.rectangle(frame, (box_x, box_y), (box_width, box_height), color, thickness=2)
                
                # Put the class name text on the detected object
                cv2.putText(frame, class_name, (box_x, box_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                
                # Put the FPS text on top of the frame
                cv2.putText(frame, f"{fps:.2f} FPS", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Show the image in full screen
        cv2.imshow('image', frame)
        out.write(frame)
        
        # Exit if 'q' is pressed
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
out.release()
cv2.destroyAllWindows()
