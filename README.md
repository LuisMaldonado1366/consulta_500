# Consulta 500

## Description

This Python script is designed to query all orders from WooCommerce API REST and write down to a specified sheets.

## Author

- **Author:** Luis Maldonado
- **Created on:**  Wed Nov  16 16:58:02 2022
- **Modified on:** Mon Aug  12 11:07:30 2024
- **Version:** 2.0.0

## Features

- Queries stock data from especified google sheets files and some database tables.
- Handles errors and retries accordingly to different situations.

## Dependencies

- Python 3.11.4
- pandas 2.0.2
- numpy 1.26.3
- pika 1.3.2
- mysql-connector 2.2.9
- gspread 5.9.0
- pydrive 1.3.1
- json
- google_sheets 1.0.1 (custom)
- connection 2.0.0 (custom)
- utils 1.0.0 (custom)

## Modules and Instances

- Standard: `json`, `sys`, `os.path`, `time.sleep`, `functools.reduce`
- Third-party: `pandas`, `pika`, `decouple.Config`, `decouple.RepositoryEnv` `requests.request`
- Custom: `GoogleSheets`, `Connection`

## Instances

- Environment Configuration: `env_config` (`decouple.Config`)
- Google Sheets Instance: `gsh` (`GoogleSheets`)

# Constants

- Maximum Retries: MAX_RETRIES
- Retries: RETRIES
- Database Credentials: DATABASE_HOST, DATABASE_PORT, DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME.
- Request Queue: REQUEST_QUEUE
- AMQP Credentials: AMQP_CREDENTIALS
- Sheets Fields: SHEETS

# Functions
1. main():
- Main execution loop for processing messages received from AMQP.

# Main Execution



## Configuration

For the configuration there must be some steps.
1. Clone the repository to your local machine.

2. If not already done, save the google tokens for the gmail api and the gsheets api, you can generate them at *[Google cloud console](https://console.cloud.google.com/)*, rename them as "mailer_token.json" and "sheets_token.json".

3. Set up the environment variables by creating a .env file with the necessary databse cradentials and store it in the "app" folder, Database credentials should be provided in the .env file, which means a json containing `host`, `user` and `password`.

4. Create a volume called "*.secrets*" using the command, in case the "*u*" volume doesn't exist, create it likewise before:
```bash
mkdir /u/.secrets
chmod -Rf 777 /u/.secrets
```

5. Set up the necessary tables in the database ("stock_update_result", "stock_update_config").

6. Build the docker image and get the container up and running using the `sh` command:

```bash 
sudo sh consulta_500.sh
```


## Usage

1. Ensure that the RabbitMQ server is running and accessible and that you have the right credentials stored y the config table at the database.
2. Set up the database connection and provide the necessary credentials.
3. Ensure the sheets data (i.e. correct sheet id, column names and so on are set in the config table).
4. Monitor the container is up and running.


## License

Not licensed yet.
