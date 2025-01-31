# Cloud Run application utilizing Streamlit Framework that demonstrates working with Gemini API in Vertex AI

|           |                                                |
| --------- | ---------------------------------------------- |
| Author(s) | [Adrien Chan](https://github.com/lorcie) |

This application demonstrates a Cloud Run application that uses the [Streamlit](https://streamlit.io/) framework.

### Clone MyMLB Repository 
Clone the repository about MyMlb application and Go inside the working Directory locally.

### Local Deployment (Cloud Shell)
Note: Before proceeding, make sure to Navigate to the folder as your active working directory.

Set up the Python virtual environment and install dependencies:

```bash
python3 -m venv mymlb
source mymlb/bin/activate
pip install -r requirements.txt
```

### Set environment variables:
**GCP_PROJECT:** Your Google Cloud project ID.**
**GCP_REGION:** The region where you deploy your Cloud Run app (e.g., us-central1).
```bash
export GCP_PROJECT='<Your GCP Project Id>'  # Replace with your project ID
export GCP_REGION='us-central1'             # Modify if needed
```
### Run the application locally:
```
streamlit run app.py \
  --browser.serverAddress=localhost \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false \
  --server.port 8080
```
Access the application URL provided in Cloud Shell's web preview or open it in your browser.
Build and Deploy to Cloud Run

### Set up environment variables for Cloud Run:

GCP_PROJECT: Your Google Cloud project ID.
GCP_REGION: The region where you deploy your Cloud Run app (e.g., us-central1).
```bash
export GCP_PROJECT='<Your GCP Project Id>'  # Replace with your project ID
export GCP_REGION='us-central1'             # Modify if needed
```

### Build the Docker image and push it to Artifact Registry:

```bash
export AR_REPO='<REPLACE_WITH_YOUR_AR_REPO_NAME>'  # Replace with your Artifact Registry repository name
export SERVICE_NAME='gemini-streamlit-app'         # Customize your application and Cloud Run service name
```
```
gcloud artifacts repositories create "$AR_REPO" --location="$GCP_REGION" --repository-format=Docker
gcloud auth configure-docker "$GCP_REGION-docker.pkg.dev"
gcloud builds submit --tag "$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/$AR_REPO/$SERVICE_NAME"
```
### Deploy the service to Cloud Run:

```bash
gcloud run deploy "$SERVICE_NAME" \
  --port=8080 \
  --image="$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/$AR_REPO/$SERVICE_NAME" \
  --allow-unauthenticated \
  --region=$GCP_REGION \
  --platform=managed  \
  --project=$GCP_PROJECT \
  --set-env-vars=GCP_PROJECT=$GCP_PROJECT,GCP_REGION=$GCP_REGION
```
Upon successful deployment, access the provided URL to explore the newly deployed Cloud Run application. Congratulations!
