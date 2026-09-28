#!/usr/bin/env python3
# app.py -- FastAPI + YOLOv8 para detección de huevos rotos/buenos
# Requiere: fastapi uvicorn ultralytics opencv-python-headless pillow numpy python-multipart

import os
import logging
import base64
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import cv2
import numpy as np

# -------------------------
# Config / Logging
# -------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yolo-eggs")

MODEL_PATH = os.getenv("MODEL_PATH", "best.pt")
CONF_THRESH = float(os.getenv("CONF_THRESH", 0.25))
IMG_SIZE = 640
RETURN_IMAGE = True

# Class names: 0 = bueno, 1 = roto (ajustar según tu modelo)
CLASS_NAMES = {0: "roto", 1: "bueno"}

# -------------------------
# App init
# -------------------------
app = FastAPI(title="YOLOv8 - Detector de Huevos (Rotos/Bueno)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Cargar modelo
# -------------------------
logger.info("🔹 Cargando modelo YOLOv8 desde %s ...", MODEL_PATH)
try:
    model = YOLO(MODEL_PATH, task="detect")
    logger.info("✅ Modelo YOLOv8 cargado correctamente.")
    logger.info("📋 Clases del modelo: %s", model.names)
except Exception as e:
    logger.error("❌ Error cargando modelo: %s", e)
    model = None

# -------------------------
# Helpers
# -------------------------
def resize_to_square(img: np.ndarray, size: int = 640) -> tuple:
    """
    Redimensiona imagen a size x size manteniendo aspect ratio con padding.
    Devuelve: (imagen_redimensionada, metadatos_de_scaling)
    """
    h, w = img.shape[:2]
    scale = size / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    
    # Crear canvas cuadrado con padding negro
    canvas = np.zeros((size, size, 3), dtype=np.uint8)
    x_offset = (size - new_w) // 2
    y_offset = (size - new_h) // 2
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    
    scaling_info = {
        "original_size": (w, h),
        "resized_size": (new_w, new_h),
        "scale_factor": round(scale, 4),
        "padding": (x_offset, y_offset),
        "target_size": size
    }
    
    return canvas, scaling_info


def image_to_base64_jpg(img_bgr: np.ndarray) -> str:
    """Convierte imagen BGR a base64 (JPG)."""
    _, buffer = cv2.imencode('.jpg', img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    return base64.b64encode(buffer).decode('utf-8')


def process_predictions(results, frame_shape) -> dict:
    """
    Procesa resultados de YOLO y devuelve clasificación de huevos detectados.
    
    Retorna:
        - huevos: Lista de detecciones con bbox, confianza, clase
        - total: Total de huevos detectados
        - buenos: Cantidad de huevos clasificados como buenos
        - rotos: Cantidad de huevos clasificados como rotos
    """
    if not results or len(results) == 0:
        return {"huevos": [], "total": 0, "buenos": 0, "rotos": 0}
    
    r = results[0]
    boxes = r.boxes.xyxy.cpu().numpy() if len(r.boxes) > 0 else np.array([])
    confs = r.boxes.conf.cpu().numpy() if len(r.boxes) > 0 else np.array([])
    clss = r.boxes.cls.cpu().numpy() if len(r.boxes) > 0 else np.array([])
    
    huevos = []
    buenos = 0
    rotos = 0
    
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box)
        cls_id = int(clss[i]) if len(clss) > i else -1
        conf = float(confs[i]) if len(confs) > i else 0.0
        
        # Obtener label desde CLASS_NAMES (0=bueno, 1=roto)
        label = CLASS_NAMES.get(cls_id, f"desconocido_{cls_id}")
        
        if label == "bueno":
            buenos += 1
        elif label == "roto":
            rotos += 1
        
        huevos.append({
            "bbox": [x1, y1, x2, y2],
            "confidence": round(conf, 4),
            "class_id": cls_id,
            "label": label
        })
    
    return {
        "huevos": huevos,
        "total": len(huevos),
        "buenos": buenos,
        "rotos": rotos
    }


def draw_detections(frame: np.ndarray, predictions: dict) -> np.ndarray:
    """Dibuja las detecciones sobre la imagen."""
    img = frame.copy()
    for huevo in predictions["huevos"]:
        x1, y1, x2, y2 = huevo["bbox"]
        label = huevo["label"]
        conf = huevo["confidence"]
        
        color = (0, 255, 0) if label == "bueno" else (0, 0, 255)
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(img, f"{label} {conf:.2f}", (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return img


# -------------------------
# Rutas
# -------------------------
@app.get("/")
def home():
    return {
        "message": "YOLOv8 Egg Detector API running",
        "model_loaded": model is not None,
        "classes": CLASS_NAMES
    }


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict/")
async def predict(
    file: Optional[UploadFile] = File(None),
    image_base64: Optional[str] = Form(None)
):
    """
    Recibe una imagen (multipart o base64) y devuelve clasificación de huevos.
    
    Respuesta:
    {
        "success": true,
        "image_info": {
            "original_size": [w, h],
            "resized_to": 640,
            "scale_factor": 0.5
        },
        "clasificacion": {
            "total": 5,
            "buenos": 3,
            "rotos": 2
        },
        "detecciones": [
            {"bbox": [x1, y1, x2, y2], "label": "bueno", "confianza": 0.95},
            ...
        ],
        "image": "base64_anotada",  # si RETURN_IMAGE=True
        "message": "OK"
    }
    """
    if model is None:
        return {"error": "Modelo no cargado"}
    
    try:
        logger.info("📩 Petición POST /predict/ recibida")
        
        # Leer imagen desde form-data o base64
        if file:
            contents = await file.read()
            nparr = np.frombuffer(contents, np.uint8)
        elif image_base64:
            if image_base64.startswith("data:image"):
                image_base64 = image_base64.split(",")[1]
            image_base64 = image_base64.strip()
            try:
                img_data = base64.b64decode(image_base64 + "===")
            except Exception as e:
                logger.error("❌ Base64 inválido: %s", e)
                return {"success": False, "error": "Base64 inválido o corrupto"}
            nparr = np.frombuffer(img_data, np.uint8)
        else:
            return {"success": False, "error": "No se recibió imagen (file o image_base64)"}
        
        # Decodificar imagen
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return {"success": False, "error": "No se pudo decodificar la imagen"}
        
        # ⚠️ GARANTIZADO: Redimensionar SIEMPRE a 640x640
        frame_resized, scaling_info = resize_to_square(frame, IMG_SIZE)
        logger.info(f"📐 Imagen redimensionada a {IMG_SIZE}x{IMG_SIZE} | Original: {scaling_info['original_size']}")
        
        # Enviar al modelo en 640x640
        logger.info(f"🧠 Procesando con YOLOv8 en {IMG_SIZE}x{IMG_SIZE}...")
        results = model.predict(source=frame_resized, conf=CONF_THRESH, verbose=False, imgsz=IMG_SIZE)
        
        predictions = process_predictions(results, frame_resized.shape)
        
        # Dibujar detecciones si se requiere
        img_b64 = None
        if RETURN_IMAGE:
            annotated = draw_detections(frame_resized, predictions)
            img_b64 = image_to_base64_jpg(annotated)
        
        logger.info(f"✅ Resultado: {predictions['total']} huevos ({predictions['buenos']} buenos, {predictions['rotos']} rotos)")
        
        return {
            "success": True,
            "image_info": {
                "original_size": list(scaling_info["original_size"]),
                "resized_to": IMG_SIZE,
                "scale_factor": scaling_info["scale_factor"]
            },
            "clasificacion": {
                "total": predictions["total"],
                "buenos": predictions["buenos"],
                "rotos": predictions["rotos"]
            },
            "detecciones": predictions["huevos"],
            "image_anotada": img_b64,
            "message": "OK" if predictions["total"] > 0 else "No se detectaron huevos"
        }
    
    except Exception as e:
        logger.exception(f"❌ Error en /predict/: {e}")
        return {"success": False, "error": str(e)}


@app.post("/predict_json/")
async def predict_json(request: Request):
    """
    Recibe imagen como JSON con campo 'image_base64'.
    Misma respuesta que /predict/
    """
    if model is None:
        return {"success": False, "error": "Modelo no cargado"}
    
    try:
        body = await request.json()
        image_base64 = body.get("image_base64")
        if not image_base64:
            return {"success": False, "error": "Campo 'image_base64' requerido"}
        
        if image_base64.startswith("data:image"):
            image_base64 = image_base64.split(",")[1]
        image_base64 = image_base64.strip()
        
        try:
            img_data = base64.b64decode(image_base64 + "===")
        except Exception as e:
            logger.error(f"❌ Base64 inválido: {e}")
            return {"success": False, "error": "Base64 inválido o corrupto"}
        
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return {"success": False, "error": "No se pudo decodificar la imagen"}
        
        logger.info("📩 Petición POST /predict_json/ recibida")
        
        # ⚠️ GARANTIZADO: Redimensionar SIEMPRE a 640x640
        frame_resized, scaling_info = resize_to_square(frame, IMG_SIZE)
        logger.info(f"📐 Imagen redimensionada a {IMG_SIZE}x{IMG_SIZE} | Original: {scaling_info['original_size']}")
        
        # Enviar al modelo en 640x640
        logger.info(f"🧠 Procesando con YOLOv8 en {IMG_SIZE}x{IMG_SIZE}...")
        results = model.predict(source=frame_resized, conf=CONF_THRESH, verbose=False, imgsz=IMG_SIZE)
        predictions = process_predictions(results, frame_resized.shape)
        
        img_b64 = None
        if RETURN_IMAGE:
            annotated = draw_detections(frame_resized, predictions)
            img_b64 = image_to_base64_jpg(annotated)
        
        logger.info(f"✅ Resultado: {predictions['total']} huevos ({predictions['buenos']} buenos, {predictions['rotos']} rotos)")
        
        return {
            "success": True,
            "image_info": {
                "original_size": list(scaling_info["original_size"]),
                "resized_to": IMG_SIZE,
                "scale_factor": scaling_info["scale_factor"]
            },
            "clasificacion": {
                "total": predictions["total"],
                "buenos": predictions["buenos"],
                "rotos": predictions["rotos"]
            },
            "detecciones": predictions["huevos"],
            "image_anotada": img_b64,
            "message": "OK" if predictions["total"] > 0 else "No se detectaron huevos"
        }
    
    except Exception as e:
        logger.exception(f"❌ Error en /predict_json/: {e}")
        return {"success": False, "error": str(e)}


# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    logger.info("🚀 Iniciando servidor en 0.0.0.0:%s", port)
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)