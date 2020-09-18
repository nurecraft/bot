FROM python:3.8 as production
LABEL maintainer="Dmytro Hoi <code@dmytrohoi.com>" \
      description="NURECRAFT Bot"

ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV PATH "/app/scripts:${PATH}"

EXPOSE 80
WORKDIR /app

COPY Pipfile* /app/
RUN pip install pipenv && \
    pipenv install --system --deploy
ADD . /app/
RUN chmod +x scripts/*

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["run-polling"]
