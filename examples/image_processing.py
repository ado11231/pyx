# Benchmarks single-core vs nopickle parallel processing on 100 synthetic images
import numpy as np
import time as time
from nopickle.pool import InterpreterPool
from nopickle.dispatcher import Dispatcher
from nopickle.future import NopickleFuture

def simple_process_image(image):
    gray = np.mean(image, axis=2)
    return gray

def heavy_process_image(image):
    gray = np.mean(image, axis=2)
    for _ in range(100):
        gray = np.sqrt(np.abs(gray * 1.1 + gray / 1.5))
    return gray

def main():
    images = []
    gray_images = []
    for _ in range(100):
        image = np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)
        images.append(image)

    sc_start = time.time()
    for image in images:
        gray_image = heavy_process_image(image)
        gray_images.append(gray_image)
    sc_end = time.time()
    print(f"Single Core: {sc_end - sc_start:.4f} seconds")

    nopickle_start = time.time()
    with InterpreterPool(4) as r:
        dispatcher = Dispatcher(r)
        futures = []
        for image in images:
            future = dispatcher.submit(heavy_process_image, (image,))
            futures.append(future)
        nopickle_results = []
        for future in futures:
            nopickle_results.append(future.result())
        dispatcher.shutdown()
    nopickle_end = time.time()
    print(f"Nopickle: {nopickle_end - nopickle_start:.4f} seconds")

main()
