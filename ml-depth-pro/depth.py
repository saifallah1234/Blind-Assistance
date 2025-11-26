from depth_model import *
from PIL import Image


# # Load model once
# model, processor, device = load_depth_model_opt(use_global_only=True)

# # Run inference
# image_path = "data/mall.png"
# depth, t = estimate_depth_from_model(image_path, model, processor, device)


# img = Image.open(image_path).convert("RGB")

# show_depth_heatmap(img, depth, t)


IMAGE_PATH = "data/mall.png"  # Replace with your image
    
# 1. Initialize Models (Load once)
# Using global_only=True for speed, False for maximum accuracy
d_model, d_processor, device = load_depth_model_opt(use_global_only=True)
yolo_model = load_yolo_model()

# 2. Run Analysis
try:
    original, result_img, depth_map = analyze_scene(
        IMAGE_PATH, 
        d_model, 
        d_processor, 
        yolo_model, 
        device
    )
    
    # 3. Show Results
    plt.figure(figsize=(15, 5))
    
    # First Subplot: 1 Row, 2 Columns, Position 1
    plt.subplot(1, 2, 1)
    plt.title("Original")
    plt.imshow(original)
    plt.axis('off')

    # Second Subplot: 1 Row, 2 Columns, Position 2
    plt.subplot(1, 2, 2)
    plt.title("Detections & Distances")
    plt.imshow(result_img)
    plt.axis('off')
    
    plt.tight_layout() # Optional: Fixes padding issues
    plt.show()
    
except FileNotFoundError:
    print(f"Error: Could not find image at {IMAGE_PATH}")
