# Image Hosting App

This codebase was adapted from the steps in [Modern JavaScript for Django Developers](https://www.saaspegasus.com/guides/modern-javascript-for-django-developers/).

This mini app allows the uploading and viewing of images and was created as a basic coding exercise.

This project can be run out of the box via Docker `docker-compose build` and then `docker-compose up`. This is meant to simulate how it could be deployed and allows easy startup without needing to handle dependencies. After starting up the container you will have access to it via http://localhost:8000/.

However, if you want to do active local development then you should instead run both the backend and frontend directly locally.

## Project setup

### Backend setup

Requires Python 3.14. This project was setup with UV, but other virtual environments should work. Just replace any instance of `uv run` with `python` in the instructions below.

- Install dependencies `uv sync` or `pip install pyproject.toml`
- Setup database `uv run manage.py migrate`
- Seed database `uv run manage.py seed` (this creates test users in the DB)
- Startup backend `uv run manage.py runserver`

You should now see your local server starting up under `localhost:8000`.

If you want to run tests, then they can be run via `uv run manage.py test`.

### Frontend setup

Requires node 24.14.1.

- Install dependencies `npm i`
- Run frontend server `npm run dev`

Your frontend should now be running. The URL it gives is unused as all routing goes via the backend under `localhost:8000`. It is only possible to view the frontend when Django is also running.

Tests are run via `npm run test`.

## Using Image Host

[main](.assets/main.png)

## Technical details

### Repository Structure

```text
image-host/ - Root project directory
|-- backend/ - Django backend app code
|   |-- management/ - Django management command modules
|   |-- migrations/ - Database migration history
|   |-- tests/ - Backend unit and integration tests
|   `-- views/ - HTTP view handlers and API endpoints
|-- frontend/ - React frontend application
|   |-- api-client/ - Generated TypeScript API client
|   |-- images/ - Folder to organise code related to the display of images
|   `-- tests/ - Frontend test suites and helpers
`-- project/ - Django project configuration
`-- dist/ - Static file build area shared between the frontend and the backend. Also used to store images.
```

uv run manage.py spectacular --file schema.yml
npm run generate-api
