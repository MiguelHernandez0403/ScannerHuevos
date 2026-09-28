# 🥚 Egg Scanner AI

Aplicación móvil para el **reconocimiento y análisis de huevos mediante Inteligencia Artificial**. El proyecto utiliza una aplicación móvil desarrollada con **Expo Go / React Native**, que se comunica mediante una **API REST** con un servidor alojado en **AWS**, donde se encuentra desplegado el modelo de Inteligencia Artificial encargado del análisis de las imágenes.

## 📋 Descripción

**Egg Scanner AI** permite al usuario capturar o seleccionar una imagen de un huevo desde un dispositivo móvil y enviarla al servidor para que sea procesada por un modelo de IA.

El flujo general del sistema es:

```text
┌─────────────────────┐
│    📱 App móvil     │
│   Expo / React      │
└──────────┬──────────┘
           │
           │ HTTP POST
           │ Imagen
           ▼
┌─────────────────────┐
│      🌐 API REST    │
│   FastAPI / Python  │
└──────────┬──────────┘
           │
           │ Procesamiento
           ▼
┌─────────────────────┐
│     ☁️ AWS EC2      │
│                     │
│   Modelo YOLO       │
│      best.pt        │
└──────────┬──────────┘
           │
           │ Predicción
           ▼
┌─────────────────────┐
│  Resultado JSON     │
│                     │
│ Clase / confianza   │
│ detecciones, etc.   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    📱 App móvil     │
│ Mostrar resultado   │
└─────────────────────┘
```

---

## 🚀 Características

- 📷 Captura de imágenes desde el dispositivo móvil.
- 🖼️ Selección de imágenes desde la galería.
- 🤖 Procesamiento mediante un modelo de Inteligencia Artificial.
- 🥚 Detección y clasificación de huevos.
- ☁️ Modelo desplegado en AWS.
- 🌐 Comunicación entre la aplicación y el servidor mediante una API REST.
- 📊 Retorno de resultados mediante JSON.
- 📱 Aplicación multiplataforma mediante React Native y Expo.

---

## 🛠️ Tecnologías utilizadas

### Aplicación móvil

- **React Native**
- **Expo**
- **Expo Go**
- JavaScript / TypeScript
- Expo Image Picker / Camera

### Backend

- **Python**
- **FastAPI**
- **Uvicorn**
- REST API
- Multipart/Form-Data

### Inteligencia Artificial

- **YOLO**
- **Ultralytics**
- PyTorch
- Modelo entrenado `best.pt`

### Infraestructura

- **AWS EC2**
- Ubuntu Server
- Python Virtual Environment
- HTTP/HTTPS

---

## 📁 Estructura del proyecto

Una posible estructura del proyecto es:

```text
EggScannerAI/
│
├── mobile/
│   ├── app/
│   ├── assets/
│   ├── components/
│   ├── services/
│   ├── package.json
│   └── app.json
│
├── backend/
│   ├── app.py
│   ├── best.pt
│   ├── requirements.txt
│   └── venv/
│
├── README.md
└── .gitignore
```

> El modelo `best.pt` puede mantenerse fuera del repositorio si su tamaño es considerable. En producción, el modelo debe encontrarse en el servidor AWS o en un servicio de almacenamiento como Amazon S3.

---

# 📱 Aplicación móvil

La aplicación móvil está desarrollada utilizando **React Native con Expo**.

Expo permite desarrollar y probar la aplicación rápidamente en dispositivos móviles utilizando **Expo Go**.

### Instalación

Primero se deben instalar las dependencias:

```bash
cd mobile
npm install
```

Luego iniciar el proyecto:

```bash
npx expo start
```

Después se puede abrir la aplicación utilizando **Expo Go** en un dispositivo móvil compatible.

---

# 🌐 API

La aplicación móvil se comunica con el backend mediante una API REST.

El endpoint principal utilizado para realizar una predicción es:

```http
POST /predict/
```

La imagen se envía utilizando `multipart/form-data`.

### Ejemplo de solicitud

```bash
curl -X POST \
  -F "file=@huevo-test.jpg" \
  http://<AWS_SERVER>:8080/predict/
```

En Windows PowerShell puede ser necesario utilizar `curl.exe` en lugar de `curl`:

```powershell
curl.exe -X POST `
  -F "file=@huevo-test.jpg" `
  http://<AWS_SERVER>:8080/predict/
```

---

# 🧠 Modelo de Inteligencia Artificial

El sistema utiliza un modelo de **YOLO (You Only Look Once)** entrenado para reconocer las características definidas para el proyecto.

El modelo entrenado se encuentra representado por:

```text
best.pt
```

Durante una predicción, el servidor:

1. Recibe la imagen.
2. Carga/procesa la imagen.
3. Ejecuta el modelo YOLO.
4. Obtiene las detecciones.
5. Procesa los resultados.
6. Devuelve la información a la aplicación móvil.
