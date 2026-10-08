import time
import statistics
import threading
import multiprocessing
import urllib.request
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler


# ============================================================
# НАСТРОЙКИ
# ============================================================

FILE_NAME = "numbers.txt"

NUM_WORKERS = 4
REPEATS = 3
NUM_URLS = 20


# ============================================================
# B1. РАБОТА С 10 МЛН ЧИСЕЛ
# ============================================================

def load_numbers():
    numbers = []

    with open(FILE_NAME, "r") as file:
        for line in file:
            numbers.append(int(line))

    return numbers


# ------------------------------------------------------------
# Последовательный вариант
# ------------------------------------------------------------

def sequential_sum(numbers):
    total = 0

    for number in numbers:
        total += number

    return total


# ------------------------------------------------------------
# Потоки
# ------------------------------------------------------------

def thread_worker(numbers, start, end, results, index):
    total = 0

    for i in range(start, end):
        total += numbers[i]

    results[index] = total


def threading_sum(numbers):
    threads = []
    results = [0] * NUM_WORKERS

    chunk_size = len(numbers) // NUM_WORKERS

    for i in range(NUM_WORKERS):

        start = i * chunk_size

        if i == NUM_WORKERS - 1:
            end = len(numbers)
        else:
            end = (i + 1) * chunk_size

        thread = threading.Thread(
            target=thread_worker,
            args=(numbers, start, end, results, i)
        )

        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return sum(results)


# ------------------------------------------------------------
# Процессы
# ------------------------------------------------------------

def process_worker(numbers):
    return sum(numbers)


def multiprocessing_sum(numbers):
    chunks = []

    chunk_size = len(numbers) // NUM_WORKERS

    for i in range(NUM_WORKERS):

        start = i * chunk_size

        if i == NUM_WORKERS - 1:
            end = len(numbers)
        else:
            end = (i + 1) * chunk_size

        chunks.append(numbers[start:end])

    with multiprocessing.Pool(NUM_WORKERS) as pool:
        results = pool.map(process_worker, chunks)

    return sum(results)


# ============================================================
# ИЗМЕРЕНИЕ ВРЕМЕНИ
# ============================================================

def measure_three_times(function, *args):

    times = []
    results = []

    for i in range(REPEATS):

        start = time.perf_counter()

        result = function(*args)

        end = time.perf_counter()

        elapsed = end - start

        results.append(result)
        times.append(elapsed)

    median_time = statistics.median(times)

    return results, times, median_time


# ============================================================
# B2. СЕТЕВАЯ ЗАДАЧА
# ============================================================

class TestHTTPHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        content = (
            "Test data for Practical Work 4. "
            "Threads and processes."
        ).encode()

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/plain"
        )

        self.send_header(
            "Content-Length",
            str(len(content))
        )

        self.end_headers()

        self.wfile.write(content)

    def log_message(self, format, *args):
        pass


def start_local_server():

    server = ThreadingHTTPServer(
        ("127.0.0.1", 8000),
        TestHTTPHandler
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True
    )

    thread.start()

    return server


def download_url(url):

    with urllib.request.urlopen(
        url,
        timeout=10
    ) as response:

        data = response.read()

    return len(data)


def sequential_download(urls):

    total = 0

    for url in urls:
        total += download_url(url)

    return total


def threaded_download(urls):

    with ThreadPoolExecutor(
        max_workers=NUM_WORKERS
    ) as executor:

        results = list(
            executor.map(
                download_url,
                urls
            )
        )

    return sum(results)


def process_download(urls):

    with ProcessPoolExecutor(
        max_workers=NUM_WORKERS
    ) as executor:

        results = list(
            executor.map(
                download_url,
                urls
            )
        )

    return sum(results)


# ============================================================
# B4. РАЗДЕЛЕНИЕ ПАМЯТИ
# ============================================================

shared_list = [1, 2, 3]


def change_list_in_thread():

    shared_list.append(4)

    print(
        "В потоке список:",
        shared_list
    )


def change_list_in_process(data):

    data.append(5)

    print(
        "В процессе список:",
        data
    )


def memory_test():

    print()
    print("=" * 70)
    print("B4. РАЗДЕЛЕНИЕ ПАМЯТИ")
    print("=" * 70)

    # ========================================================
    # ПОТОК
    # ========================================================

    global shared_list

    shared_list = [1, 2, 3]

    print()
    print("ПРОВЕРКА ПОТОКА")
    print()

    print("Исходный список:")
    print(shared_list)

    thread = threading.Thread(
        target=change_list_in_thread
    )

    thread.start()
    thread.join()

    print("После работы потока:")
    print(shared_list)

    # ========================================================
    # ПРОЦЕСС
    # ========================================================

    process_list = [1, 2, 3]

    print()
    print("ПРОВЕРКА ПРОЦЕССА")
    print()

    print("Исходный список:")
    print(process_list)

    process = multiprocessing.Process(
        target=change_list_in_process,
        args=(process_list,)
    )

    process.start()
    process.join()

    print("После работы процесса:")
    print(process_list)

    # ========================================================
    # ВЫВОД
    # ========================================================

    print()
    print("Вывод:")

    print(
        "Поток изменил исходный список, "
        "потому что потоки используют "
        "общее адресное пространство."
    )

    print(
        "Процесс изменил только свою копию списка, "
        "поэтому родительский процесс "
        "не увидел изменение."
    )


