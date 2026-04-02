import numpy as np
import time as time
from loom.pool import InterpreterPool
from loom.dispatcher import Dispatcher
from loom.future import LoomFuture


def process_image(image):
    gray = np.mean(image, axis = 2)
    return gray

def main():
    images = []
    gray_images = []

    for _ in range(100):
        image = np.random.randint(0, 255, (256, 256, 3), dtype = np.uint8)
        images.append(image)

    sc_start = time.time()

    for image in images:
        gray_image = process_image(image)
        gray_images.append(gray_image)

    sc_end = time.time()

    print(f"Single Core: {sc_end - sc_start:.4f} seconds")

    loom_start = time.time()

    with InterpreterPool(4) as r:
        dispatcher = Dispatcher(r)

        futures = []
        for image in images:
            future = dispatcher.submit(process_image, (image,))
            futures.append(future)

        loom_results = []
        for future in futures:
            future.wait()
            loom_results.append(future.result())

    loom_end = time.time()
    
    print(f"Loom: {loom_end - loom_start:.4f} seconds")

main()  