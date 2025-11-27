import torch
from PIL import Image
import numpy as np
from transformers import DepthProImageProcessor, DepthProForDepthEstimation
import time
import torch
from transformers import DepthProForDepthEstimation, DepthProImageProcessor, AutoImageProcessor
from ultralytics import YOLO
import cv2
import torch
import requests        # <--- NEW
import base64          # <--- NEW
from io import BytesIO
def load_depth_model_opt(use_global_only=True):
    """
    Extracts the loading phase including device setup, model initialization, 
    and turbo-mode configuration.
    """
    
    # 1. Setup Device & Optimizations
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.benchmark = True
    
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Running on: {device}")

    print("Loading model...")

    # 2. Load Model in FP16
    # Note: attn_implementation="sdpa" is crucial for RTX cards
    model = DepthProForDepthEstimation.from_pretrained(
        "apple/DepthPro-hf", 
        dtype=torch.float16,
        attn_implementation="sdpa"
    )

    # 3. Apply Turbo Mode logic
    if use_global_only:
        print("Mode: GLOBAL ONLY (Fastest)")
        # Setting this to an empty list forces the model to skip cropping logic
        # This prevents the ValueError when using custom resolutions like 1024x1024
        model.config.scaled_images_ratios = [] 
    else:
        print("Mode: STANDARD (High Precision)")
        # Default usually includes [0.25] or similar ratios
        if not model.config.scaled_images_ratios:
            model.config.scaled_images_ratios = [0.25]

    model.to(device)
    model.eval()

    # 4. Initialize Processor
    try:
        # NOTE: To fix the 1024x1024 crash without 'use_global_only=True', 
        # you would add size={"height": 1024, "width": 1024} inside here.
        processor = DepthProImageProcessor.from_pretrained("apple/DepthPro-hf")
    except Exception as e:
        print(f"Processor load warning: {e}")
        processor = AutoImageProcessor.from_pretrained("apple/DepthPro-hf")

    return model, processor, device
def load_depth_model(use_global_only=True, device=None):
    """
    Loads DepthPro model and processor once, to reuse across multiple predictions.

    Parameters:
        use_global_only : bool
            If True → global-only inference (fast).
            If False → adds patch refinement (slower, sharper).
        device : "cuda" or "cpu" (auto if None)

    Returns:
        model, processor, device
    """

    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load model with FP16 and SDPA (flash attention)
    model = DepthProForDepthEstimation.from_pretrained(
        "apple/DepthPro-hf",
        dtype=torch.float16,
        attn_implementation="sdpa",
        use_fov_model=True
    )

    # Turbo mode logic
    if use_global_only:
        model.config.scaled_images_ratios = []
    else:
        model.config.scaled_images_ratios = [0.5]

    model.to(device)
    model.eval()

    # Load processor
    try:
        processor = DepthProImageProcessor.from_pretrained("apple/DepthPro-hf")
    except:
        from transformers import AutoImageProcessor
        processor = AutoImageProcessor.from_pretrained("apple/DepthPro-hf")

    return model, processor, device

#ma tetmasech
def estimate_depth_from_model(input_image, model, processor, device):
    """
    Runs depth inference using a pre-loaded model and processor.

    Parameters:
        input_image : PIL.Image or image path
        model       : Loaded DepthPro model
        processor   : Loaded image processor
        device      : Torch device

    Returns:
        depth_map (numpy array), inference_time (float)
    """

    # Load if a path is provided
    if isinstance(input_image, str):
        image = Image.open(input_image).convert("RGB")
    else:
        image = input_image.convert("RGB")

    # Prepare tensors
    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(device, dtype=torch.float16) for k, v in inputs.items()}

    # Warmup
    if torch.cuda.is_available():
        with torch.no_grad():
            model(**inputs)
        torch.cuda.synchronize()

    # Inference
    start = time.time()
    with torch.no_grad():
        outputs = model(**inputs)

    if torch.cuda.is_available():
        torch.cuda.synchronize()
    end = time.time()

    inference_time = end - start

    # Extract depth
    predicted_depth = 1/outputs.predicted_depth
    depth_map = torch.nn.functional.interpolate(
        predicted_depth.unsqueeze(1),
        size=image.size[::-1],
        mode="bilinear",
        align_corners=False
    ).squeeze().float().cpu().numpy()
    print("inference time = ",inference_time,"sec")
    return depth_map, inference_time


