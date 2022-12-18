from typing import Optional

import logging

logging.basicConfig(
    format="[%(name)s] (%(asctime)s) %(levelname)s:%(message)s",
    datefmt="%m/%d %I:%M:%S %p",
)


class CustomHandler:
    @staticmethod
    def development(
        name: Optional[str] = None, /, file_name: Optional[str] = None
    ) -> logging.Logger:
        new_logger = logging.getLogger(name)
        new_logger.setLevel(logging.DEBUG)

        stream_handler = logging.StreamHandler()
        new_logger.addHandler(stream_handler)

        if not file_name is None:
            file_handler = logging.FileHandler(f"logs/{file_name}")
            new_logger.addHandler(file_handler)

        return new_logger

    @staticmethod
    def production_info_level(
        name: Optional[str] = None, /, file_name: Optional[str] = None
    ) -> logging.Logger:
        new_logger = logging.getLogger(name)
        new_logger.setLevel(logging.INFO)

        stream_handler = logging.StreamHandler()
        new_logger.addHandler(stream_handler)

        if not file_name is None:
            file_handler = logging.FileHandler(f"logs/{file_name}")
            new_logger.addHandler(file_handler)

        return new_logger

    @staticmethod
    def production_warn_level(
        name: Optional[str] = None, /, file_name: Optional[str] = None
    ) -> logging.Logger:
        new_logger = logging.getLogger(name)
        new_logger.setLevel(logging.WARN)

        stream_handler = logging.StreamHandler()
        new_logger.addHandler(stream_handler)

        if not file_name is None:
            file_handler = logging.FileHandler(f"logs/{file_name}")
            new_logger.addHandler(file_handler)

        return new_logger

    @staticmethod
    def production_error_level(
        name: Optional[str] = None, /, file_name: Optional[str] = None
    ) -> logging.Logger:
        new_logger = logging.getLogger(name)
        new_logger.setLevel(logging.ERROR)

        stream_handler = logging.StreamHandler()
        new_logger.addHandler(stream_handler)

        if not file_name is None:
            file_handler = logging.FileHandler(f"logs/{file_name}")
            new_logger.addHandler(file_handler)

        return new_logger

    @staticmethod
    def file_writer(
        name: Optional[str] = None, /, file_name: Optional[str] = None
    ) -> logging.Logger:
        new_logger = logging.getLogger(name)
        new_logger.setLevel(logging.INFO)
        raw_formatter = logging.Formatter("%(message)s")
        log_formatter = logging.Formatter(
            "Deleted webhook detected [%(name)s] (%(asctime)s): %(message)s"
        )

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_formatter)
        new_logger.addHandler(stream_handler)

        if not file_name is None:
            file_handler = logging.FileHandler(f"logs/{file_name}")
            file_handler.setFormatter(raw_formatter)
            new_logger.addHandler(file_handler)

        return new_logger
