# Tutorial Summary

## Initial Setup
1.  **Activate Cloud Shell**
2.  **Open Editor**
3.  **Sign in to Cloud Code**
4.  **Find Google Cloud Project ID**
5.  **Open terminal**

## Terminal Commands
1.  **Verify authentication:** `gcloud auth list`
2.  **Clone repo:** `git clone -b adk-1.2.1-a2a-0.2.7 https://github.com/weimeilin79/instavibe-bootstrap.git`
3.  **Set permissions:**
    ```bash
    chmod +x ~/instavibe-bootstrap/init.sh
    chmod +x ~/instavibe-bootstrap/set_env.sh
    ```
4.  **Run init script:**
    ```bash
    cd ~/instavibe-bootstrap
    ./init.sh
    ```
5.  **Set gcloud project:** `gcloud config set project $(cat ~/project_id.txt) --quiet`
6.  **Enable APIs:**
    ```bash
    gcloud services enable run.googleapis.com \
                            cloudfunctions.googleapis.com \
                            cloudbuild.googleapis.com \
                            artifactregistry.googleapis.com \
                            spanner.googleapis.com \
                            apikeys.googleapis.com \
                            iam.googleapis.com \
                            compute.googleapis.com \
                            aiplatform.googleapis.com \
                            cloudresourcemanager.googleapis.com \
                            maps-backend.googleapis.com
    ```
7.  **Set environment variables:**
    ```bash
    export PROJECT_ID=$(gcloud config get project)
    export PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
    export SERVICE_ACCOUNT_NAME=$(gcloud compute project-info describe --format="value(defaultServiceAccount)")
    export SPANNER_INSTANCE_ID="instavibe-graph-instance"
    export SPANNER_DATABASE_ID="graphdb"
    export GOOGLE_CLOUD_PROJECT=$(gcloud config get project)
    export GOOGLE_GENAI_USE_VERTEXAI=TRUE
    export GOOGLE_CLOUD_LOCATION="us-central1"
    ```
8.  **Grant IAM Permissions:** Run a series of `gcloud projects add-iam-policy-binding` commands.
9.  **Create Artifact Registry:**
    ```bash
    export REPO_NAME="introveally-repo"
    gcloud artifacts repositories create $REPO_NAME \
      --repository-format=docker \
      --location=us-central1 \
      --description="Docker repository for InstaVibe workshop"
    ```

## Google Cloud Console UI Steps
1.  **Validate IAM in console**
2.  **Create Maps API Key:**
    *   Go to APIs & Services > Credentials.
    *   Create a new API key.
    *   Rename it to "Maps Platform API Key".
    *   Restrict it to "Maps JavaScript API".