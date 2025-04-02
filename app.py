from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from docxtpl import DocxTemplate
import os
import tempfile
import json
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Configuración más específica de CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "https://*.vercel.app"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Accept"],
        "supports_credentials": True
    }
})

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return jsonify({
        'message': 'API is running',
        'endpoints': {
            'upload': '/api/upload',
            'generate-pdf': '/api/generate-pdf'
        }
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    logger.info("Iniciando proceso de carga de archivo")
    if 'file' not in request.files:
        logger.error("No se encontró archivo en la solicitud")
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        logger.error("Nombre de archivo vacío")
        return jsonify({'error': 'No selected file'}), 400
        
    if not file.filename.endswith('.docx'):
        logger.error(f"Tipo de archivo no válido: {file.filename}")
        return jsonify({'error': 'File must be a .docx file'}), 400

    # Guardar el archivo temporalmente
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    logger.info(f"Archivo guardado en: {filepath}")
    
    # Leer el documento y encontrar campos vacíos
    doc = DocxTemplate(filepath)
    context = doc.undeclared_template_variables
    
    # Convertir los campos a un formato más amigable
    empty_fields = []
    current_section = "Información General"  # Sección por defecto
    
    # Diccionario de descripciones por campo
    field_descriptions = {
        'año': 'matricular y prestar servicios educacionales –quien acepta– en el Jardín Infantil Vuelta Canela, sucursal La Florida, para el año',
        'nombre_apoderado': 'Ingrese el nombre completo del apoderado legal del párvulo',
        'rut_apoderado': 'Ingrese el RUT del apoderado en formato XX.XXX.XXX-X',
        'domicilio_apoderado': 'Ingrese la dirección completa donde reside el apoderado',
        'comuna_apoderado': 'Ingrese la comuna donde reside el apoderado',
        'correo_electronico_apoderado': 'Ingrese el correo electrónico principal del apoderado',
        'nombre_parvulo': 'Ingrese el nombre del párvulo',
        'apellido_parvulo': 'Ingrese el apellido del párvulo',
        'fecha_nacimiento_parvulo': 'Ingrese la fecha de nacimiento del párvulo en formato DD/MM/AAAA',
        'rut_parvulo': 'Ingrese el RUT del párvulo en formato XX.XXX.XXX-X',
        'direccion_parvulo': 'Ingrese la dirección donde reside el párvulo',
        'nivel_parvulo': 'Seleccione el nivel educativo del párvulo',
        'jornada_parvulo': 'Seleccione la jornada en la que asistirá el párvulo',
        'mensualidad_kinder_prekinder': 'Ingrese el monto de la mensualidad para Kinder/Pre-Kinder',
        'mensualidad_salacuna_medio': 'Ingrese el monto de la mensualidad para Sala Cuna/Medio',
        'autorizacion_imagen': 'Seleccione si autoriza el uso de imágenes del párvulo'
    }
    
    for field in context:
        # Determinar si el campo es de autorización (opcional)
        is_optional = field.lower().startswith(('autorizar', 'autorización', 'permiso'))
        
        # Determinar la sección basada en el nombre del campo
        field_lower = field.lower()
        if 'apoderado' in field_lower:
            current_section = "Información del Apoderado"
        elif 'parvulo' in field_lower:
            current_section = "Información del Párvulo"
        elif 'mensualidad' in field_lower:
            current_section = "Información de Pagos"
        elif 'autorizo' in field_lower:
            current_section = "Autorizaciones"
        
        # Determinar el tipo de campo
        field_type = 'text'  # Por defecto
        if 'autorizacion' in field_lower or 'autorización' in field_lower:
            field_type = 'radio'
        
        # Obtener la descripción del campo
        description = field_descriptions.get(field, '')
        
        empty_fields.append({
            'id': field,
            'text': field,
            'type': field_type,
            'required': not is_optional,  # Los campos de autorización son opcionales
            'section': current_section,
            'description': description
        })
    
    logger.info(f"Campos vacíos encontrados: {len(empty_fields)}")
    return jsonify({
        'empty_fields': empty_fields,
        'filename': file.filename
    })

@app.route('/api/generate-pdf', methods=['POST', 'OPTIONS'])
def generate_pdf():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response
        
    try:
        logger.info("Iniciando proceso de generación de PDF")
        data = request.json
        contract_data = data.get('contractData', {})
        original_filename = data.get('filename', '')
        
        logger.info(f"Datos recibidos - Filename: {original_filename}, Campos: {len(contract_data)}")
        
        # Obtener la ruta del archivo original
        original_filepath = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
        logger.info(f"Ruta del archivo original: {original_filepath}")
        
        if not os.path.exists(original_filepath):
            raise FileNotFoundError(f"No se encontró el archivo original: {original_filepath}")
        
        # Crear un documento temporal para el PDF
        doc = DocxTemplate(original_filepath)
        logger.info("Documento original cargado")
        
        # Preparar el contexto con los datos
        context = contract_data
        context['fecha_actual'] = datetime.now().strftime('%d/%m/%Y')
        
        # Renderizar el documento
        logger.info("Renderizando documento con los datos")
        doc.render(context)
        
        # Crear nombre de archivo con nombre del apoderado y RUT
        nombre_apoderado = contract_data.get('nombre_apoderado', '')
        rut_apoderado = contract_data.get('rut_apoderado', '')
        
        # Limpiar el nombre del apoderado para usarlo en el nombre del archivo
        nombre_archivo = nombre_apoderado.replace(' ', '_').lower()
        if nombre_archivo:
            nombre_archivo = f"contrato_{nombre_archivo}_{rut_apoderado}.docx"
        else:
            nombre_archivo = 'contrato_generado.docx'
        
        # Guardar el documento temporal
        temp_docx = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
        doc.save(temp_docx.name)
        logger.info(f"Documento temporal guardado en: {temp_docx.name}")
        
        # Enviar el archivo
        logger.info("Enviando archivo")
        response = send_file(
            temp_docx.name,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=nombre_archivo
        )
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        return response
    except Exception as e:
        logger.error(f"Error general: {str(e)}", exc_info=True)
        response = jsonify({'error': str(e)})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        return response, 500
    finally:
        # Limpiar archivos temporales
        try:
            if 'temp_docx' in locals() and os.path.exists(temp_docx.name):
                os.unlink(temp_docx.name)
                logger.info("Archivo DOCX temporal eliminado")
        except Exception as e:
            logger.error(f"Error al limpiar archivos temporales: {str(e)}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 