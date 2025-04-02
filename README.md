# Generador de Contratos Educacionales

Aplicación web para generar contratos educacionales de manera automatizada para el Jardín Infantil Vuelta Canela.

## Características

- Carga de plantillas Word (.docx)
- Detección automática de campos variables
- Interfaz intuitiva para completar datos
- Generación de documentos personalizados
- Organización de campos por secciones
- Validación de campos según tipo de dato

## Tecnologías Utilizadas

- Frontend: React.js
- Backend: Flask (Python)
- Procesamiento de documentos: python-docx, docxtpl

## Requisitos

- Python 3.8+
- Node.js 14+
- npm o yarn

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/contrato-educacional-vueltacanela.git
cd contrato-educacional-vueltacanela
```

2. Instalar dependencias del backend:
```bash
pip install -r requirements.txt
```

3. Instalar dependencias del frontend:
```bash
cd frontend
npm install
```

## Uso Local

1. Iniciar el servidor backend:
```bash
python app.py
```

2. En otra terminal, iniciar el frontend:
```bash
cd frontend
npm start
```

3. Abrir http://localhost:3000 en el navegador

## Estructura del Proyecto

```
contrato-educacional-vueltacanela/
├── frontend/           # Aplicación React
├── backend/           # Servidor Flask
├── uploads/           # Carpeta para archivos temporales
├── requirements.txt   # Dependencias de Python
└── README.md         # Este archivo
```

## Formato de Plantilla

La plantilla Word debe usar el siguiente formato para las variables:

```
{{ variable }}
```

Para agregar descripciones y organizar campos:

```
<!--SECTION:Nombre de la Sección-->
<!--FIELD:help=Descripción del campo-->
{{ variable }}
```

## Despliegue

Este proyecto está configurado para ser desplegado en Vercel:

1. Frontend: Se despliega automáticamente desde la rama main
2. Backend: Requiere configuración adicional en Vercel

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles. 