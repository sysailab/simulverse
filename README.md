# simulverse
<p align="center">
    <em> A metaverse content management framework based on fastapi </em>
</p>

# Prerequisite
 * In order to execute the simulverse, you should setup the following variables in the `instance/config.py` file.
 ```
    MONGODB_URL = "mongodb://id:pw@mongo_db_:27017/"

    # to earn key run:
    # openssl rand -hex 32
    JWT_REFRESH_SECRET_KEY = "COMPLEX_KEY"
    JWT_SECRET_KEY = "COMPLEX_KEY"
    ALGORITHM = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
    REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
 ```
 - You should put `instance` directory under the `app/core/`  to execute the simulverse
 - If you want to use management scripts, you should put `instance` directory under the `manage/`

# How to Execute
 - HTTPS support
```python
>$ python simulverse.py https
```
 - HTTP support
 ```python
>$ python simulverse.py http
```