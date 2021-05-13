
<h1 align="center">
<br>
Twitter Bot
</h1>

<p align="center">conquer twitter</p>

<hr />
<br />


## 📚 Project Definition

Simple API for social media platform(currently only twitter is supported)


## 🛠️ Features

Technologies used:

- ⚛️ **Flask** — Python library
- 🌐 **Docker** — Containerization
- 📊 **PostgreSQL** - Database


## 🚀 Getting started

- create and configure .env.production / .env.development files (cp .env.example)

- configure database:

  1. flask db init

  2. flask db upgrade

  3. flask configure-db (all flask commands ar listed with : (venv) → <PROJECT_NAME>› flask)


## 🔋 Commands

- check flask for more info


## 🌐 Docker development setup

- run docker-compose up -d inside root
- 2 containers are created:
  - app container
  - database container


## Flask Migrate changes

- update file ```\migrations\env.py``` so the database will be created in a separate postgres schema (other than public)
  
```
schema = current_app.config['DB_SCHEMA']

def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and object.schema != schema:
        return False
    else:
        return True

with connectable.connect() as connection:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
        version_table_schema=schema,
        include_object=include_object,
        process_revision_directives=process_revision_directives,
        **current_app.extensions['migrate'].configure_args
    )
```
