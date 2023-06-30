PROJECT_ID=summarize-app-391011
gcloud config set project ${PROJECT_ID}
gcloud builds submit --tag gcr.io/${PROJECT_ID}/slack-app
gcloud run deploy slack-app --image gcr.io/${PROJECT_ID}/slack-app --platform managed
