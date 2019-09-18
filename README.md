This is the code for the **supervisor** that all **crawlers** report to.

## PREPARE THE ENVIRONMENT

**NOTE:** The supervisor can only run in a **Google Compute Engine** instance.

## INSTALL THE DEPENDENCIES

    pip install -r requirements.txt

## CONFIGURE THE SUPERVISOR

Create `config.py` based on `config.py.sample`.

    cp config.py.sample config.py
    
Edit `config.py`.

## RUN THE SUPERVISOR

    python app.py
