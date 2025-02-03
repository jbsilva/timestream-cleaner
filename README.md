# Amazon Timestream Database Table Cleanup Tool

This Python CLI tool allows you to delete all tables in a specified Amazon Timestream database.

## Features

- List all tables in a Timestream database
- Delete multiple tables (with user confirmation)
- Detailed logging

## Requirements

- Python 3.12+
- AWS credentials with Timestream permissions

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/jbsilva/timestream-cleaner.git
   cd timestream-cleaner
   ```

2. Install the required dependencies:

   ```bash
   uv sync
   ```

   Or use the `Setup Python Environment` VS Code task.

## Usage

To delete all tables in a Timestream database:

```bash
timestream-cleaner [OPTIONS] DATABASE_NAME
```

Options:

- `--region TEXT`: AWS region for Timestream database (default: eu-west-1)
- `--help`: Show help message and exit

Example:

```bash
timestream-cleaner --region eu-west-2 my-database
```

## Permissions

Required IAM permissions:

- `timestream:ListTables`
- `timestream:DeleteTable`

## Development

To contribute to this project:

1. Fork the repository
2. Create a new branch for your feature
3. Implement your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool can permanently delete data. Use with caution and always backup your data before running
deletion operations.
