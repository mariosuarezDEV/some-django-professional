# 🚀 Algo de Django Profesional

**Una guía integral desde los fundamentos hasta la arquitectura de sistemas complejos.**

Este proyecto no es solo un repositorio de código; es una ruta de aprendizaje basada en la experiencia real desarrollando sistemas de nivel empresarial. Aquí encontrarás teoría aplicada y estructuras profesionales para dominar Django.

---

## 👨‍💻 Sobre el Autor y la Guía

Con más de **2 años de experiencia en el backend**, he condensado conocimientos adquiridos en proyectos críticos de la vida real:

* **Sistemas de RRHH:** Gestión de nóminas, empleados y sucursales.
* **E-commerce & Fintech:** Integración de pasarelas de pago (Stripe) y logística de delivery.
* **Sistemas Legacy:** Modernización y trabajo con bases de datos preexistentes.
* **Open Source:** Colaboraciones que refuerzan las mejores prácticas de la industria.

---

## 🛠 Stack Tecnológico

El proyecto está diseñado bajo una arquitectura moderna y escalable, utilizando Docker para centralizar todos los servicios:

| Componente | Tecnología | Propósito |
| --- | --- | --- |
| **Backend** | Django | Framework principal |
| **Base de Datos** | PostgreSQL, SQLserver (MSSQL), MySQL | Almacenamiento relacional robusto |
| **Cache / Broker** | Redis | Manejo de colas y optimización |
| **Tareas Asíncronas** | Celery | Procesamiento de tareas en segundo plano |
| **Programador** | Celery Beat | Tareas programadas (cron jobs) |

---

## 📖 Documentación

La documentación detallada está construida con **MkDocs** y está disponible en línea:
👉 **[Ver Documentación Completa](https://mariosuarezdev.github.io/some-django-professional/)**

---

## 🚀 Instalación y Configuración Local

### 1. Clonar el repositorio

```bash
git clone https://github.com/mariosuarezDEV/some-django-professional
cd some-django-professional

```

### 2. Configuración con Docker (Recomendado)

Este proyecto utiliza **Dev Containers** para facilitar la configuración del entorno de desarrollo.

1. Abre la carpeta en **Visual Studio Code**.
2. Si tienes la extensión "Dev Containers" instalada, aparecerá un aviso. Selecciona **"Reopen in Container"** (Volver a ejecutar en el contenedor).
3. VSC construirá la imagen automáticamente con Django, Postgres, Redis y Celery listos para usar.

### 3. Preparar el Proyecto

Una vez dentro del contenedor (o en tu entorno virtual local):

**Instalar dependencias:**

```bash
pip install -r requirements.txt

```

**Configurar la base de datos:**

```bash
python manage.py migrate
python manage.py createsuperuser

```

---

## 🖥️ Uso

### Ejecutar la Documentación (Local)

Si prefieres leer la guía en tu propia máquina:

```bash
mkdocs serve

```

Luego visita `http://127.0.0.1:8000`.

### Ejecutar el Proyecto Django

Para ver el sistema de ejemplo en funcionamiento:

```bash
cd project
python manage.py runserver 0.0.0.0:8080

```

---

## 📂 Estructura del Proyecto

* `/docs`: Archivos fuente de la documentación en Markdown.
* `/project`: El núcleo de la aplicación Django con las implementaciones prácticas.
* `.devcontainer`: Configuración de la arquitectura Dockerizada.

---

*Desarrollado con ❤️ por [mariosuarezDEV*](https://github.com/mariosuarezDEV)
