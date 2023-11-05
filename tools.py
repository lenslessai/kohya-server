import cv2

# Load the pre-trained Haar Cascade Classifier for face detection
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def crop_and_resize(image_path, target_resolution):
    print("crop_and_resize " + image_path)
    # Load the image
    image = cv2.imread(image_path)
    
    # Get the dimensions of the image
    height, width, _ = image.shape

    # Calculate the side length for the square crop
    side_length = min(height, width)

    # Calculate the cropping region to preserve faces if detected
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) > 0:
        # If faces are detected, try to center the crop around the first detected face
        x, y, w, h = faces[0]
        center_x, center_y = x + w // 2, y + h // 2
        x1 = max(0, center_x - side_length // 2)
        y1 = max(0, center_y - side_length // 2)
        x2 = min(width, x1 + side_length)
        y2 = min(height, y1 + side_length)
    else:
        # If no faces are detected, crop the center of the image
        x1 = (width - side_length) // 2
        y1 = (height - side_length) // 2
        x2 = x1 + side_length
        y2 = y1 + side_length

    # Perform the crop
    cropped_image = image[y1:y2, x1:x2]

    # Resize the cropped image to the target resolution
    resized_image = cv2.resize(cropped_image, target_resolution)

    cv2.imwrite(image_path, result_image)