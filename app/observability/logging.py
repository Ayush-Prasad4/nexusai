import logging


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s %(levelname)s "
            "logger=%(name)s message=%(message)s"
        ),
    )
