# deploy.ps1

$PROJECT_ID = "serp-425005"
$REGION = "us-central1"
$JOB_NAME = "webpage-monitor-job"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$JOB_NAME"
$BUCKET_NAME = "$PROJECT_ID-monitor-data" # Automated bucket name
$SCHEDULE = "0 0 * * *" # Midnight daily
$TIMEZONE = "Asia/Seoul"

Write-Host "Configuring Gcloud Project..."
gcloud config set project $PROJECT_ID

# 1. GCS Bucket Setup
Write-Host "Checking GCS Bucket: gs://$BUCKET_NAME..."
$bucketExists = gcloud storage buckets list gs://$BUCKET_NAME --format="value(name)" 2>$null
if (-not $bucketExists) {
    Write-Host "Creating bucket gs://$BUCKET_NAME..."
    gcloud storage buckets create gs://$BUCKET_NAME --location=$REGION
}
else {
    Write-Host "Bucket exists."
}

# 2. Build and Submit Image
Write-Host "Building container image..."
gcloud builds submit --tag $IMAGE_NAME .

# 3. Create/Update Cloud Run Job
Write-Host "Updating Cloud Run Job: $JOB_NAME..."
# Check if job exists to update or create
gcloud run jobs describe $JOB_NAME --region $REGION 2>$null
if ($LASTEXITCODE -eq 0) {
    gcloud run jobs update $JOB_NAME --image $IMAGE_NAME --region $REGION --max-retries 0 --task-timeout 10m
}
else {
    gcloud run jobs create $JOB_NAME --image $IMAGE_NAME --region $REGION --max-retries 0 --task-timeout 10m
}

# 4. Service Account for Scheduler
$SA_NAME = "webpage-monitor-sa"
$SA_EMAIL = "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"
Write-Host "Checking Service Account: $SA_EMAIL..."
gcloud iam service-accounts describe $SA_EMAIL 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating Service Account $SA_NAME..."
    gcloud iam service-accounts create $SA_NAME --display-name "Webpage Monitor Scheduler SA"
}

# Grant Invoker Permission
Write-Host "Granting Run Invoker permission..."
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/run.invoker" | Out-Null
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/run.developer" | Out-Null # Ensure job execution rights

# 5. Cloud Scheduler
$SCHEDULER_JOB_NAME = "$JOB_NAME-trigger"
Write-Host "Updating Cloud Scheduler: $SCHEDULER_JOB_NAME..."
gcloud scheduler jobs describe $SCHEDULER_JOB_NAME --location $REGION 2>$null
if ($LASTEXITCODE -eq 0) {
    gcloud scheduler jobs update http $SCHEDULER_JOB_NAME --location $REGION --schedule="$SCHEDULE" --time-zone="$TIMEZONE" --uri="https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/$JOB_NAME:run" --http-method=POST --oauth-service-account-email="$SA_EMAIL"
}
else {
    gcloud scheduler jobs create http $SCHEDULER_JOB_NAME --location $REGION --schedule="$SCHEDULE" --time-zone="$TIMEZONE" --uri="https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/$JOB_NAME:run" --http-method=POST --oauth-service-account-email="$SA_EMAIL"
}

Write-Host "Deployment complete."
Write-Host "IMPORTANT: You must set your environment variables (GOOGLE_API_KEY, SMTP_PASSWORD) in the Cloud Run Job Console:"
Write-Host "https://console.cloud.google.com/run/jobs/details/$REGION/$JOB_NAME/configuration?project=$PROJECT_ID"
