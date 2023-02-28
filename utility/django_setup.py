import subprocess

err_makemigrations = None
err_migrate = None
err_createsuperuser = None

# makemigrations
try:
    p = subprocess.run(['python', 'manage.py', 'makemigrations'], shell=True)
except Exception as e:
    err_makemigrations = e

print(f"ERROR: makemigrations failed\n{err_makemigrations}") if err_makemigrations is not None else print("INFO: makemigrations complete")

# migrate
try:
    p = subprocess.run(['python', 'manage.py', 'migrate'], shell=True)
except Exception as e:
    err_migrate = e

print(f"ERROR: migrate failed\n{err_migrate}") if err_migrate is not None else print("INFO: migrate complete")

# createsuperuser
try:
    p = subprocess.run(['python', 'manage.py', 'createsuperuser', '--no-input'], shell=True)
    p.kill()
except Exception as e:
    err_migrate = e

print(f"ERROR: createsuperuser failed\n{err_createsuperuser}") if err_createsuperuser is not None else print("INFO: createsuperuser complete")
