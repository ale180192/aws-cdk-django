
## Dish clients service
Este servicio esta implementado con el framework FastAPI/Mangum, cuenta con el CRUD de clientes en donde se tienen validaciones y las respuestas de error y exito estan homologadas con la misma estructura. La estructura del servicio es guiada por una arquitectura hexagonal(adaptador/puerto), Usa inyeccion de dependencias para que sea escalable y las pruebas unitarias/integracion se puedan hacer de una manera sencilla y rapida. Crear o modificar funcionalidades y probarlas de manera local es muy sencillo.

### Preparar entorno de desarrollo
Primero tenemos que crear nuestro entorno virtual, instalar las dependencias, crear nuestro archivo .env donde estaran las variables para podernos conectar a nuestra base de datos local o remota.
```bash
python3 -m venv .venv-lambda
source .venv-lambda/bin/activate
pip install -r src/requirements.txt

# creamos nuestro archivo .env dentro del folder src y seteamos nuestras variables. ver abajo todas las variables y su uso
touch src/.env

# Levantamos nuestro servidor local
cd src
ENVIRONMENT=local uvicorn entrypoint.handler:app --reload

# levantamos nuestro servidor local y forzamos que las variables se carguen de los secrets. para esto tenemos que settear las variables AWS_SECRET_ID y AWS_PROFILE en el archivo .en
ENVIRONMENT=staging FORCE_SECRETS_AWS_FROM_LOCAL=true uvicorn entrypoint.handler:app --reload
```

#### .env variables
```txt
AWS_SECRET_ID=xxx
SQL_HOST=xxx
SQL_USER=xxx
SQL_PASSWORD=xxx
SQL_DATABASE=xxx
AWS_PROFILE=xxx
```

### TODO:
* Crear un docker-compose file para levantar todo el entorno local, por ahora se tiene que instalar de forma independiente el servidor SQL, crear la base de datos y la tabla clients.
* Crear el update y delete del CRUD
* Crear pruebas unitarias y de integracion

### ddl

```sql
CREATE DATABASE dish_clients;

CREATE TABLE clients (
    phone VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255),
    last_name VARCHAR(255),
    age VARCHAR(3)
);
```

### Documentacion de la API
La API se desarrollo cuidando de que la documentacion se genere de forma correcta, esta la podemos encontrar en la ruta: http://localhost:8000/docs

Nota: En el ambiente de produccion no funciona por ahora.


### Endpoints
URL de produccion: https://fdslzckf30.execute-api.us-east-1.amazonaws.com/prod

GET detail -> base_url/v1/clients/<phone_number>
GET all -> base_url/v1/clients/list
CREATE -> base_url/v1/clients/


Ejemplo para listar todos los clientes en produccion: https://fdslzckf30.execute-api.us-east-1.amazonaws.com/prod/v1/clients/list




