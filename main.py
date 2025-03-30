import asyncio

import shutil
import argparse
import logging
from pathlib import Path

# Налаштовуємо логування
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def copy_file(file_path: Path, output_folder: Path):
    """Асинхронно копіює файл до папки на основі розширення."""
    try:
        ext = (
            file_path.suffix[1:] or "unknown"
        )  # Отримуємо розширення файлу, якщо немає — "unknown"
        target_dir = output_folder / ext
        target_dir.mkdir(
            parents=True, exist_ok=True
        )  # Створюємо папку, якщо її не існує
        target_path = target_dir / file_path.name

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, shutil.copy2, file_path, target_path
        )  # Копіюємо файл

        logging.info(f"Скопійовано {file_path} -> {target_path}")
    except Exception as e:
        logging.error(f"Помилка при копіюванні {file_path}: {e}")


async def read_folder(source_folder: Path, output_folder: Path):
    """Асинхронно читає файли та копіює їх до відповідних папок."""
    tasks = []
    for file_path in source_folder.rglob("*"):  # Рекурсивно шукаємо файли
        if file_path.is_file():
            tasks.append(copy_file(file_path, output_folder))

    await asyncio.gather(*tasks)  # Запускаємо копіювання файлів асинхронно


def parse_arguments():
    """Обробляє аргументи командного рядка."""
    parser = argparse.ArgumentParser(
        description="Асинхронне копіювання файлів за розширеннями."
    )
    parser.add_argument("source", type=str, help="Папка-джерело файлів")
    parser.add_argument(
        "output", type=str, help="Папка для відсортованих файлів"
    )
    return parser.parse_args()


async def main():
    """Головна асинхронна функція."""
    args = parse_arguments()
    source_folder = Path(args.source)
    output_folder = Path(args.output)

    if not source_folder.exists() or not source_folder.is_dir():
        logging.error(
            f"Вихідна папка '{source_folder}' не існує "
            f"або не є директорією."
        )
        return

    output_folder.mkdir(
        parents=True, exist_ok=True
    )  # Створюємо вихідну папку, якщо її немає

    await read_folder(source_folder, output_folder)  # Запускаємо сортування


if __name__ == "__main__":
    asyncio.run(main())  # Запускаємо головний цикл
