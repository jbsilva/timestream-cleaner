#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "boto3",
#     "boto3-stubs[timestream-write]",
#     "loguru",
#     "typer",
# ]
# ///
"""
Amazon Timestream Database Table Cleanup CLI Tool.

This script provides a command-line interface for deleting all tables in a specified Amazon
Timestream database.

Usage:
    python timestream_cleaner.py [OPTIONS] DATABASE_NAME

Options:
    --region TEXT  AWS region for Timestream database (default: eu-west-1)
    --help         Show this message and exit.
"""

import sys
from collections.abc import Generator
from typing import TYPE_CHECKING

import boto3
import typer
from botocore.exceptions import ClientError, NoCredentialsError
from loguru import logger
from mypy_boto3_timestream_write.client import TimestreamWriteClient


if TYPE_CHECKING:
    from mypy_boto3_timestream_write.type_defs import ListTablesResponseTypeDef

app = typer.Typer(help="Amazon Timestream database management tool")

# Remove the default handler so we can add custom ones
logger.remove()

# Console handler: logs ERROR and above to stderr
logger.add(
    sink=sys.stderr,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{message}</cyan>"
    ),
    colorize=True,
    level="ERROR",
)

# File handler: logs DEBUG-level messages to a file
logger.add(
    "logs/timestream_cleaner_{time:YYYY_MM_DD_HH_mm_ss}.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
)


def list_all_tables(
    client: TimestreamWriteClient,
    database_name: str,
) -> Generator[str]:
    """
    List all tables in a Timestream database.

    Args:
        client: Initialized Timestream client.
        database_name: Name of the database to list tables from.

    Yields:
        str: Table names from the database.

    """
    pagination_token: str | None = None
    while True:
        params = {"DatabaseName": database_name}
        if pagination_token:
            params["NextToken"] = pagination_token
        response: ListTablesResponseTypeDef = client.list_tables(**params)
        yield from (table["TableName"] for table in response.get("Tables", []))
        pagination_token = response.get("NextToken")
        if not pagination_token:
            break


@app.command()
def delete_tables(
    database_name: str = typer.Argument(..., help="Name of the database to delete tables from"),
    region: str = typer.Option("eu-west-1", help="AWS region for Timestream database"),
) -> None:
    """Delete all tables in a Timestream database."""
    try:
        client: TimestreamWriteClient = boto3.client("timestream-write", region_name=region)
    except NoCredentialsError as err:
        logger.error("AWS credentials not found. Please configure your AWS credentials.")
        raise typer.Exit(code=1) from err

    try:
        tables = list(list_all_tables(client, database_name))
    except ClientError as err:
        error_code = err.response.get("Error", {}).get("Code")
        if error_code == "ResourceNotFoundException":
            logger.error(f"Database '{database_name}' not found.")
            raise typer.Exit(code=1) from err
        logger.critical(f"AWS API error when listing tables: {err}")
        raise typer.Exit(code=1) from err

    if not tables:
        logger.info(f"No tables found in database '{database_name}'.")
        return

    logger.warning(f"Found {len(tables)} tables in database '{database_name}'.")
    for table in tables:
        logger.info(f" - {table}")

    if not typer.confirm(f"\nPermanently delete ALL {len(tables)} tables?", default=False):
        logger.error("Operation cancelled by user.")
        raise typer.Exit(code=1)

    for table in tables:
        try:
            logger.info(f"Deleting table '{table}'...")
            client.delete_table(DatabaseName=database_name, TableName=table)
            logger.success(f"Successfully deleted table '{table}'.")
        except ClientError as err:
            logger.error(f"Error deleting table '{table}': {err}")

    logger.success(f"Completed processing {len(tables)} tables.")


if __name__ == "__main__":
    logger.info("Starting Timestream cleanup tool")
    app()
