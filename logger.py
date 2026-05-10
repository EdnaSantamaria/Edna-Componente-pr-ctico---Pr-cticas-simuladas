"""Configuración centralizada de logs en archivo."""
import logging
from pathlib import Path

LOG_FILE = Path(__file__).parent / "eventos.log"

logging.basicConfig(
    filename=str(LOG_FILE),
    filemode="a",
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)


def get_logger(nombre: str) -> logging.Logger:
    return logging.getLogger(nombre)