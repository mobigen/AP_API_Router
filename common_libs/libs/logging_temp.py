log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"default": {"format": "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] - %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "level": "DEBUG", "formatter": "default"}},
    "loggers": {"local": {"level": "DEBUG", "handlers": ["console"], "propagate": True}},
}
