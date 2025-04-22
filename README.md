# RFP-Studio

## Running the Application

1. **Build the Docker Image**  
    Build the Docker image using the provided `Dockerfile`:
    ```bash
    docker build -t rfp-studio .
    ```

2. **Run the Docker Container**
    Start the application by running the Docker container:
    ```bash
    docker run -p 8000:8000 --env-file .env rfp-studio
    ```

3. **Access the API**
    Open your browser or API client and navigate to:
    ```bash
    http://127.0.0.1:8000
    ```

    The API documentation is available at:
    ```bash
    http://127.0.0.1:8000/docs
    ```
