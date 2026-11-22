FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd --gid 1000 atlas \
    && useradd --uid 1000 --gid atlas --create-home atlas \
    && mkdir -p /app/data/raw /app/data/processed \
    && chown -R atlas:atlas /app/data

COPY apps/collector/ /app/apps/collector/
COPY apps/web/ /app/apps/web/
COPY apps/planner/ /app/apps/planner/
COPY apps/admin/ /app/apps/admin/
COPY docs/proposta-brs-bhls/estudos/rede-integrada-2026-11-21/ /app/docs/proposta-brs-bhls/estudos/rede-integrada-2026-11-21/
COPY docs/proposta-brs-bhls/revisao-atual/ /app/docs/proposta-brs-bhls/revisao-atual/

USER atlas
EXPOSE 8000
STOPSIGNAL SIGINT

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python3", "-c", "from urllib.request import urlopen; urlopen('http://127.0.0.1:8000/api/status', timeout=3).close()"]

CMD ["python3", "apps/collector/server.py", "--host", "0.0.0.0", "--port", "8000"]
