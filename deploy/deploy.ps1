# deploy.ps1

$PROJECT_ID = "serp-425005"
$REGION = "us-central1"
$JOB_NAME = "webpage-monitor-job"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$JOB_NAME"
$BUCKET_NAME = "$PROJECT_ID-monitor-data" 
$SCHEDULE = "0 0 * * *" 
$TIMEZONE = "Asia/Seoul"

Write-Host "Configuring Gcloud Project..."
gcloud config set project $PROJECT_ID
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"

# 1. GCS Bucket Setup
Write-Host "Checking GCS Bucket: gs://$BUCKET_NAME..."
$bucketExists = gcloud storage buckets list gs://$BUCKET_NAME --format="value(name)" 2>$null
if (-not $bucketExists) {
    Write-Host "Creating bucket gs://$BUCKET_NAME..."
    gcloud storage buckets create gs://$BUCKET_NAME --location=$REGION
}

# 2. Build and Submit Image
Write-Host "Building container image from root..."
try {
    Copy-Item -Path "deploy/Dockerfile" -Destination "." -Force
    Copy-Item -Path "deploy/.gcloudignore" -Destination "." -Force
    gcloud builds submit --tag $IMAGE_NAME .
}
finally {
    if (Test-Path "Dockerfile") { Remove-Item -Path "Dockerfile" -Force }
    if (Test-Path ".gcloudignore") { Remove-Item -Path ".gcloudignore" -Force }
}

# 3. Create/Update Cloud Run Job
Write-Host "Updating Cloud Run Job: $JOB_NAME..."
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

Write-Host "Granting permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/run.invoker" | Out-Null
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/run.developer" | Out-Null

# 5. Cloud Scheduler
$SCHEDULER_JOB_NAME = "$JOB_NAME-trigger"
$URI = "https://$REGION-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_NUMBER/jobs/$JOB_NAME:run"

Write-Host "Updating Cloud Scheduler: $SCHEDULER_JOB_NAME..."
gcloud scheduler jobs describe $SCHEDULER_JOB_NAME --location $REGION 2>$null
if ($LASTEXITCODE -eq 0) {
    gcloud scheduler jobs update http $SCHEDULER_JOB_NAME --location $REGION --schedule="$SCHEDULE" --time-zone="$TIMEZONE" --uri="$URI" --http-method=POST --message-body="{}" --update-headers="Content-Type=application/json" --oidc-service-account-email="$SA_EMAIL" --oidc-token-audience="$URI"
}
else {
    gcloud scheduler jobs create http $SCHEDULER_JOB_NAME --location $REGION --schedule="$SCHEDULE" --time-zone="$TIMEZONE" --uri="$URI" --http-method=POST --message-body="{}" --headers="Content-Type=application/json" --oidc-service-account-email="$SA_EMAIL" --oidc-token-audience="$URI"
}

Write-Host "Deployment complete."
Write-Host "IMPORTANT: Set your secrets (GOOGLE_API_KEY, SMTP_PASSWORD) in the Cloud Run Job Console if not yet set."

