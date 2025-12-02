from depth_model import *
from PIL import Image


# # Load model once
# model, processor, device = load_depth_model_opt(use_global_only=True)

# # Run inference
# image_path = "data/mall.png"
# depth, t = estimate_depth_from_model(image_path, model, processor, device)


# img = Image.open(image_path).convert("RGB")

# show_depth_heatmap(img, depth, t)


#IMAGE_PATH = "data/mall.png"  # Replace with your image
    
# 1. Initialize Models (Load once)
# Using global_only=True for speed, False for maximum accuracy
# d_model, d_processor, device = load_depth_model_opt(use_global_only=True)
# yolo_model = load_yolo_model()

# # 2. Run Analysis
# try:
#     original, result_img, depth_map = analyze_scene(
#         IMAGE_PATH, 
#         d_model, 
#         d_processor, 
#         yolo_model, 
#         device
#     )
    
#     # 3. Show Results
#     plt.figure(figsize=(15, 5))
    
#     # First Subplot: 1 Row, 2 Columns, Position 1
#     plt.subplot(1, 2, 1)
#     plt.title("Original")
#     plt.imshow(original)
#     plt.axis('off')

#     # Second Subplot: 1 Row, 2 Columns, Position 2
#     plt.subplot(1, 2, 2)
#     plt.title("Detections & Distances")
#     plt.imshow(result_img)
#     plt.axis('off')
    
#     plt.tight_layout() # Optional: Fixes padding issues
#     plt.show()
    
# except FileNotFoundError:
#     print(f"Error: Could not find image at {IMAGE_PATH}")

# --- test iheb ---


#--------------------------------------------------------------------------
# Define the full URL to your Flask endpoint
# NOTE: Replace with the actual URL and port your Flask app is running on
API_URL = "http://127.0.0.1:5000/api/yolo/latest" 

# 1. Initialize Models (Load once)
d_model, d_processor, device = load_depth_model_opt(use_global_only=True)

# 2. Get Image from API
print(f"Fetching latest frame from {API_URL}...")
original_image, detections_data = get_image_from_api(API_URL)

if original_image is None:
    print("Failed to retrieve image. Exiting analysis.")
else:
    # 3. Run Analysis
    # NOTE: You will need to update your 'analyze_scene' function to accept 
    # a PIL Image object instead of a file path (and potentially use detections_data)
    try:
        while True:
            data = analyze_scene(
                original_image,
                detections_data,
                d_model, 
                d_processor, 
                device
            )
            # if data.get("objects"):
            #     print(f"🚀 Sending {len(data['objects'])} objects to backend...")
                
            #     try:
            #         response = requests.post(
            #             "http://127.0.0.1:5000/api/depth/upload_depth_result", 
            #             json=data,
            #             timeout=5
            #         )
                    
            #         if response.status_code == 200:
            #             print(f"✅ Saved to DB with ID: {response.json().get('id')}")
            #         else:
            #             print(f"❌ Server Error {response.status_code}: {response.text}")

            #     except Exception as e:
            #         print(f"❌ Connection Failed: {e}")
            # else:
            #     print("Skipping upload (no objects detected).")
            print(f"🚀 Sending {len(data['objects'])} objects to backend...")
                
            try:
                response = requests.post(
                    "http://127.0.0.1:5000/api/depth/upload_depth_result", 
                    json=data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    print(f"✅ Saved to DB with ID: {response.json().get('id')}")
                else:
                    print(f"❌ Server Error {response.status_code}: {response.text}")

            except Exception as e:
                print(f"❌ Connection Failed: {e}")
            original_image, detections_data = get_image_from_api(API_URL)
            time.sleep(1)
            # # 4. Show Results (as before)
            # plt.figure(figsize=(15, 5))
            
            # plt.subplot(1, 2, 1)
            # plt.title("Original (from API)")
            # plt.imshow(original_image)
            # plt.axis('off')

            # plt.subplot(1, 2, 2)
            # plt.title("Detections & Distances")
            # plt.imshow(result_img)
            # plt.axis('off')
            
            # plt.tight_layout()
            # plt.show()
        
    except Exception as e:
        print(f"Error during scene analysis: {e}")