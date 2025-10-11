/**
 * Google Sheets Apps Script para Bot People
 * 
 * Instrucciones de uso:
 * 1. Abrir Google Sheet
 * 2. Ir a Extensiones → Apps Script
 * 3. Copiar y pegar este código completo
 * 4. IMPORTANTE: Cambiar la URL en la línea del 'const url' 
 *    a tu servidor de producción antes de guardar
 * 5. Guarda y autoriza el script
 */

function onEdit(e) {
  const range = e.range;
  const sheet = range.getSheet();

  // Verifico que sea la hoja que me interesa
  if (sheet.getName() !== "Hoja 1") return;

  const row = range.getRow();
  const col = range.getColumn();

  // Verifico si se editó la columna del checkbox (columna 1 = A)
  if (col === 1 && e.value === "TRUE") {
    // Obtengo el valor del checkbox y el DNI (columna 4)
    const checkboxValue = sheet.getRange(row, 1).getValue(); // Columna A
    const dniValue = sheet.getRange(row, 4).getValue();      // Columna D

    Logger.log(checkboxValue,"-", dniValue);

    // Envío esta info a mi backend en Python
    const url = "https://0fe582fd9261.ngrok-free.app/autorizados";
    const payload = {
      row: row,
      autorizado: checkboxValue,
      dni_autorizado: dniValue
    };

    UrlFetchApp.fetch(url, {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload)
    });
    Logger.log("Mande los datos al back");
  }
}
