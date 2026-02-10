# QA Agent – MVP

Agente interno para ayudar a POs y QAs a mejorar la calidad de las historias de usuario **antes del desarrollo**.

El agente actúa como un QA senior virtual: analiza historias, detecta faltas de definición e incongruencias funcionales, y propone criterios de aceptación claros y testables.  
No toma decisiones de negocio ni sustituye al equipo.

---

## Qué hace

Dada una historia de usuario, el agente devuelve un JSON estructurado con:

- Resumen de calidad de la historia
- Nivel de riesgo (LOW / MEDIUM / HIGH)
- Faltas de definición detectadas
- Criterios de aceptación propuestos (Gherkin)
- Casos borde relevantes
- Notas sobre automatización de tests

El análisis se apoya en:
- Un prompt de QA senior
- Validación estricta por schema
- Reintento automático con autocorrección
- Conocimiento del proyecto (RAG)

---

## Conocimiento del proyecto (RAG)

El agente puede usar documentación propia del proyecto (RAG – Retrieval Augmented Generation), por ejemplo:

- Definition of Done
- Guías de QA
- Decisiones funcionales estables
- Limitaciones técnicas conocidas
- Bugs recurrentes

Estos documentos viven en archivos Markdown y se consultan dinámicamente para mejorar la precisión del análisis, sin entrenar el modelo ni almacenar conversaciones.

---

## Requisitos

- macOS / Linux
- Python 3.9+
- Cuenta en OpenAI Platform con billing activo
- API Key de OpenAI

---

## Instalación

1. Entrar en la carpeta del proyecto

cd qa-agent-mvp

2. Crear entorno virtual

python3 -m venv .venv  
source .venv/bin/activate

3. Instalar dependencias

pip install -r requirements.txt

---

## Configuración

Exportar la API key de OpenAI como variable de entorno:

export OPENAI_API_KEY="tu_api_key_aqui"

La API key no se guarda en el código ni en el repositorio.

---

## Arrancar el servicio

uvicorn api:app --reload

Servicio disponible en:

http://127.0.0.1:8000

Swagger UI:

http://127.0.0.1:8000/docs

---

## Uso

### Endpoint

POST /analyze

### Ejemplo de petición

{
  "issue_id": "PROJ-203",
  "title": "Registro de usuario con validación de edad",
  "description": "Como usuario quiero registrarme en la plataforma creando una cuenta con mis datos personales.",
  "acceptance_criteria": "El usuario debe poder completar un formulario de registro y ser mayor de 18 años."
}

### Respuesta

JSON estructurado con:
- Análisis de calidad
- Riesgos
- Criterios de aceptación
- Casos borde
- Consideraciones de automatización

---

## Estructura del proyecto

qa-agent-mvp/
├── api.py
├── core/
│   ├── agent.py
│   ├── llm.py
│   ├── prompt_builder.py
│   ├── retry.py
│   ├── validator.py
│   ├── schemas.py
│   └── rag.py
├── tenants/
│   └── default/
│       ├── system_prompt.txt
│       └── rag/
│           └── *.md
├── schemas/
└── requirements.txt

---

## Qué NO hace el agente

- No aprueba historias
- No redefine requisitos de negocio
- No prioriza
- No inventa comportamiento no especificado

---

## Estado del proyecto

- MVP funcional y estable
- Uso local
- Preparado para integración con Jira
- Preparado para multi-equipo / multi-cliente
- Base sólida para evolución a CI/CD

