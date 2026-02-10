# QA Agent – MVP

Agente interno para ayudar a POs y QAs a mejorar la calidad de las historias de usuario **antes del desarrollo**.

El agente analiza historias, detecta faltas de definición e incongruencias funcionales, y propone criterios de aceptación en formato Gherkin.  
No toma decisiones de negocio ni sustituye al equipo: actúa como **asistente de calidad**.

---

## Qué hace

Dada una historia de usuario, el agente devuelve un JSON con:

- Resumen de calidad de la historia
- Nivel de riesgo (LOW / MEDIUM / HIGH)
- Faltas de definición detectadas
- Criterios de aceptación propuestos (Gherkin)
- Casos borde relevantes
- Notas sobre automatización de tests

El objetivo es reducir aclaraciones posteriores y bugs funcionales.

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

(No se guarda en el código.)

---

## Arrancar el servicio

uvicorn api:app --reload

Servicio disponible en:

http://127.0.0.1:8000  
Swagger UI:

http://127.0.0.1:8000/docs

---

## Uso

Navega a la url del Swagger y en el Endpoint:

POST /analyze

Ejemplo de petición:

{
  "issue_id": "PROJ-203",
  "title": "Registro de usuario con validación de edad",
  "description": "Como usuario quiero registrarme en la plataforma creando una cuenta con mis datos personales.",
  "acceptance_criteria": "El usuario debe poder completar un formulario de registro y ser mayor de 18 años."
}

Respuesta:

JSON estructurado con análisis de calidad, riesgos y criterios de aceptación.

---

## Estado del proyecto

- MVP funcional
- Uso local
- Fácil de integrar con Jira en siguientes fases
- Preparado para extender a multi-equipo o multi-cliente
