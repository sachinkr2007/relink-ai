import json
import re
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
from google import genai
from ..utils.image_helpers import hash_similarity, compute_color_histogram, color_similarity
from ..config import settings

class VisualMatcher:
    """
    Evaluates visual similarity between two item images.
    Uses Google Gemini 3.8 Flash Multimodal Vision when configured,
    and perceptual hash (dHash) + HSV color histogram when offline.
    """
    
    @staticmethod
    def _get_full_image_path(rel_path: Optional[str]) -> Optional[Path]:
        if not rel_path:
            return None
        # Handle multiple comma-separated image paths
        first_path = rel_path.split(",")[0].strip()
        clean = first_path.lstrip("/").replace("\\", "/")
        
        # 1. Try relative to PROJECT_ROOT
        full_path = settings.PROJECT_ROOT / clean
        if full_path.exists():
            return full_path
            
        # 2. Try direct in UPLOADS_DIR
        filename = Path(clean).name
        upload_path = settings.UPLOADS_DIR / filename
        if upload_path.exists():
            return upload_path
            
        # 3. Try relative to current working dir
        cwd_path = Path.cwd() / clean
        if cwd_path.exists():
            return cwd_path
            
        return None

    @classmethod
    def local_match(
        cls,
        image_path1: Optional[str], hash1: Optional[str],
        image_path2: Optional[str], hash2: Optional[str]
    ) -> Tuple[float, str]:
        """Local perceptual hash, file digest & color histogram matching."""
        if not image_path1 or not image_path2:
            return 0.5, "One or both items have no image uploaded; using neutral baseline (50%)."
        
        p1 = cls._get_full_image_path(image_path1)
        p2 = cls._get_full_image_path(image_path2)
        
        # Instant Exact Byte/File Match Check
        if p1 and p2 and p1.exists() and p2.exists():
            try:
                b1 = p1.read_bytes()
                b2 = p2.read_bytes()
                if b1 == b2:
                    return 1.0, "Exact identical image uploaded (100% visual match). High-confidence asset signature verified."
            except Exception:
                pass
        
        # Dynamic Hash Recovery if hashes were None or missing
        img1 = None
        img2 = None
        if p1 and p2 and (not hash1 or not hash2):
            try:
                img1 = Image.open(p1)
                img2 = Image.open(p2)
                if not hash1 and img1:
                    from ..utils.image_helpers import compute_dhash
                    hash1 = compute_dhash(img1)
                if not hash2 and img2:
                    from ..utils.image_helpers import compute_dhash
                    hash2 = compute_dhash(img2)
            except Exception:
                pass

        # Hash similarity
        dhash_sim = hash_similarity(hash1 or "", hash2 or "")
        
        # Color histogram similarity
        col_sim = 0.5
        if p1 and p2:
            try:
                if img1 is None:
                    img1 = Image.open(p1)
                if img2 is None:
                    img2 = Image.open(p2)
                hist1 = compute_color_histogram(img1)
                hist2 = compute_color_histogram(img2)
                col_sim = color_similarity(hist1, hist2)
            except Exception:
                pass
                
        # If hashes match exactly
        if dhash_sim >= 0.98 or (hash1 and hash2 and hash1.strip().lower() == hash2.strip().lower()):
            score = 1.0
            explanation = "Visual Correspondence: 100% (Identical perceptual hash and visual signature detected)."
            return score, explanation

        # Weighted local score
        score = dhash_sim * 0.65 + col_sim * 0.35
        
        # High confidence boost for strong structural similarity
        if dhash_sim >= 0.85:
            score = max(score, dhash_sim)
            
        score = round(max(0.0, min(1.0, score)), 4)
        explanation = (
            f"Local CV Analysis: Structural feature similarity {int(dhash_sim * 100)}%, "
            f"Color palette similarity {int(col_sim * 100)}%."
        )
        return score, explanation

    @classmethod
    def gemini_match(
        cls,
        image_path1: str,
        hash1: Optional[str],
        image_path2: str,
        hash2: Optional[str],
        api_key: str
    ) -> Tuple[float, str]:
        """Multimodal image comparison using Google Gemini."""
        try:
            p1 = cls._get_full_image_path(image_path1)
            p2 = cls._get_full_image_path(image_path2)
            
            if not p1 or not p2:
                return cls.local_match(image_path1, hash1, image_path2, hash2)
                
            # Fast path: check identical files before API call
            if p1.read_bytes() == p2.read_bytes():
                return 1.0, "Exact identical image uploaded (100% visual match confirmed)."

            img1 = Image.open(p1)
            img2 = Image.open(p2)
            
            client = genai.Client(api_key=api_key)
            prompt = """Analyze these two images. Image 1 is a reported LOST item, Image 2 is a reported FOUND item.
Evaluate if these two images could show the exact same object or identical model.
Inspect:
1. Object type, silhouette, model, shape.
2. Color, texture, material.
3. Identifying marks, wear, scratches, stickers, logos, attachments.

Return ONLY a JSON object in this exact format:
{
  "visual_similarity": 0.88,
  "visual_reasoning": "Both photos display the exact same item model and color with identical visual characteristics."
}
visual_similarity must be between 0.0 and 1.0."""

            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=[prompt, img1, img2]
            )
            
            raw = (response.text or "").strip()
            if "```" in raw:
                raw = re.sub(r'```json\s*|\s*```', '', raw).strip()
            data = json.loads(raw)
            score = float(data.get("visual_similarity", 0.5))
            reasoning = str(data.get("visual_reasoning", "Gemini vision analysis completed."))
            return round(max(0.0, min(1.0, score)), 4), reasoning
            
        except Exception:
            # Graceful fallback to local matching preserving hashes
            return cls.local_match(image_path1, hash1, image_path2, hash2)

    @classmethod
    def match(
        cls,
        image_path1: Optional[str], hash1: Optional[str],
        image_path2: Optional[str], hash2: Optional[str],
        api_key: Optional[str] = None
    ) -> Tuple[float, str]:
        active_key = api_key or settings.GEMINI_API_KEY
        if active_key and image_path1 and image_path2:
            return cls.gemini_match(image_path1, hash1, image_path2, hash2, active_key)
        return cls.local_match(image_path1, hash1, image_path2, hash2)
