#!/bin/bash

# List of environment variables to check
# env_vars=("TG_ADMIN_ID" "TG_API_TOKEN" "DB_HOST" "DB_PORT" "DB_USER" "DB_PASSWORD" "DB_NAME" "TABLE_ID")

# for var in "${env_vars[@]}"; do
#     if [ -z "${!var}" ]; then
#         echo "Environment variable $var is not set or is empty."
#         exit 1
#     # else
#     #     echo "Environment variable $var is set to '${!var}'."
#     fi
# done

# Add cron jobs to crontab
# (crontab -l 2>/dev/null; echo "0 * * * * python3 /app/upload_sql.py") | crontab -
# (crontab -l 2>/dev/null; echo "*/14 * * * * python3 /app/upload_sql.py") | crontab -



# Start the schedules.py script
python3 -u /app/schedules.py
