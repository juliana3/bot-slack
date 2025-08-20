async function loadModels() {
  // Cargar modelos de detección facial
  await faceapi.nets.tinyFaceDetector.loadFromUri('/models');
  await faceapi.nets.faceLandmark68Net.loadFromUri('/models');
}

loadModels();

document.getElementById("dni_frente").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const img = await faceapi.bufferToImage(file);
  const canvas = document.getElementById("preview");
  const ctx = canvas.getContext("2d");

  canvas.width = img.width;
  canvas.height = img.height;
  ctx.drawImage(img, 0, 0);

  // Detectar rostro
  const detections = await faceapi
    .detectSingleFace(img, new faceapi.TinyFaceDetectorOptions())
    .withFaceLandmarks();

  if (!detections) {
    alert("No se detectó una cara en la foto.");
    event.target.value = "";
    return;
  }

  // Calcular inclinación con los ojos
  const leftEye = detections.landmarks.getLeftEye();
  const rightEye = detections.landmarks.getRightEye();

  const dx = rightEye[0].x - leftEye[0].x;
  const dy = rightEye[0].y - leftEye[0].y;
  const angle = Math.atan2(dy, dx) * 180 / Math.PI;

  if (Math.abs(angle) > 15) {
    alert("Tu cara está inclinada. Por favor subí una foto vertical, de frente.");
    event.target.value = "";
  } else {
    alert("✅ Foto aceptada, la cara está bien orientada.");
  }
});