# Docker SQL Transfer

A docker image for transferring data from one database to another.

# Support

Currently supports transfers to and from SQL Server, Postgres, and MySQL databases.

# How to use

```bash
docker pull dbeachnau/sql_transfer
doker run dbeachnau/sql_transfer \
    {from_connection_string} \
    {to_connection_string} \
    {sql} \
    {destination_table} \
    {mode}[optional]
```

Connection strings should follow SQLAlchemy's [specification](https://docs.sqlalchemy.org/en/13/core/engines.html), since that is what is doing the heavy lifting behind the scenes. This also means that we can leverage some of the quality of life features which SQLAlchemy provides. For example, it is not necessary to have the destination table to exist since SQLAlchemy will create the table for the user. However, there are some drawbacks to SQLAlchemy as well. In some (many) cases it is not the most optimal in raw performance. When inserting into a Postgres database, for example, it is often many magnitudes faster to use psycopg2's `execute_values` function.