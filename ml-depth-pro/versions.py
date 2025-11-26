import torch

if torch.cuda.is_available():
    print(f"Success! PyTorch can see your GPU.")
    print(f"Device Name: {torch.cuda.get_device_name(0)}")
else:
    print("--- PROBLEM ---")
    print("PyTorch CANNOT see your GPU.")
    print("This is why your code is slow.")
    print("Please follow Step 2 to fix your installation.")