def estimate_depth(
    input_image,
    use_global_only=True,
    device=None
):
    """
    Runs DepthPro on an image and returns a depth map (NumPy array).

    Parameters:
        input_image      : Path to image OR PIL.Image instance
        use_global_only  : If True, runs only global model (faster, softer edges)
        device           : "cuda" or "cpu". If None, auto-detect.

    Returns:
        depth_map (numpy.ndarray), inference_time (float)
    """

    # --- DEVICE SETUP ---
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load image if path provided
    if isinstance(input_image, str):
        image = Image.open(input_image).convert("RGB")
    else:
        image = input_image.convert("RGB")

    # Load model (FP16 + SDPA flash attention)
    model = DepthProForDepthEstimation.from_pretrained(
        "apple/DepthPro-hf",
        dtype=torch.float16,
        attn_implementation="sdpa",
        use_fov_model=False
    )

    # Turbo mode logic
    if use_global_only:
        model.config.scaled_images_ratios = []   # no patch refinement
    else:
        model.config.scaled_images_ratios = [0.25]

    model.to(device)
    model.eval()

    # Load processor
    try:
        processor = DepthProImageProcessor.from_pretrained("apple/DepthPro-hf")
    except:
        from transformers import AutoImageProcessor
        processor = AutoImageProcessor.from_pretrained("apple/DepthPro-hf")

    # Prepare inputs
    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(device, dtype=torch.float16) for k, v in inputs.items()}

    # Warmup
    if torch.cuda.is_available():
        with torch.no_grad():
            model(**inputs)
        torch.cuda.synchronize()

    # Run inference
    start = time.time()
    with torch.no_grad():
        outputs = model(**inputs)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    end = time.time()

    inference_time = end - start

    predicted_depth = outputs.predicted_depth

    # Resize to original resolution
    depth_map = torch.nn.functional.interpolate(
        predicted_depth.unsqueeze(1),
        size=image.size[::-1],
        mode="bicubic",
        align_corners=False,
    ).squeeze().float().cpu().numpy()

    return depth_map, inference_time



import matplotlib.pyplot as plt

def show_depth_heatmap(image, depth, inference_time=None):
    """
    Displays the original image and depth heatmap side by side.

    Parameters:
        image           : PIL image (RGB)
        depth           : numpy array returned by the depth model
        inference_time  : float (optional) – printed in the title
    """
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))

    # Original image
    ax[0].imshow(image)
    ax[0].set_title("Original")
    ax[0].axis("off")

    # Depth heatmap
    title = "Depth"
    if inference_time is not None:
        title += f" ({inference_time:.2f}s)"

    ax[1].imshow(depth, cmap="inferno")
    ax[1].set_title(title)
    ax[1].axis("off")

    plt.tight_layout()
    plt.show()


def load_yolo_model():
    YOLO_MODEL_PATH = "yolo11n.pt"
    yolo = YOLO(YOLO_MODEL_PATH)
    return yolo

def build_front_roi(width, height):
    left_bottom = (int(width * 0.20), height)
    right_bottom = (int(width * 0.80), height)
    right_top = (int(width * 0.58), int(height * 0.38))
    left_top = (int(width * 0.42), int(height * 0.38))
    return np.array([left_bottom, right_bottom, right_top, left_top], dtype=np.int32)

def get_distance_for_box(depth_map, box, patch_radius=6):
    """
    Estimates the depth for a single object bounding box.

    Parameters:
        depth_map     : 2D numpy array of depth values (same size as image)
        box           : tuple (x1, y1, x2, y2)
        patch_radius  : how many pixels around the measuring point to sample

    Returns:
        depth_value (float or NaN)
            Median depth from patch around bottom-center of the bounding box.
    """

    x1, y1, x2, y2 = box

    # Compute center bottom
    cx = (x1 + x2) // 2
    cy = (y1+y2) //2

    # Compute window (convert to int explicitly!)
    xmin = int(max(cx - patch_radius, x1))
    xmax = int(min(cx + patch_radius, x2))
    ymin = int(max(cy - patch_radius, y1))
    ymax = int(min(cy + patch_radius, y2))

    # Now safe to slice
    patch = depth_map[ymin:ymax+1, xmin:xmax+1]

    patch = patch[np.isfinite(patch)]
    return float(np.median(patch)) if patch.size > 0 else float("nan")


def is_box_in_roi(box, roi_polygon):
    """
    Checks if the 'foot' (bottom center) of the object is inside the defined ROI.
    """
    x1, y1, x2, y2 = map(int, box)
    
    # Calculate bottom center point of the bounding box
    cx = int((x1 + x2) / 2)
    cy = int((y1+y2)/2)
    
    # cv2.pointPolygonTest returns:
    # positive if inside, negative if outside, 0 if on edge
    result = cv2.pointPolygonTest(roi_polygon, (cx, cy), False)
    
    return result >= 0

