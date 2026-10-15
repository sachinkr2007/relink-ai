# ⚡ ReLink AI — Multimodal Lost & Found Asset Recovery Platform

> **Advanced AI-driven platform that automatically cross-references lost and found items via Computer Vision (dHash + HSV Color Histograms + Gemini Multimodal Vision), Semantic Natural Language Processing, and Geospatial GPS Proximity.**

ReLink AI is a production-grade, multimodal asset recovery and reunion platform. It cross-references lost item reports with found item reports using an intelligent **Tri-Factor AI Matching Engine with Visual Primacy**:
1. **Multimodal Visual Inspection (40% - 100% Adaptive Primacy)**: Exact byte verification + Local Perceptual Hashing (dHash) & HSV Color Histograms + Google Gemini 2.0 Flash Vision.
2. **Semantic Description Understanding (35% Weight)**: Deep NLP semantic reasoning + Category strictness, brand detection, and keyword token matching.
3. **Geospatial Proximity Calculation (25% Weight)**: High-precision Haversine distance decay formula + Landmark/venue name matching with native browser GPS auto-detection.

---

## 🌟 Key Features

- **Visual Primacy Matching**: Identical or high-similarity photos are immediately recognized and given top match priority (95%+ match score).
- **100% Clean & Production Ready**: Starts with a fresh database (`0 Lost, 0 Found`), ready for real-world user submissions.
- **Native GPS Auto-Detection**: Uses HTML5 Geolocation (`📍 Detect My Location`) to capture precise GPS coordinates without any external map tile API keys or broken map tiles.
- **Tri-Factor Composite Scoring**: Calculates a weighted similarity score $[0\% - 100\%]$ and provides transparent reasoning for every candidate pair.
- **Side-by-Side Match Inspection**: Compare photos, descriptions, timestamps, and exact distance in meters/kilometers.
- **Anti-Fraud Ownership Claims**: Generates dynamic verification challenge questions (e.g., hidden marks, lockscreen images, pouch contents) to ensure only the true owner can claim.

---

## 🚀 Local Run (VS Code / Terminal)

```bash
# Install dependencies
pip install -r requirements.txt

# Start the application
python run.py
```

Open in browser: **http://127.0.0.1:8000** or **http://localhost:8000**

---

## ☁️ How to Deploy (Deployment Guide)

### Option 1: Deploy on Render.com (Recommended & Free)
1. Push this folder to a GitHub repository.
2. Go to [Render.com](https://render.com) and click **New Web Service**.
3. Connect your GitHub repository.
4. Render will automatically detect `render.yaml` or use these settings:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`
5. *(Optional)* Add Environment Variable:
   - `GEMINI_API_KEY`: Your Gemini API Key from [Google AI Studio](https://aistudio.google.com/)
6. Click **Deploy**. Your app will be live at `https://your-app-name.onrender.com`!

---

### Option 2: Deploy on Railway.app
1. Push this folder to GitHub.
2. Go to [Railway.app](https://railway.app) and select **New Project** -> **Deploy from GitHub repo**.
3. Railway automatically detects `Procfile` / `Dockerfile` and deploys your service.
4. Add `GEMINI_API_KEY` in the Variables tab.

---

### Option 3: Deploy with Docker
```bash
# Build Docker image
docker build -t relink-ai .

# Run Docker container
docker run -p 8000:8000 -e GEMINI_API_KEY="your_api_key_here" relink-ai
```
Access at `http://localhost:8000`.

---

## 📡 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `GET /api/health` | GET | Health check and engine status |
| `POST /api/items/lost` | POST | Submit lost item report with image & GPS |
| `POST /api/items/found` | POST | Submit found item report with custody location |
| `GET /api/items` | GET | List and filter items (by type, category, search) |
| `GET /api/items/{id}` | GET | Get item details and its top matches |
| `GET /api/matches` | GET | Get ranked AI matches with score breakdown |
| `POST /api/ai/analyze-image` | POST | Auto-extract details from photo with Gemini |
| `POST /api/ai/generate-claim-questions` | POST | Generate anti-fraud challenge questions |
| `POST /api/claims` | POST | File an ownership claim |
| `PATCH /api/claims/{id}/approve` | PATCH | Approve claim & mark items as Reunited |
| `GET /api/claims/stats/summary` | GET | Dashboard metrics summary |

---

## 🧪 Testing

```bash
python tests/test_matching.py      # Math & Computer Vision tests
python tests/verify_endpoints.py    # Production lifecycle integration tests
```
