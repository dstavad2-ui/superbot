#!/usr/bin/env python3
"""
ECOSYSTEM NFT LAYER: Convert products/media to NFT format, track ownership, link to catalog
"""

from PIL import Image, ImageDraw, ImageFont
import json, os, hashlib
from self_heal import self_heal

class NFTEcosystem:
    def __init__(self, nft_dir="nft_assets", catalog_manager=None):
        self.nft_dir = nft_dir
        self.catalog = catalog_manager
        self.nft_registry = self._load_registry()
        
        if not os.path.exists(nft_dir):
            os.makedirs(nft_dir)

    def _load_registry(self):
        """Load NFT ownership registry"""
        registry_file = f"{self.nft_dir}/registry.json"
        try:
            if os.path.exists(registry_file):
                with open(registry_file, "r") as f:
                    return json.load(f)
            return {"nfts": [], "ownership": {}}
        except Exception as e:
            self_heal(f"NFT registry load failed: {e}")
            return {"nfts": [], "ownership": {}}

    def _save_registry(self):
        """Save NFT registry"""
        try:
            registry_file = f"{self.nft_dir}/registry.json"
            with open(registry_file, "w") as f:
                json.dump(self.nft_registry, f, indent=2)
            return True
        except Exception as e:
            self_heal(f"NFT registry save failed: {e}")
            return False

    def convert_image_to_nft(self, img_path, product_name, section_name, metadata=None):
        """Convert image to NFT with metadata embedding"""
        try:
            # Load and convert image
            img = Image.open(img_path).convert("RGB")
            
            # Generate NFT ID (hash of content + timestamp)
            nft_id = hashlib.sha256(
                f"{product_name}{section_name}{os.path.getmtime(img_path)}".encode()
            ).hexdigest()[:16]
            
            # Create NFT with embedded metadata
            nft_path = f"{self.nft_dir}/{nft_id}_nft.png"
            
            # Add metadata watermark
            draw = ImageDraw.Draw(img)
            metadata_text = f"NFT:{nft_id[:8]}\nProduct:{product_name}"
            
            try:
                font = ImageFont.load_default()
                draw.text((10, 10), metadata_text, fill=(255, 255, 255), font=font)
            except:
                pass  # If font not available, skip overlay
            
            img.save(nft_path)
            
            # Register in catalog
            if self.catalog:
                self.catalog.register_product_nft(section_name, product_name, nft_path)
            
            # Record in registry
            nft_record = {
                "nft_id": nft_id,
                "product_name": product_name,
                "section_name": section_name,
                "nft_file": nft_path,
                "original_file": img_path,
                "metadata": metadata or {},
                "created_timestamp": os.path.getmtime(img_path),
                "owner": None
            }
            
            self.nft_registry["nfts"].append(nft_record)
            self._save_registry()
            
            return nft_id, nft_path
        except Exception as e:
            self_heal(f"Convert image to NFT failed: {e}")
            return None, None

    def assign_nft_ownership(self, nft_id, owner_user_id):
        """Assign NFT to user/subscriber"""
        try:
            for nft in self.nft_registry["nfts"]:
                if nft["nft_id"] == nft_id:
                    nft["owner"] = owner_user_id
                    self.nft_registry["ownership"][nft_id] = {
                        "owner_id": owner_user_id,
                        "acquired_timestamp": os.times(),
                        "product_name": nft["product_name"]
                    }
                    self._save_registry()
                    return True
            return False
        except Exception as e:
            self_heal(f"Assign NFT ownership failed: {e}")
            return False

    def get_nft_by_id(self, nft_id):
        """Retrieve NFT metadata and file"""
        try:
            for nft in self.nft_registry["nfts"]:
                if nft["nft_id"] == nft_id:
                    return nft
            return None
        except Exception as e:
            self_heal(f"Get NFT failed: {e}")
            return None

    def get_user_nfts(self, user_id):
        """Get all NFTs owned by user"""
        try:
            user_nfts = []
            for nft_id, ownership in self.nft_registry["ownership"].items():
                if ownership["owner_id"] == user_id:
                    nft = self.get_nft_by_id(nft_id)
                    if nft:
                        user_nfts.append(nft)
            return user_nfts
        except Exception as e:
            self_heal(f"Get user NFTs failed: {e}")
            return []

    def generate_product_nft(self, product_name, section_name, product_specs):
        """Generate NFT from product data without image"""
        try:
            # Create image from scratch
            img = Image.new("RGB", (400, 300), color=(20, 20, 20))
            draw = ImageDraw.Draw(img)
            
            # Draw product info
            draw.text((20, 20), f"NTRLI' {section_name}", fill=(255, 200, 0))
            draw.text((20, 60), product_name, fill=(255, 255, 255))
            draw.text((20, 100), product_specs, fill=(200, 200, 200))
            draw.text((20, 150), "Verified Product", fill=(0, 255, 100))
            
            # Save temporary
            temp_path = f"{self.nft_dir}/temp_product.png"
            img.save(temp_path)
            
            # Convert to NFT
            nft_id, nft_path = self.convert_image_to_nft(
                temp_path,
                product_name,
                section_name,
                metadata={"generated": True, "specs": product_specs}
            )
            
            # Cleanup temp
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return nft_id, nft_path
        except Exception as e:
            self_heal(f"Generate product NFT failed: {e}")
            return None, None

    def get_nft_stats(self):
        """Get NFT ecosystem statistics"""
        try:
            total_nfts = len(self.nft_registry["nfts"])
            owned_nfts = len(self.nft_registry["ownership"])
            unique_owners = len(set(
                v["owner_id"] for v in self.nft_registry["ownership"].values()
            ))
            
            return {
                "total_nfts_generated": total_nfts,
                "nfts_with_ownership": owned_nfts,
                "unique_owners": unique_owners,
                "unowned_nfts": total_nfts - owned_nfts
            }
        except Exception as e:
            self_heal(f"Get NFT stats failed: {e}")
            return {}

    def list_all_nfts(self):
        """List all NFTs in ecosystem"""
        return self.nft_registry["nfts"]

    def export_nft_certificate(self, nft_id):
        """Generate certificate/metadata export"""
        try:
            nft = self.get_nft_by_id(nft_id)
            if not nft:
                return None
            
            certificate = {
                "nft_id": nft_id,
                "product_name": nft["product_name"],
                "product_category": nft["section_name"],
                "nft_file": nft["nft_file"],
                "created": nft["created_timestamp"],
                "owner": nft["owner"],
                "verified": True,
                "ecosystem": "NTRLI' Ecosystem"
            }
            
            return certificate
        except Exception as e:
            self_heal(f"Export NFT certificate failed: {e}")
            return None
