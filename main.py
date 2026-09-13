import cv2
import csv
import math

# 1. Load the pre-made color model dataset
def load_color_dataset(filename="colors.csv"):
    colors = []
    try:
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                colors.append({
                    "name": row["color_name"],
                    "R": int(row["R"]),
                    "G": int(row["G"]),
                    "B": int(row["B"])
                })
        return colors
    except FileNotFoundError:
        print(f"Error: '{filename}' not found. Please create it in this directory.")
        return []

# 2. Prediction Processor: Distance calculations
def predict_color_name(input_R, input_G, input_B, dataset):
    minimum_distance = float('inf')
    closest_color_name = "Unknown"
    
    for color in dataset:
        # Euclidean Distance formula to map nearest coordinates
        distance = math.sqrt(
            (input_R - color["R"])**2 + 
            (input_G - color["G"])**2 + 
            (input_B - color["B"])**2
        )
        if distance < minimum_distance:
            minimum_distance = distance
            closest_color_name = color["name"]
            
    return closest_color_name

# Global variables for mouse interaction
clicked = False
r = g = b = 0

# Mouse callback function to pick a pixel value
def draw_function(event, x, y, flags, param):
    global b, g, r, clicked
    if event == cv2.EVENT_LBUTTONDBLCLK:
        clicked = True
        # OpenCV frames are structured as BGR, not RGB
        b, g, r = frame[y, x]
        b, g, r = int(b), int(g), int(r)

# --- Main Application Execution ---
if __name__ == "__main__":
    # Load model
    color_model = load_color_dataset()
    if not color_model:
        exit()

    # Initialize live camera stream
    cap = cv2.VideoCapture(0)
    cv2.namedWindow('Color Detection Pipeline')
    cv2.setMouseCallback('Color Detection Pipeline', draw_function)

    print("Pipeline active! Double-click anywhere on the camera window to detect the color.")
    print("Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab camera frame.")
            break

        if clicked:
            # Pass our sampled BGR variables in standard RGB sequence to the processor
            color_name = predict_color_name(r, g, b, color_model)
            
            # Create a visual HUD overlay block on top of the stream window
            cv2.rectangle(frame, (20, 20), (750, 60), (b, g, r), -1)
            text = f"Detected: {color_name} (R:{r} G:{g} B:{b})"
            
            # Change text color dynamically for dark/light backgrounds
            text_color = (0, 0, 0) if (r + g + b) > 600 else (255, 255, 255)
            cv2.putText(frame, text, (50, 50), 2, 0.8, text_color, 2, cv2.LINE_AA)

        cv2.imshow('Color Detection Pipeline', frame)

        # Break loop when 'q' is pressed
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