# ============================================================
# B1. ЗАПУСК ТЕСТА СУММЫ
# ============================================================

def run_number_test(numbers):

    print()
    print("=" * 70)
    print("B1. СУММА 10 МЛН ЧИСЕЛ")
    print("=" * 70)

    print()
    print(
        f"Количество чисел: {len(numbers)}"
    )

    # --------------------------------------------------------
    # Последовательно
    # --------------------------------------------------------

    print()
    print("1. Последовательный способ")

    results, times, median_time = measure_three_times(
        sequential_sum,
        numbers
    )

    print(
        "Результаты:",
        results
    )

    print(
        "Время:",
        [f"{t:.4f}" for t in times]
    )

    print(
        f"Медиана: {median_time:.4f} секунд"
    )

    sequential_result = results[0]

    # --------------------------------------------------------
    # Потоки
    # --------------------------------------------------------

    print()
    print("2. 4 потока (threading)")

    results, times, median_time = measure_three_times(
        threading_sum,
        numbers
    )

    print(
        "Результаты:",
        results
    )

    print(
        "Время:",
        [f"{t:.4f}" for t in times]
    )

    print(
        f"Медиана: {median_time:.4f} секунд"
    )

    threading_result = results[0]

    # --------------------------------------------------------
    # Процессы
    # --------------------------------------------------------

    print()
    print("3. 4 процесса (multiprocessing)")

    results, times, median_time = measure_three_times(
        multiprocessing_sum,
        numbers
    )

    print(
        "Результаты:",
        results
    )

    print(
        "Время:",
        [f"{t:.4f}" for t in times]
    )

    print(
        f"Медиана: {median_time:.4f} секунд"
    )

    multiprocessing_result = results[0]

    # --------------------------------------------------------
    # Проверка
    # --------------------------------------------------------

    print()
    print("Проверка правильности:")

    if (
        sequential_result
        == threading_result
        == multiprocessing_result
    ):

        print(
            "Все способы дали одинаковую сумму."
        )

        print(
            f"Сумма: {sequential_result}"
        )

    else:

        print(
            "ОШИБКА: результаты отличаются!"
        )


# ============================================================
# B2. ЗАПУСК СЕТЕВОГО ТЕСТА
# ============================================================

def run_network_test():

    print()
    print("=" * 70)
    print("B2. СЕТЕВАЯ ЗАДАЧА — 20 URL")
    print("=" * 70)

    # --------------------------------------------------------
    # Запускаем локальный сервер
    # --------------------------------------------------------

    server = start_local_server()

    time.sleep(0.5)

    urls = [
        f"http://127.0.0.1:8000/file{i}"
        for i in range(1, NUM_URLS + 1)
    ]

    print()
    print(
        f"Количество URL: {len(urls)}"
    )

    # --------------------------------------------------------
    # Последовательно
    # --------------------------------------------------------

    print()
    print("1. Последовательно")

    start = time.perf_counter()

    result = sequential_download(urls)

    end = time.perf_counter()

    sequential_time = end - start

    print(
        f"Загружено байт: {result}"
    )

    print(
        f"Время: {sequential_time:.4f} секунд"
    )

    # --------------------------------------------------------
    # ThreadPoolExecutor
    # --------------------------------------------------------

    print()
    print("2. ThreadPoolExecutor — 4 потока")

    start = time.perf_counter()

    result = threaded_download(urls)

    end = time.perf_counter()

    threaded_time = end - start

    print(
        f"Загружено байт: {result}"
    )

    print(
        f"Время: {threaded_time:.4f} секунд"
    )

    # --------------------------------------------------------
    # ProcessPoolExecutor
    # --------------------------------------------------------

    print()
    print("3. ProcessPoolExecutor — 4 процесса")

    start = time.perf_counter()

    result = process_download(urls)

    end = time.perf_counter()

    process_time = end - start

    print(
        f"Загружено байт: {result}"
    )

    print(
        f"Время: {process_time:.4f} секунд"
    )

    # --------------------------------------------------------
    # Останавливаем сервер
    # --------------------------------------------------------

    server.shutdown()

    # --------------------------------------------------------
    # Вывод
    # --------------------------------------------------------

    print()
    print("Вывод:")

    print(
        "Для сетевых задач потоки эффективны, "
        "потому что во время ожидания I/O "
        "другой поток может выполнять работу."
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print(
        "ПРАКТИЧЕСКАЯ РАБОТА №4 — "
        "ПОТОКИ И ПРОЦЕССЫ"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # Загрузка 10 млн чисел
    # --------------------------------------------------------

    print()
    print("Загрузка numbers.txt...")

    numbers = load_numbers()

    print(
        f"Загружено чисел: {len(numbers)}"
    )

    # --------------------------------------------------------
    # B1
    # --------------------------------------------------------

    run_number_test(numbers)

    # --------------------------------------------------------
    # B2
    # --------------------------------------------------------

    run_network_test()

    # --------------------------------------------------------
    # B4
    # --------------------------------------------------------

    memory_test()

    # --------------------------------------------------------
    # Конец
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("ПРАКТИЧЕСКАЯ РАБОТА ЗАВЕРШЕНА")
    print("=" * 70)