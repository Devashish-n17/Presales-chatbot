# RFP-Studio

## Running the Application

1. **Build the Docker Image**  
    ```bash
    docker build -t rfp-studio .
    ```

2. **Run the Docker Container**
    ```bash
    docker run -p 8000:8000 --env-file .env rfp-studio
    ```

3. **Access the API**
    ```bash
    http://127.0.0.1:8000
    ```

    For Swagger UI:
    ```bash
    http://127.0.0.1:8000/docs
    ```
