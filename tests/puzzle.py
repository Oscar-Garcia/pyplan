# -*- coding: utf-8 -*-
import random


class Puzzle(object):
    """
    This class represents a N-Puzzle.

    Attributes:
        height(int): The puzzle height.
        width(int): The puzzle width.
        _puzzle(list): Internal representation of the puzzle.
    """
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'
    BLANK = 0  # This is the blank or missing tile, where movements can be performed.

    movements = (UP, DOWN, LEFT, RIGHT,)

    def __init__(self, height: int, width: int, puzzle: list=None):
        """
        Generates a puzzle of size height x width.
        """
        self._puzzle = puzzle or self.generate_puzzle(height, width)
        assert isinstance(self._puzzle, list)
        self.height = height
        self.width = width

    def generate_puzzle(self, height: int, width: int):
        """
        Generates a solved puzzle (if we consider BLANK to be 0).
        """
        assert height > 1
        assert width > 1

        self.height = height
        self.width = width
        return [x for x in range(height*width)]

    def get_tile(self, col, row):
        """
        Gets the content of a tile.
        """
        return self._puzzle[row*self.width + col]

    def shuffle(self, steps=1, seed=None):
        """
        Shuffle the puzzle making steps movements.
        Parameters:
            steps(int): Maximun number of movements for shuffling.
            seed(int): An initial random seed.
        """
        rand = random.Random()
        if seed is not None:
            rand.seed(seed)
        for _ in range(0, steps):
            self.random_move(rand)
        return self._puzzle

    def random_move(self, rand):
        """
        Performs a random possible move.
        """
        random_movements = list(self.movements)
        rand.shuffle(random_movements)
        for movement in random_movements:
            if self.can_move(movement):
                return self._move(movement, self._puzzle)

    def is_solved(self):
        """
        Checks if the puzzle is already solved.
        """
        for i in range(self.size):
            if i != self._puzzle[i]:
                return False
        return True

    def _move(self, movement, puzzle, first_position=None):
        first_position = first_position or self.get_blank_position(puzzle)
        if movement == self.UP:
            second_position = first_position - self.width
        elif movement == self.DOWN:
            second_position = first_position + self.width
        elif movement == self.LEFT:
            second_position = first_position - 1
        elif movement == self.RIGHT:
            second_position = first_position + 1
        second = puzzle[second_position]
        first = puzzle[first_position]
        puzzle[first_position] = second
        puzzle[second_position] = first
        return puzzle

    def move(self, movement, first_position=None):
        return Puzzle(self.height, self.width, self._move(movement, list(self._puzzle), first_position))

    def get_position(self, tile, puzzle=None):
        puzzle = puzzle or self._puzzle
        return puzzle.index(tile)

    def get_coordinates(self, position):
        """
        Gets the row and the col for a given position.
        Parameters:
            position(int): An index on the puzzle array.
        Returns:
            (int, int): A row and col pair.
        """
        return position % self.width, position//self.width

    @property
    def size(self):
        return self.height*self.width

    def get_blank_position(self, puzzle=None):
        return self.get_position(self.BLANK, puzzle)

    def can_move(self, movement, position=None):
        """
        Checks if the given movement is possible or not.
        """
        position = position or self.get_blank_position()
        if movement == self.UP:
            return position > self.width
        elif movement == self.DOWN:
            return position < ((self.height - 1) * self.width)
        elif movement == self.LEFT:
            return position % self.width > 0
        elif movement == self.RIGHT:
            return (position + 1) % self.width > 0
        else:
            raise ValueError(movement)

    def to_list(self):
        return self._puzzle

    def __str__(self):
        return str([self._puzzle[i*self.width:(i*self.width + self.width)] for i in range(0, self.height)])
