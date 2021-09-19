from sonja.worker import Worker
import asyncio
import time


def do(key):
    print('do start %s' % key)
    time.sleep(2)
    print('do end %s' % key)


class MyWorker(Worker):
    def cleanup(self):
        print('cleanup')

    async def work(self):
        loop = asyncio.get_running_loop()
        for i in range(2):
            await loop.run_in_executor(None, do, i+1)


def some_work():
    print('some_work')
    return 3


if __name__ == '__main__':
    worker = MyWorker()
    worker.post(lambda: print('lambda'))
    worker.start()
    print(worker.query(some_work))
    worker.cancel()
    worker.join()

    worker = MyWorker()
    worker.start()
    time.sleep(6)
    worker.trigger()
    time.sleep(1)
    worker.cancel()
    worker.join()
    print('joined worker')
    worker.cancel()
    worker.join()
