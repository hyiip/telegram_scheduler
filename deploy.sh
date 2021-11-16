gcloud beta functions deploy gcf_handler \
--runtime python37 \
--trigger-http \
--allow-unauthenticated \
--region=us-central1 \
--security-level=secure-always \
--update-secrets 'TGTOKEN=TGTOKEN:latest'