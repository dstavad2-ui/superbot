from PIL import Image
from self_heal import self_heal

def convert_to_nft(img_path, output="nft.png"):
    try:
        Image.open(img_path).convert("RGB").save(output)
        return output
    except Exception as e:
        self_heal(f"NFT conversion failed: {e}")
        return None
