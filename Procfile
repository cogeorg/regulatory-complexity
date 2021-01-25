web: python --chdir app __init__:app runserver --host 0.0.0.0 --port ${PORT}
init: python --chdir app __init__:app db init
migrate: python --chdir app __init__:app db migrate
upgrade: python --chdir app __init__:app db upgrade