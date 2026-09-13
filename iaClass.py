import os
import json
import mimetypes
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class iaClass:
    SYSTEM_INSTRUCTION = """
Eres un experto en extracción de datos de documentos contables y procesamiento de facturas (OCR + NLP). 

Tu tarea es analizar la factura de proveedor adjunta y extraer toda la información estructurada, devolviendo ÚNICAMENTE un objeto JSON válido, sin ningún texto adicional, explicaciones ni formato Markdown fuera del bloque de código.

Sigue estrictamente las siguientes reglas de extracción:
1. Extrae los datos del encabezado/pie de la factura y la lista detallada de elementos (ítems).
2. Si un dato no está presente en la factura, asigna el valor null (o un arreglo vacío [] en el caso de las líneas de detalle).
3. Asegúrate de formatear las fechas en formato ISO (YYYY-MM-DD).
4. Convierte todos los valores numéricos de montos, impuestos y cantidades a tipo Number (no String), eliminando símbolos de moneda y separadores de miles.
5. El resultado final debe ser un JSON estrictamente válido.

Estructura del JSON a retornar:

{
  "data_invoice": {
    "proveedor": {
      "nombre": string | null,
      "nit": string | null,
      "direccion": string | null,
      "telefono": string | null,
      "email": string | null
    },
    "factura": {
      "numero_factura": string | null,
      "fecha_emision": string | null,
      "fecha_vencimiento": string | null,
      "moneda": string | null,
      "metodo_pago": string | null,
      "orden_compra": string | null
    },
    "totales": {
      "subtotal": number | null,
      "impuestos": number | null,
      "descuento": number | null,
      "porcentaje_descuento": number | null,
      "total": number | null
    }
  },
  "items": [
    {
      "codigo": string | null,
      "descripcion": string | null,
      "cantidad": number | null,
      "precio_unitario": number | null,
      "descuento": number | null,
      "impuesto_porcentaje": number | null,
      "total_linea": number | null
    }
  ]
}
"""
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv(""
        ""
        "")
        if not self.api_key:
            raise ValueError("API key is required. Please set the GENAI_API_KEY environment variable or provide it as an argument.")
        self.client = genai.Client(api_key=self.api_key)

    def extract_invoice_data(self, invoice_file_path: str, model: str = "gemini-3.1-flash-lite") -> Dict[str, Any]:
        """
        Extracts structured data from an invoice PDF file using Google GenAI.

        Args:
            invoice_file_path (str): The path to the invoice PDF file.

        Returns:
            Dict[str, Any]: A dictionary containing the extracted invoice data.
        """
        with open(invoice_file_path, "rb") as f:
            invoice_content = f.read()


        #print(f"Extracting data from invoice: {invoice_file_path} using model: {model}")    

        config = types.GenerateContentConfig(
           system_instruction=self.SYSTEM_INSTRUCTION,
           response_mime_type="application/json",
           temperature=0.0,
           max_output_tokens=65536
           )
        
        mime_type = mimetypes.guess_type(invoice_file_path)[0] or "application/octet-stream"
        response = self.client.models.generate_content(
          model=model,
          contents=[
           "Extrae la información estructurada de este documento contable.",
            types.Part.from_bytes(data=invoice_content, mime_type=mime_type),
          ],
          config=config
        )

        if not response.text:
          raise ValueError("La IA no devolvió datos para la factura.")

        extracted_data = json.loads(response.text)
        if not isinstance(extracted_data, dict):
          raise ValueError("La IA devolvió un formato de datos inválido.")
        
        #print(f"Extracted data: {extracted_data}") 
        return extracted_data