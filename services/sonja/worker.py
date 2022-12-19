import asyncio
import threading
from typing import Optional


class Worker(threading.Thread):
    def __init__(self):
        super().__init__()
        self.__loop = asyncio.new_event_loop()
        self.__task = None
        self.__future = None
        self.__cancelled = False
        self.__semaphore = threading.Semaphore(0)
        self.__is_paused = False

    def run(self):
        asyncio.set_event_loop(self.__loop)
        self.__loop.run_until_complete(self.__main())

    def trigger(self, payload=None):
        self.__loop.call_soon_threadsafe(self.__trigger, payload)

    def reschedule_internally(self, delay_in_seconds, payload=None):
        self.__loop.call_later(delay_in_seconds, self.__trigger, payload)

    def cancel(self):
        self.__loop.call_soon_threadsafe(self.__cancel)
        self.resume()

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

    def try_pause(self, timeout: Optional[int] = None) -> bool:
        if self.__semaphore.acquire(timeout=timeout):
            self.__is_paused = True
            return True
        
        return False

    def resume(self):
        if self.__is_paused:
            self.__semaphore.release()
            self.__is_paused = False

    async def work(self, payload):
        pass

    def cleanup(self):
        pass

    async def __work(self):
        initial_iteration = True
        payload = None
        while True:
            # acquire the semaphore while working
            if initial_iteration:
                # when entering the loop the semaphore has already been acquired
                # by the constructor
                initial_iteration = False
            else:
                self.__semaphore.acquire()

            self.__future = self.__loop.create_future()

            await self.work(payload)

            # now release the semaphore
            self.__semaphore.release()

            # wait for trigger() or a scheduled wake-up
            payload = await self.__future

    def __cancel(self):
        self.__cancelled = True
        if self.__task:
            self.__task.cancel()

    def __trigger(self, payload):
        self.__future.set_result(payload)
