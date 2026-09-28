import { useState, useRef, useEffect, useCallback } from "react";
import { StyleSheet, Text, View } from "react-native";
import { CameraView, useCameraPermissions } from "expo-camera";

const API_URL = "http://ec2-52-20-213-89.compute-1.amazonaws.com:8080/predict_json/";
const REFERENCE_FPS = 60;
const FRAMES_PER_CAPTURE = 30;
const CAPTURE_INTERVAL_MS = (FRAMES_PER_CAPTURE / REFERENCE_FPS) * 1000;

interface Deteccion {
  bbox: number[];
  confidence: number;
  class_id: number;
  label: string; // "bueno" | "roto"
}

interface PredictResponse {
  success: boolean;
  clasificacion?: {
    total: number;
    buenos: number;
    rotos: number;
  };
  detecciones?: Deteccion[];
  message?: string;
  error?: string;
}

export default function Index() {
  const [permission, requestPermission] = useCameraPermissions();
  const cameraRef = useRef<CameraView>(null);
  const isBusyRef = useRef(false);

  const [isCameraReady, setIsCameraReady] = useState(false);
  const [detection, setDetection] = useState<string | null>(null);

  useEffect(() => {
    if (!permission) return;
    if (!permission.granted) requestPermission();
  }, [permission]);

  const captureAndPredict = useCallback(async () => {
    if (!cameraRef.current || isBusyRef.current || !isCameraReady) return;

    isBusyRef.current = true;
    try {
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.4,
        base64: true,
      });

      if (!photo?.base64) return;

      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          image_base64: photo.base64, // nombre exacto que espera tu API
        }),
      });

      if (!response.ok) throw new Error(`Respuesta HTTP ${response.status}`);

      const result: PredictResponse = await response.json();

      if (!result.success || !result.clasificacion || result.clasificacion.total === 0) {
        setDetection(null);
        return;
      }

      const { buenos, rotos, total } = result.clasificacion;

      // Mensaje según lo detectado. Ajusta el texto a tu gusto.
      if (rotos > 0 && buenos === 0) {
        setDetection(`⚠️ Huevo ROTO detectado (${rotos})`);
      } else if (buenos > 0 && rotos === 0) {
        setDetection(`✅ Huevo BUENO detectado (${buenos})`);
      } else {
        setDetection(`Detectados: ${buenos} buenos, ${rotos} rotos (total ${total})`);
      }
    } catch (err: any) {
      console.log("Error en la predicción:", err.message);
    } finally {
      isBusyRef.current = false;
    }
  }, [isCameraReady]);

  useEffect(() => {
    if (!permission?.granted || !isCameraReady) return;

    const intervalId = setInterval(captureAndPredict, CAPTURE_INTERVAL_MS);
    return () => clearInterval(intervalId);
  }, [permission, isCameraReady, captureAndPredict]);

  if (!permission) return <View style={styles.container} />;

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={styles.infoText}>
          Necesitamos acceso a la cámara para continuar.
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <CameraView
        ref={cameraRef}
        style={StyleSheet.absoluteFill}
        facing="back"
        onCameraReady={() => setIsCameraReady(true)}
      />

      {detection && (
        <View style={styles.overlay}>
          <Text style={styles.overlayText}>{detection}</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "black" },
  infoText: { color: "white", textAlign: "center", marginTop: 40 },
  overlay: {
    position: "absolute",
    bottom: 60,
    alignSelf: "center",
    backgroundColor: "rgba(0,0,0,0.75)",
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 12,
  },
  overlayText: { color: "white", fontSize: 18, fontWeight: "bold" },
});