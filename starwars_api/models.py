from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        for key,value in json_data.items():
            setattr(self, key, value)
        
       

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        
        if cls.RESOURCE_NAME == 'people':
            return cls(api_client.get_people(resource_id))
        else:
            return cls(api_client.get_films(resource_id))
        raise SWAPIClientError    
        
        

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        if cls.RESOURCE_NAME == 'people':
            return PeopleQuerySet()
        else:
            return FilmsQuerySet()


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self):
        self.data = api_client._get_swapi('/api/'+self.RESOURCE_NAME)
        self.total = 0
        self.index = 0
        self.page = 1
        self.total_count = self.data["count"]
        
    def __iter__(self):
        self.total = 0
        self.index = 0
        self.page = 1
        
        return self
    
    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        
        if self.total == self.total_count:
            raise StopIteration()
        if self.index == len(self.data['results']): 
            self.page += 1
            self.index = 0
            self.data = api_client._get_swapi('/api/people',page=self.page)
        
        data = self.data['results'][self.index]
        self.index += 1
        self.total += 1
        
        if self.RESOURCE_NAME == 'people':
            return People(data)
        else:
            return Films(data)

    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
    
        count = 0
        for elem in self:
            count += 1
        return count


class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
