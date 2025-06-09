from ultralytics import YOLO

def detect_pothole(image_path):
    model = YOLO('yolov8n.pt')  # Use your trained YOLOv8 model path here
    results = model(image_path)
    # Simulated example output (parse results in actual implementation)
    return {
        'width': 45.0,
        'height': 30.0,
        'depth': 5.0,
        'severity': 'orange'  # Based on model detection logic
    }
