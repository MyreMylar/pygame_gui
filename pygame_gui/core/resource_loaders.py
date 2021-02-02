import warnings

from abc import ABCMeta, abstractmethod
from typing import Tuple, Any, Union
from collections import deque

import pygame

from pygame_gui.core.utility import ClosableQueue, StoppableOutputWorker
from pygame_gui.core.utility import ImageResource, FontResource, SurfaceResource


class IResourceLoader(metaclass=ABCMeta):
    """
    Interface for a resource loader class. Resource loaders should inherit this interface.
    """

    @abstractmethod
    def add_resource(self, resource: Union[FontResource, ImageResource, SurfaceResource]):
        """
        Adds a resource to be loaded.

        :param resource:  Either an ImageResource, SurfaceResource or a FontResource.
        """

    @abstractmethod
    def start(self):
        """
        Kicks off the loading process. No more resources can be added to the loader at this point.
        """

    @abstractmethod
    def update(self) -> Tuple[bool, float]:
        """
        Updates the load process.

        :return: A Boolean indicating whether the load has finished, and a float indicating the
                 load's progress (between 0.0 and 1.0).
        """

    @abstractmethod
    def started(self) -> bool:
        """
        Tells us if the loader has already begun or finished loading.

        :return: Returns True when it's too late to add anything to the load queues.
        """


class ThreadedLoader:
    """
    A loader that uses threads to try and load data faster.

    Defaults to using five threads. Mess with it before starting the loader if you want to
    see if you can get any better loading performance with a different number.

    """
    def __init__(self):

        self.num_loading_threads = 5

        self._threaded_loading_queue = ClosableQueue()
        self._threaded_loading_done_queue = ClosableQueue()
        self._threading_error_queue = ClosableQueue()

        self._sequential_loading_queue = deque()
        self._sequential_loading_done_queue = deque()

        self._load_threads = None
        self._threaded_loading_finished = False
        self._sequential_loading_finished = False

        self._threaded_load_queue_start_length = 0
        self._sequential_load_queue_start_length = 0

        self._threads_running = False

        self._timer = pygame.time.Clock()
        self._started = False

    def started(self) -> bool:
        """
        Tells us if the loader has already begun or finished loading.

        :return: Returns True when it's too late to add anything to the load queues.
        """
        return self._started

    def add_resource(self, resource: Union[FontResource, ImageResource, SurfaceResource]):
        """
        Adds a resource to be loaded.

        Currently Fonts & Images are loaded with threads. Surfaces load sequentially after the
        images are finished because they rely on their image being loaded and it is difficult to
        guarantee that with threads.

        :param resource:  Either an ImageResource, SurfaceResource or a FontResource.
        """
        if not self._started:
            if isinstance(resource, (ImageResource, FontResource)):
                self._threaded_loading_queue.put(resource)
            else:
                self._sequential_loading_queue.append(resource)
        else:
            raise ValueError('Too late to add this resource to the loader')

    def start(self):
        """
        Kicks off the loading process. No more resources can be added to the loader at this point.

        """
        self._started = True
        self._threads_running = True
        self._threaded_loading_finished = False
        self._sequential_loading_finished = False

        self._threaded_loading_done_queue = ClosableQueue()
        self._threading_error_queue = ClosableQueue()

        self._threaded_load_queue_start_length = self._threaded_loading_queue.qsize()
        self._start_output_threads(self.num_loading_threads,
                                   ThreadedLoader._threaded_loader,
                                   self._threaded_loading_queue,
                                   self._threaded_loading_done_queue,
                                   self._threading_error_queue)

    def set_finished(self):
        pass
    # Currently we are relying on disabling the resource loader after one use to support dynamic loading
    #     self._started = False

    def _start_output_threads(self,
                              count: int,
                              func,
                              in_queue: ClosableQueue,
                              out_queue: ClosableQueue,
                              error_queue: ClosableQueue):
        self._load_threads = [StoppableOutputWorker(func=func,
                                                    in_queue=in_queue,
                                                    out_queue=out_queue,
                                                    error_queue=error_queue) for _ in range(count)]
        for thread in self._load_threads:
            thread.start()

    def _stop_threaded_loading(self):
        for _ in self._load_threads:
            self._threaded_loading_queue.close()

        # This blocks, waiting for all load threads to be finished.
        self._threaded_loading_queue.join()

        for thread in self._load_threads:
            thread.join()

        self._threads_running = False

    @staticmethod
    def _threaded_loader(loadable: Any):
        error = loadable.load()
        return loadable, error

    def _untimed_sequential_loading_update(self) -> bool:
        if not self._sequential_loading_queue:
            return True
        # No time budget so just do one update per call
        resource = self._sequential_loading_queue.popleft()
        error = resource.load()
        self._sequential_loading_done_queue.append(resource)

        if error is not None:
            warnings.warn(str(error))

        return False

    def _timed_sequential_loading_update(self, time_budget: float) -> bool:
        if not self._sequential_loading_queue:
            return True
        self._timer.tick()
        time_spent = 0.0
        while self._sequential_loading_queue and time_spent < time_budget:
            # Keep popping till we run out of time or things to pop
            resource = self._sequential_loading_queue.popleft()
            error = resource.load()
            self._sequential_loading_done_queue.append(resource)

            if error is not None:
                warnings.warn(str(error))

            time_spent += self._timer.tick()
        return False

    def _calculate_progress(self) -> float:
        if self._threaded_load_queue_start_length == self._threaded_loading_done_queue.qsize():
            self._threaded_loading_finished = True

        work_to_do = (self._threaded_load_queue_start_length +
                      self._sequential_load_queue_start_length)

        work_done = (self._threaded_loading_done_queue.qsize() +
                     len(self._sequential_loading_done_queue))

        if work_done == work_to_do:
            return 1.0
        elif work_done == 0.0:
            return 0.0
        else:
            return work_done/work_to_do


