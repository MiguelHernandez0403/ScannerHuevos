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

Ejemplo conceptual:

```text
Imagen
   │
   ▼
YOLO
   │
   ├── Clase detectada
   ├── Confianza
   └── Coordenadas
          │
          ▼
       JSON
```

---

# ☁️ Despliegue en AWS

El backend y el modelo de IA se ejecutan en una instancia **AWS EC2**.

La estructura del servidor puede ser:

```text
AWS EC2
│
└── proyecto/
    │
    ├── app.py
    ├── best.pt
    ├── requirements.txt
    └── venv/
```

Para acceder al servidor mediante SSH:

```bash
ssh -i "EggScanner.pem" ubuntu@<AWS_PUBLIC_IP>
```

---

## 🐍 Configuración del entorno

Crear un entorno virtual:

```bash
python3 -m venv venv
```

Activarlo:

```bash
source venv/bin/activate
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

Ejemplo de `requirements.txt`:

```text
fastapi
uvicorn
python-multipart
ultralytics
torch
opencv-python
pillow
```

---

# ▶️ Ejecutar el backend

Con el entorno virtual activado:

```bash
uvicorn app:app --host 0.0.0.0 --port 8080
```

El servidor quedará disponible mediante:

```text
http://<AWS_PUBLIC_IP>:8080
```

Y el endpoint de predicción:

```text
http://<AWS_PUBLIC_IP>:8080/predict/
```

---

# 📡 Comunicación entre la aplicación y AWS

La aplicación móvil debe conocer la dirección pública de la API.

Por ejemplo:

```javascript
const API_URL = "http://<AWS_PUBLIC_IP>:8080";
```

Para enviar una imagen:

```javascript
const formData = new FormData();

formData.append("file", {
  uri: imageUri,
  name: "egg.jpg",
  type: "image/jpeg",
});

const response = await fetch(`${API_URL}/predict/`, {
  method: "POST",
  body: formData,
});

const result = await response.json();
```

La respuesta recibida puede utilizarse para mostrar el resultado al usuario.

---

# 📦 Ejemplo de respuesta

La estructura exacta dependerá de cómo se haya implementado el backend. Un ejemplo podría ser:

```json
{
  "success": true,
  "detections": [
    {
      "class": "egg",
      "confidence": 0.94,
      "bbox": [
        120,
        80,
        450,
        380
      ]
    }
  ]
}
```

La aplicación móvil puede utilizar esta información para mostrar:

```text
Resultado del análisis

🥚 Objeto: Huevo
📊 Confianza: 94%
```

---

# 🔐 Seguridad

Para un entorno de desarrollo se puede utilizar HTTP directamente.

Sin embargo, para producción se recomienda:

- Utilizar **HTTPS**.
- Configurar un dominio.
- Utilizar un reverse proxy como Nginx.
- Restringir los puertos de AWS mediante Security Groups.
- Evitar almacenar credenciales directamente en el código.
- Utilizar variables de entorno para configuraciones sensibles.
- Implementar autenticación para la API si es necesario.
- Limitar el tamaño de las imágenes enviadas.

---

# ⚠️ Consideraciones

La aplicación móvil **no ejecuta directamente el modelo de IA**.

El procesamiento se realiza en el servidor:

```text
📱 Smartphone
     │
     │ Imagen
     ▼
🌐 API
     │
     ▼
☁️ AWS EC2
     │
     ▼
🤖 YOLO
     │
     ▼
📊 Resultado
     │
     ▼
📱 Smartphone
```

Esto permite mantener el modelo en el servidor y evitar incluirlo directamente dentro de la aplicación móvil.

---

# 🔄 Flujo completo del sistema

```text
1. Usuario abre la aplicación
             ↓
2. Selecciona o captura una imagen
             ↓
3. La aplicación prepara la imagen
             ↓
4. Se envía mediante POST /predict/
             ↓
5. AWS recibe la imagen
             ↓
6. FastAPI procesa la solicitud
             ↓
7. YOLO analiza la imagen
             ↓
8. Se generan las predicciones
             ↓
9. FastAPI construye la respuesta JSON
             ↓
10. La aplicación recibe el resultado
             ↓
11. Se muestra el resultado al usuario
```

---

# 🧪 Pruebas

Antes de conectar la aplicación móvil, se recomienda comprobar que la API funciona correctamente desde el servidor.

Ejemplo:

```bash
curl -X POST \
  -F "file=@huevo-test.jpg" \
  http://localhost:8080/predict/
```

También se puede probar utilizando la dirección pública de AWS:

```bash
curl -X POST \
  -F "file=@huevo-test.jpg" \
  http://<AWS_PUBLIC_IP>:8080/predict/
```

Si la API devuelve correctamente el resultado, se puede proceder a conectar la aplicación móvil.

---

# 🐛 Problemas comunes

### Puerto 8080 ocupado

Si aparece:

```text
[Errno 98] Address already in use
```

significa que otro proceso ya está utilizando el puerto `8080`.

Se puede identificar el proceso con:

```bash
sudo lsof -i :8080
```

Y posteriormente detenerlo si corresponde.

---

### La aplicación no puede conectarse a AWS

Comprobar:

1. Que la instancia EC2 esté ejecutándose.
2. Que la API esté ejecutándose.
3. Que el puerto `8080` esté permitido en el Security Group.
4. Que la dirección IP pública sea correcta.
5. Que la aplicación esté utilizando la URL correcta.

---

# 📌 Estado del proyecto

| Componente | Estado |
|---|---|
| Modelo YOLO | ✅ |
| Entrenamiento del modelo | ✅ |
| Backend FastAPI | ✅ |
| API de predicción | ✅ |
| AWS EC2 | ✅ |
| Aplicación Expo | 🚧 |
| Integración App ↔ API | 🚧 |
| Pruebas finales | 🚧 |

---

# 👨‍💻 Autores

Proyecto desarrollado como parte de un proyecto académico de **Inteligencia Artificial y desarrollo de aplicaciones móviles**.

---

# 📄 Licencia

Este proyecto está destinado principalmente a fines académicos y de aprendizaje.

La licencia puede modificarse según los requerimientos del proyecto.
