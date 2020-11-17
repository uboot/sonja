import asyncio
import threading
import time


class Worker(threading.Thread):
    def __init__(self):
        super().__init__()
        self.__loop = asyncio.new_event_loop()
        self.__task = None
        self.__future = None
        self.__cancelled = False

    def run(self):
        asyncio.set_event_loop(self.__loop)
        self.__loop.run_until_complete(self.__main())

    def trigger(self):
        self.__loop.call_soon_threadsafe(self.__trigger)

    def cancel(self):
        self.__loop.call_soon_threadsafe(self.__cancel)

    async def __main(self):
        if self.__cancelled:
            return

        try:
            self.__task = asyncio.create_task(self.__work())
            await self.__task
        except asyncio.CancelledError:
            pass
        finally:
            self.cleanup()

    async def __callback_wrapper(self, callback):
        return callback()

    def post(self, callback):
        self.__loop.call_soon_threadsafe(callback)

    def query(self, callback):
        return asyncio.run_coroutine_threadsafe(self.__callback_wrapper(callback), self.__loop).result()

    async def work(self):
        pass

    def cleanup(self):
        pass

    async def __work(self):
        while True:
            self.__future = self.__loop.create_future()
            await self.work()
            await self.__future

    def __cancel(self):
        self.__cancelled = True
        if self.__task:
            self.__task.cancel()

    def __trigger(self):
        self.__future.set_result(None)
