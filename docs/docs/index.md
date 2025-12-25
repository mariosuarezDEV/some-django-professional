# Curso DJango

Configuracion basica a caracteristicas avanzadas usando cosas nativas de python y paquets que se complementan perfecto con el framework django.

## 1. Preparar el entorno

- Crear el entorno virtual

```bash
python -m venv .venv
```

- Activar el entorno virtual
- En Windows PowerShell

```bash
.\.venv\Scripts\Activate.ps1
```

> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

- En Windows CMD

```bash
.\.venv\Scripts\activate.bat
```

- En Linux o MacOS

```bash
source .venv/bin/activate
```

- Instalar las dependencias (creacion de proyecto)

```bash
pip install "paquete"
```

- Instalar las depedencias (Proyecto ya construido)

```bash
pip install -r requirements.txt
```

- Guardar las dependencias en un archivo

```bash
pip freeze > requirements.txt
```

## 2. Crear proyecto

- Crear un proyecto de consola

```bash
django-admin startproject project
```

- Crear un proyecto de consola en el path (todos los archivos se quedan el path)

```bash
django-admin startproject project .
```
