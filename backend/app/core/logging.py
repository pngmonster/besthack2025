import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.contextvars.merge_contextvars,  # принимает logger, method_name, event_dict
        structlog.processors.add_log_level,       # тоже принимает три аргумента
        structlog.processors.StackInfoRenderer(), # для стеков
        structlog.processors.format_exc_info,     # для exc_info
        structlog.processors.JSONRenderer()       # финальный рендерер
    ]
)

logger = structlog.get_logger()
