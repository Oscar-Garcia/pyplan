# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from collections import ChainMap, UserDict

from .decorators import inherit_doc


class ScopeNotFoundError(Exception):
    def __init__(self, scope_id):
        super().__init__()
        self.scope_id = scope_id

    def __repr__(self):
        return "Scope with id %s not found." % self.scope_id


class CollectionMap(ABC):
    """
    This abstract class represents a Key-Value collection of records.
    Different implementations of this class allow to query and save the information using different
    persistence methods (files, databases, ...)
    """

    @abstractmethod
    def all_keys(self):
        """
        Get all keys of the values stored in the collection.

        Returns:
            (iterator): An iterator over all the keys in the collection.
        """
        raise NotImplementedError()

    @abstractmethod
    def insert_record(self, key, record):
        """
        Appends a new record to the collection.

        Parameters:
            key(object): The identifier used for the record.
            record(object): The new record to append.

        Returns:
            object: The appended record.
        """
        raise NotImplementedError()

    @abstractmethod
    def put_record(self, key, record):
        """
        Updates an existing record on the collection.

        Parameters:
            record(object): The record to be updated.

        Returns:
            object: The updated record.
        """
        raise NotImplementedError()

    @abstractmethod
    def next_id(self):
        """
        Generates the key for the next node to insert.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_record(self, key):
        """
        Finds a record on the collection given its key.
        """
        raise NotImplementedError()


@inherit_doc  # pylint: disable=too-many-ancestors
class MemoryCollectionMap(UserDict, CollectionMap):
    """
    A `CollectionMap` whose records are maintained in memory.
    """
    def all_keys(self):
        return iter(self)

    def insert_record(self, key, record):
        self[key] = record

    def put_record(self, key, record):
        self[key] = record

    def next_id(self):
        return len(self)

    def get_record(self, key):
        return self[key]


class ScopeStore(ABC):
    """
    A store for `CollectionMap`.
    Allows the creation and deletion of collections as needed.
    """

    @abstractmethod
    def create_scope(self, scope_id: object, parent_id: object=None) -> CollectionMap:
        """
        Creates a new `CollectionMap` for a new context or scope.
        Parameters:
            scope_id(object): Is an identifier of the new scope that will be created.
            parent(object): Is the identifier of the parent scope collection with the current data.
                If no identifier is provided init scope will be used as parent.
        Returns:
            CollectionMap: A new collection.
        """
        raise NotImplementedError()

    @abstractmethod
    def delete_scope(self, scope_id: object):
        """
        Releases the resources of a scope collection.
        Parameters:
            scope_id(int): Is an identifier of the collection to delete.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def init(self) -> CollectionMap:
        """
        Gets the initial collection scope.
        """
        raise NotImplementedError()

    @abstractmethod
    def get_scope(self, scope_id: object) -> CollectionMap:
        """
        Gets the scope with the given id.
        Returns:
            CollectionMap: The collection for the given id.
        Raises:
            ScopeNotFoundError: In the case there is no scope with the given id.
        """
        raise NotImplementedError()


@inherit_doc  # pylint: disable=too-many-ancestors
class ChainCollectionMap(CollectionMap):
    """
    A `CollectionMap` whose records are maintained in memory.
    """
    def __init__(self, chain):
        self.chain = chain

    def all_keys(self):
        return iter(self.chain)

    def insert_record(self, key, record):
        self.chain[key] = record

    def put_record(self, key, record):
        self.chain[key] = record

    def next_id(self):
        return len(self.chain)

    def get_record(self, key):
        return self.chain[key]


@inherit_doc
class ChainScopeStore(ScopeStore):
    """
    This is a store of collections where all the collections are chained using a `ChainMap`.
    """

    def __init__(self, init=None, factory=None):
        self.factory = factory or get_default_collection_factory()
        self.collections = {}
        self._init = init or self.factory()

    @property
    def init(self) -> CollectionMap:
        return self._init

    def create_scope(self, scope_id: object, parent_id: object=None) -> CollectionMap:
        new_scope = self.factory()
        if parent_id:
            parent = self.collections[parent_id]
            chain_map = ChainCollectionMap(parent.chain.new_child(new_scope))
        else:
            chain_map = ChainCollectionMap(ChainMap(new_scope, self.init))
        self.collections[scope_id] = chain_map
        return chain_map

    def delete_scope(self, scope_id: object):
        self.collections.pop(scope_id)

    def get_scope(self, scope_id: object) -> CollectionMap:
        try:
            return self.collections[scope_id]
        except KeyError:
            raise ScopeNotFoundError(scope_id)


@inherit_doc
class NoScopeStore(ScopeStore):
    """
    This is a store for those problems whose solving do not need backtrack so it is not needed
    to manage different scopes.
    """
    def __init__(self, init=None, factory=None):
        self.factory = factory or get_default_collection_factory()
        self._init = init or self.factory()

    @property
    def init(self) -> CollectionMap:
        return self._init

    def create_scope(self, scope_id: object, parent_id: object=None) -> CollectionMap:
        return self.init

    def delete_scope(self, scope_id: object):
        pass

    def get_scope(self, scope_id: object) -> CollectionMap:
        return self._init


def get_default_collection_factory():
    return MemoryCollectionMap


def get_default_collection():
    return get_default_collection_factory()()


def get_default_scope_store():
    return ChainScopeStore()
