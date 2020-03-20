import click
import pandas as pd
from sqlalchemy import create_engine
import logging
from contextlib import closing

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


def transfer(
    from_conn_string,
    to_conn_string,
    sql,
    destination_table,
    mode,
    schema=None
):
    """
    Transfers data from one database to another.
    """
    from_engine = create_engine(from_conn_string).execution_options()
    with closing(from_engine.connect()) as conn:
        results = pd.read_sql(sql, conn)

    log.info(f"{results.shape[0]} rows and {results.shape[1]} columns in results from executing query:\n{sql}")
    log.info(f"{results.head(5)}")
    log.info(f"{results.tail(5)}")
    log.info(results.info())

    if results.shape[0] > 0:
        log.info(f"Inserting data into table {destination_table} using mode {mode} in schema {schema or '{no schema specified - using database default}'}")
        to_engine = create_engine(to_conn_string)

        with closing(to_engine.connect()) as conn:
            results.to_sql(destination_table, conn, if_exists=mode, index=False, schema=schema)
    else:
        log.info("There were no results, skipping data insertion.")


@click.command()
@click.option('-f', '--from-conn-string', required=True, type=str,
              help="SQL Alchemy connection string for source database.")
@click.option('-t', '--to-conn-string', required=True, type=str,
              help="SQL Alchemy connection string for destination database.")
@click.option('-s', '--sql', required=True, type=str,
              help="SQL Query.")
@click.option('-d', '--destination-table', required=True, type=str,
              help="Table that the data should be inserted into.")
@click.option('-m', '--mode', default='append', type=click.Choice(['fail', 'replace', 'append'], case_sensitive=False),
              help="How to insert the data if the table already exists.")
@click.option('--schema', default=None)
def transfer_cmd(
        from_conn_string,
        to_conn_string,
        sql,
        destination_table,
        mode,
        schema
):
    print(from_conn_string)
    transfer(from_conn_string, to_conn_string, sql, destination_table, mode, schema)


if __name__ == '__main__':
    transfer_cmd()


# from_conn_string="DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.2.41;DATABASE=MPC;UID=appguest;"