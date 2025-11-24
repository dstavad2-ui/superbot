#!/usr/bin/env python3
"""
ECOSYSTEM CORE: Catalog Management
Integrates with AI, NFT, self-heal, subscriptions, and heartbeat
"""

import json, os, asyncio
from self_heal import self_heal

class CatalogManager:
    def __init__(self, catalog_file="catalog.json", ai_engine=None):
        self.catalog_file = catalog_file
        self.ai_engine = ai_engine  # HybridAI instance for AI-powered descriptions
        self.catalog = self._load_catalog()

    def _load_catalog(self):
        try:
            if os.path.exists(self.catalog_file):
                with open(self.catalog_file, "r") as f:
                    return json.load(f)
            return {
                "brand": "🌒   N T R L I '   S E L E C T I O N",
                "tagline": "Det her er ikke bare noget du tilvælger, det er noget du genkender.",
                "sections": [],
                "premium_tiers": [],
                "info": {},
                "ai_insights": [],  # Track AI-generated product insights
                "nft_catalog": []   # Track NFT-ified products
            }
        except Exception as e:
            self_heal(f"Catalog load failed: {e}")
            return {"sections": [], "premium_tiers": [], "ai_insights": [], "nft_catalog": []}

    def _save_catalog(self):
        try:
            with open(self.catalog_file, "w") as f:
                json.dump(self.catalog, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self_heal(f"Catalog save failed: {e}")
            return False

    async def generate_product_insight(self, product_name, specs):
        """Use AI to generate intelligent product descriptions"""
        try:
            if not self.ai_engine:
                return None
            
            prompt = f"Generate a compelling, brief product insight for: {product_name} ({specs}). Keep it 1-2 sentences, professional."
            insight = await self.ai_engine.generate(prompt)
            
            self.catalog["ai_insights"].append({
                "product": product_name,
                "insight": insight,
                "timestamp": str(os.times())
            })
            self._save_catalog()
            return insight
        except Exception as e:
            self_heal(f"Generate product insight failed: {e}")
            return None

    def add_section(self, title, emoji, description=""):
        try:
            section = {
                "title": title,
                "emoji": emoji,
                "description": description,
                "products": []
            }
            self.catalog["sections"].append(section)
            self._save_catalog()
            return True
        except Exception as e:
            self_heal(f"Add section failed: {e}")
            return False

    def add_product_to_section(self, section_title, name, specs, price, notes=""):
        try:
            for section in self.catalog["sections"]:
                if section["title"] == section_title:
                    product = {
                        "name": name,
                        "specs": specs,
                        "price": price,
                        "notes": notes,
                        "status": "available",
                        "nft_id": None,  # Will be set when NFT is created
                        "ai_generated": False
                    }
                    section["products"].append(product)
                    self._save_catalog()
                    return True
            return False
        except Exception as e:
            self_heal(f"Add product failed: {e}")
            return False

    def register_product_nft(self, section_title, product_name, nft_file):
        """Register NFT conversion for a product"""
        try:
            for section in self.catalog["sections"]:
                if section["title"] == section_title:
                    for product in section["products"]:
                        if product["name"] == product_name:
                            product["nft_id"] = nft_file
                            self.catalog["nft_catalog"].append({
                                "product": product_name,
                                "nft_file": nft_file,
                                "section": section_title
                            })
                            self._save_catalog()
                            return True
            return False
        except Exception as e:
            self_heal(f"Register NFT failed: {e}")
            return False

    def update_product(self, section_title, product_name, **kwargs):
        try:
            for section in self.catalog["sections"]:
                if section["title"] == section_title:
                    for product in section["products"]:
                        if product["name"] == product_name:
                            for key, value in kwargs.items():
                                if key in product:
                                    product[key] = value
                            self._save_catalog()
                            return True
            return False
        except Exception as e:
            self_heal(f"Update product failed: {e}")
            return False

    def delete_product(self, section_title, product_name):
        try:
            for section in self.catalog["sections"]:
                if section["title"] == section_title:
                    section["products"] = [p for p in section["products"] if p["name"] != product_name]
                    self._save_catalog()
                    return True
            return False
        except Exception as e:
            self_heal(f"Delete product failed: {e}")
            return False

    def get_section(self, title):
        for section in self.catalog["sections"]:
            if section["title"] == title:
                return section
        return None

    def get_all_sections(self):
        return self.catalog["sections"]

    def get_product_by_nft(self, nft_id):
        """Retrieve product associated with NFT"""
        for section in self.catalog["sections"]:
            for product in section["products"]:
                if product.get("nft_id") == nft_id:
                    return product, section["title"]
        return None, None

    def set_brand_info(self, key, value):
        try:
            self.catalog[key] = value
            self._save_catalog()
            return True
        except Exception as e:
            self_heal(f"Set brand info failed: {e}")
            return False

    def set_opening_hours(self, hours):
        try:
            self.catalog["info"]["opening_hours"] = hours
            self._save_catalog()
            return True
        except Exception as e:
            self_heal(f"Set hours failed: {e}")
            return False

    def set_delivery_info(self, delivery_text):
        try:
            self.catalog["info"]["delivery"] = delivery_text
            self._save_catalog()
            return True
        except Exception as e:
            self_heal(f"Set delivery failed: {e}")
            return False

    def render_menu(self):
        """Generate formatted menu with exact aesthetic"""
        try:
            menu = f"{self.catalog['brand']}\n"
            menu += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            for section in self.catalog["sections"]:
                menu += f"{section['emoji']}  {section['title']}\n"
                menu += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
                if section["description"]:
                    menu += f"{section['description']}\n\n"
                
                for product in section["products"]:
                    menu += f"**{product['name']}**\n"
                    menu += f"{product['specs']}\n"
                    menu += f"💵 {product['price']}\n"
                    if product['notes']:
                        menu += f"{product['notes']}\n"
                    menu += "\n"
            
            menu += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            menu += f"\n\"{self.catalog['tagline']}\"\n"
            
            return menu
        except Exception as e:
            self_heal(f"Render menu failed: {e}")
            return "Menu unavailable"

    def get_ai_insights(self):
        return self.catalog["ai_insights"]

    def get_nft_catalog(self):
        return self.catalog["nft_catalog"]
