from abc import abstractmethod, ABC


class ResponseGetter(ABC):
    @abstractmethod
    def get_response(self, **kwargs):
        pass

    @abstractmethod
    def get_vector(self, **kwargs):
        pass