class IncrementalThreadedResourceLoader(ThreadedLoader, IResourceLoader):
    """
    This loader is designed to have it's update function called repeatedly until it is finished.

    It's useful if you want to display a loading progress bar for the UI - Though you will have to
    be careful not to use any assets that are still being loaded.

    """
    def __init__(self):
        super().__init__()

        self._time_budget = 0.02

    def set_update_time_budget(self, budget: float):
        """
        Set the minimum amount of time to spend loading, per update loop.

        Actual time spent may be somewhat over this budget as a long file load may start while we
        are within the budget.

        NOTE: This only affects sequentially loading resources.

        :param budget: A time budget in seconds. The default is 0.02 seconds.
        """
        self._time_budget = budget

    def update(self) -> Tuple[bool, float]:
        """
        Updates the load process will try to spend only as much time in here as
        allocated by the time budget.

        :return: A Boolean indicating whether the load has finished, and a float indicating the
                 load's progress (between 0.0 and 1.0).
        """
        progress = self._calculate_progress()
        if self._threaded_loading_finished and self._threads_running:
            self._stop_threaded_loading()
            self.set_finished()

            while self._threading_error_queue.qsize() > 0:
                loading_error = self._threading_error_queue.get_nowait()
                warnings.warn(str(loading_error))

        self._sequential_loading_finished = self._timed_sequential_loading_update(
            self._time_budget)

        return (self._threaded_loading_finished and self._sequential_loading_finished), progress


class BlockingThreadedResourceLoader(ThreadedLoader, IResourceLoader):
    """
    This loader is designed to have it's update function called once, after which it will
    block the main thread until all it's assigned loading is complete.

    """

    def update(self) -> Tuple[bool, float]:
        """
        Updates the load process. Blocks until it is completed.

        :return: A Boolean indicating whether the load has finished, and a float indicating the
                 load's progress (between 0.0 and 1.0).

        """
        self._stop_threaded_loading()
        while self._threading_error_queue.qsize() > 0:
            loading_error = self._threading_error_queue.get_nowait()
            warnings.warn(str(loading_error))

        while not self._sequential_loading_finished:
            self._sequential_loading_finished = self._untimed_sequential_loading_update()

        self.set_finished()

        return (self._threaded_loading_finished and self._sequential_loading_finished), 1.0
