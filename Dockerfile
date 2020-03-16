FROM python:3.8.2

# ODBC Driver installation
RUN \
  apt-get update && apt-get install -y \
    # The first three are required for installing the ODBC Drivers
    unixodbc \
    curl \
    gnupg \
    apt-transport-https \
    ca-certificates \
    # These are python nodule dependencies
    unixodbc-dev \
    gcc \
  && \
  curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
  curl -O "https://packages.microsoft.com/debian/10/prod/pool/main/m/msodbcsql17/msodbcsql17_17.4.1.1-1_amd64.deb" && \
  ACCEPT_EULA=Y DEBIAN_FRONTEND=noninteractive dpkg -i msodbcsql17_17.4.1.1-1_amd64.deb && \
  rm -f msodbcsql17_17.4.1.1-1_amd64.deb


ENV PATH=$PATH:/sql_transfer
ENV PYTHONPATH=$PYTHONPATH:/sql_transfer

COPY sql_transfer/ /sql_transfer
COPY requirements.txt requirements.txt
COPY openssl.cnf /etc/ssl/openssl.cnf
RUN pip install -r requirements.txt && pip freeze
