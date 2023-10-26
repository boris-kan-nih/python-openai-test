README.md

1. Python installation
Visit https://www.python.org/downloads/ to get installation file. Install it to appropriate folder. You will need this folder path later.

2. Create a virutal environment
````shell
/path/to/python/executable -m venv .venv or
/usr/local/bin/python3.11 -m venv .venv
````

3. Activate the environment
````shell
source .venv/bin/activate # In terminal or 
env/Scripts/activate.bat      # In CMD
env/Scripts/Activate.ps1      # In Powershel
````
4. Install all dependencies
````pip install -r requirements.txt
````

6. Create an environment file
Copy the .env-example file and change its name to .env
Replace the SES policy ARN from AWS SES in POLICY_ARN
Replace sender's email in SENDER 

5. Run API
````shell
uvicorn main:app --reload
````

Now, api will run by default in 8080 port. It gets auto reload whenever there is changes in source files.