def annotate_frame(image_pil, boxes, classes, confidences, distances, class_names, roi_polygon=None):
    """
    Draws bounding boxes with dynamic colors based on distance:
    < 5m  : RED
    < 10m : YELLOW
    > 10m : GREEN
    """
    # Convert PIL to OpenCV format (RGB -> BGR)
    img_cv = np.array(image_pil)
    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
    
    # Draw ROI Polygon if provided
    if roi_polygon is not None:
        cv2.polylines(img_cv, [roi_polygon], isClosed=True, color=(255, 255, 0), thickness=2) # Cyan ROI

    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box)
        label = class_names[int(classes[i])]
        conf = confidences[i]
        dist = distances[i]
        
        # --- NEW COLOR LOGIC ---
        if np.isnan(dist):
            # Unknown distance -> Grey or Red (your choice, defaulting to Red/Danger)
            color = (0, 0, 255) 
        elif dist < 5.0:
            # Close/Danger -> Red (BGR)
            color = (0, 0, 255) 
        elif dist < 10.0:
            # Warning -> Yellow (BGR: 0 Blue, 255 Green, 255 Red)
            color = (0, 255, 255) 
        else:
            # Safe -> Green (BGR)
            color = (0, 255, 0)
        # -----------------------
        
        # Draw Box
        cv2.rectangle(img_cv, (x1, y1), (x2, y2), color, 2)
        
        # Draw Label text (Class + Distance)
        text = f"{label}"
        if not np.isnan(dist):
            text += f" {dist:.1f}m"
            
        cv2.putText(img_cv, text, (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Convert back to RGB for PIL/Matplotlib
    return cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)

# def analyze_scene(input_path, depth_model, depth_processor, yolo_model, device):
#     """
#     Full pipeline: Load Image -> Estimate Depth -> Detect Objects -> Filter ROI -> Visualize
#     """
#     # 1. Load Image
#     pil_image = Image.open(input_path).convert("RGB")
#     width, height = pil_image.size
    
#     # 2. Generate ROI Polygon based on image size
#     roi_poly = build_front_roi(width, height)
    
#     # 3. Get Depth Map
#     # Note: DepthPro outputs metric depth (meters)
#     print("Estimating Depth...")
#     depth_map, d_time = estimate_depth_from_model(pil_image, depth_model, depth_processor, device)
    
#     # 4. Get Object Detections (YOLO)
#     print("Detecting Objects...")
#     # classes argument filters for vehicles/people (COCO: 0=person, 2=car, 3=motor, 5=bus, 7=truck)
#     """hedhi win yolo maach nestha9ouh"""
#     results = yolo_model(pil_image, classes=[0, 2, 3, 5, 7], verbose=False)[0]
    
#     boxes = results.boxes.xyxy.cpu().numpy()
#     cls_ids = results.boxes.cls.cpu().numpy()
#     confs = results.boxes.conf.cpu().numpy()
#     class_names = yolo_model.names
    
#     valid_boxes = []
#     valid_classes = []
#     valid_confs = []
#     calculated_distances = []
    
#     # 5. Process Detections
#     for i, box in enumerate(boxes):
#         # Check if object is relevant (inside ROI)
#         if is_box_in_roi(box, roi_poly):
#             dist = get_distance_for_box(depth_map, box)
            
#             valid_boxes.append(box)
#             valid_classes.append(cls_ids[i])
#             valid_confs.append(confs[i])
#             calculated_distances.append(dist)
            
#             print(f"Found {class_names[int(cls_ids[i])]} at {dist:.2f} meters.")

#     # 6. Visualisation
#     annotated_img_arr = annotate_frame(
#         pil_image, 
#         valid_boxes, 
#         valid_classes, 
#         valid_confs, 
#         calculated_distances, 
#         class_names,
#         roi_poly
#     )
    
#     return pil_image, annotated_img_arr, depth_map
import numpy as np 
# You may still need to import these functions from their respective modules
# from depth_model import get_distance_for_box, build_front_roi, is_box_in_roi, estimate_depth_from_model
# from utils import annotate_frame
# from PIL import Image 


# IMPORTANT: Added 'detections_data' as the second argument
import numpy as np

import numpy as np
import base64
from io import BytesIO
from PIL import Image

def analyze_scene(input_image, detections_data, depth_model, depth_processor, device): 
    """
    Full pipeline: Use Input Image (PIL) -> Estimate Depth -> USE PRE-SAVED Detections -> Filter ROI -> Visualize
    
    Returns:
        dict: {
            "image": "base64_string...", 
            "objects": [ {"class": "person", "distance": 2.5, "box": [x,y,x,y]}, ... ]
        }
    """
    
    # 1. Load Image
    pil_image = input_image 
    width, height = pil_image.size
    
    # 2. Generate ROI Polygon
    roi_poly = build_front_roi(width, height)
    
    # 3. Get Depth Map
    print("Estimating Depth...")
    depth_map, d_time = estimate_depth_from_model(pil_image, depth_model, depth_processor, device)
    
    # --- 4. Process Pre-saved Detections ---
    print("Processing Pre-saved Detections...")

    # Manual COCO mapping
    CLASS_NAME_TO_ID = {
        "person": 0, "bicycle": 1, "car": 2, "motorcycle": 3, "airplane": 4, 
        "bus": 5, "train": 6, "truck": 7, "boat": 8
    }
    class_names_map = {v: k for k, v in CLASS_NAME_TO_ID.items()}
    
    boxes_list = []
    cls_ids_list = []
    
    # Loop through JSON detections
    for detection in detections_data:
        class_name = detection.get("class")
        box = detection.get("box")
        cls_id = CLASS_NAME_TO_ID.get(class_name)
        
        if cls_id is not None:
            # Filter: Person(0) or Vehicle(2,3,5,7)
            if cls_id in [0, 2, 3, 5, 7]:
                boxes_list.append(box)
                cls_ids_list.append(cls_id)

    boxes = np.array(boxes_list)
    cls_ids = np.array(cls_ids_list)
    
    # Dummy confidence
    confs = np.ones(len(cls_ids)) if len(cls_ids) > 0 else np.array([])

    # Helper function to convert PIL to Base64
    def encode_image_to_base64(img_pil):
        buffered = BytesIO()
        img_pil.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    # --- Handle No Detections Case ---
    if boxes.size == 0:
         print("No relevant detections found.")
         # Return original image as base64 and empty list
         return {
             "image": encode_image_to_base64(pil_image),
             "objects": []
         }

    # --- 5. Process Detections & Collect Data ---
    valid_boxes = []
    valid_classes = []
    valid_confs = []
    calculated_distances = []
    
    # This list will hold the clean JSON data
    json_objects_list = []
    
    for i, box in enumerate(boxes):
        if is_box_in_roi(box, roi_poly):
            dist = get_distance_for_box(depth_map, box)
            
            # Add to lists for Annotation function
            valid_boxes.append(box)
            valid_classes.append(cls_ids[i])
            valid_confs.append(confs[i])
            calculated_distances.append(dist)
            
            # Get class name
            obj_name = class_names_map.get(int(cls_ids[i]), "Unknown")
            
            # Add to JSON result list
            # Note: Convert numpy types to native python types for JSON serialization
            json_objects_list.append({
                "class": obj_name,
                "distance": float(round(dist, 2)), # Round to 2 decimals
            })
            
            print(f"Found {obj_name} at {dist:.2f} meters.")

    # 6. Visualization
    annotated_img_arr = annotate_frame(
        pil_image, 
        valid_boxes, 
        valid_classes, 
        valid_confs, 
        calculated_distances, 
        class_names_map,
        roi_poly
    )
    
    # 7. Convert Annotated Array to Base64
    # annotate_frame returns a NumPy array, we must convert it back to PIL
    result_pil = Image.fromarray(annotated_img_arr)
    base64_image = encode_image_to_base64(result_pil)
    
    # 8. Return final JSON
    return {
        "image": base64_image,
        "objects": json_objects_list
    }

def get_image_from_api(api_url="http://127.0.0.1:5000/api/yolo/latest"):
    """
    Fetches the latest frame and detections from the Flask API, 
    safely handles list wrapping, decodes Base64, and returns data.
    """
    
    # 1. Fetch the data from the API
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        raw_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None, None
    
    # --- FIX 1: UNWRAP THE DATA ---
    if isinstance(raw_data, list) and len(raw_data) > 0:
        data = raw_data[0]
    elif isinstance(raw_data, dict):
        data = raw_data
    else:
        print("Error: API response is empty or not in the expected format.")
        return None, None
    # 2. Extract Base64 string and decode
    try:
        # Get the 'image_data' field safely. If it's missing, this returns None.
        image_data_payload = data.get("image_data")
        
        # Check 1: Ensure image_data exists before proceeding
        if image_data_payload is None:
            raise KeyError("The key 'image_data' is missing or null in the response.")

        # Handle inner list wrap
        if isinstance(image_data_payload, list) and image_data_payload:
            image_data_dict = image_data_payload[0]
        else:
            image_data_dict = image_data_payload

        # Check 2: Ensure the inner dictionary exists
        if image_data_dict is None:
            raise ValueError("Image data structure is invalid after unwrapping.")

        # 5. Create a PIL Image from bytes
        image_bytes = base64.b64decode(image_data_dict)
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        
        # 6. Extract detections (Safe because 'data' is a dict)
        detections = data.get("detections", []) 
        
        return image, detections
        
    except (KeyError, ValueError) as e:
        # Provide a more specific error message based on which key/value failed
        print(f"Error decoding or loading image: Invalid JSON structure. {e}")
        return None, None
    except Exception as e:
        print(f"Error decoding or loading image: {e}")
        return None, None