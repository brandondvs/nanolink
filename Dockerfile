FROM postgres:18.3

ENV POSTGRES_USER=nanolink \
    POSTGRES_PASSWORD=nanolink \
    POSTGRES_DB=nanolink

EXPOSE 5432
