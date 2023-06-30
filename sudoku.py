""" sudoku.py
"""
from numpy import array, zeros

class Sudoku:
    """A class for sudoku grids: create, modify, solve, compute information...
    S = Sudoku(*args, **kwargs): Makes a sudoku grid. Positiona: or keyword args
    can be among the following *attributes*:
    m: int = 3 : height of a rectangular block. Can also be given as first integer positional arg.
    n: int = m : width of a rectangular block. Can also be given as second integer positional arg.
        The entire sudoku grid is a matrix of n x m rectangular blocks (a.k.a. regions) of size m x n.
    grid: object = zeros((m*n, m*n), int) : a 2D numpy ndarray with N x N integer elements in [0, ..., N].
        Can also be given as string or (possibly nested) list or 1D array with N*N elements,
        which, if 1D, is then reformatted to a 2D array of size N x N.
    N: int = m*n : computed from given m, n or grid. Must not be a prime number.
        If m is not given, it will be taken to be the least divisor >= sqrt(N), and n = N/m.
        (For example, if  N = 9, then  m = n = 3; if  N = 6, then  m = 3, n = 2.)
    indices: set = { 0, ..., N-1 } : for convenience.
    entries: set = { 1, ..., N } : for convenience.
    poss: dict = { (i,j): Sij ; i,j in indices }, where Sij = set of possible entries for cell (i,j)
*Methods:*
    all(): generator = (i,j) for i in indices for j in indices : all indices of the grid
    row(i): generator = (i,j) for j in indices : all indices of row i
    col(j): generator = (i,j) for i in indices : all indices of col. j
    possible(i,j): set = { possible values v that can be inserted at position (i,j) } ( = set() if grid[i,j] > 0).
    only(region: iterable): iterable = ( ((i,j), v) such that (i,j) is 
        the *only* (i,j) in region such that v is in possible(i,j) )
sible value that can be at (i,j)
    
    """
    default = {'m': 3}
    def __init__(self, *args, **kwargs):
        """Initialize a sudoku grid. Args can be:
        a) one or two integers m (= 3 by default) and n (= m by default)
           which defines the size: total width & height = m*n,
           made from n x m blocks of size (rows x cols) = m x n,
           n of which are stacked vertically and m concatenated horizontally.
           Example for (m,n)=(2,3) :  AAA BBB CCC
                                      AAA BBB CCC
                                      DDD EEE FFF
                                      DDD EEE FFF
                                      GGG HHH JJJ
                                      GGG HHH JJJ
        b) A list of lists (or 2D numpy array or matrix) which will hold
           the grid.
        """
        # first check positional args
        for i,arg in enumerate(args):
            # if there are integers, these are 'm' and then 'n',
            # and those must not be given as kwargs.
            if isinstance(arg, int):
                if 'm' not in kwargs:
                    kwargs['m'] = arg
                elif i == 0:
                    raise ValueError("Parameter m specified twice, as "
                                     "positional and as keyword argument!")
                elif 'n' not in kwargs:
                    kwargs['n'] = arg
                else:
                    raise ValueError("Too many integer parameters: found "
                                     f"argument '{arg}' in addition to "
                                     f"m = {kwargs['m']} and n = {kwargs['n']}.")
                
            # otherwise, if positional arg is not an integer,
            # it must be the 'grid', and that must not be given as kwarg:
            elif 'grid' not in kwargs:
                kwargs['grid'] = arg
            else:
                raise ValueError(f"Unrecognized positional argument '{arg}'.")

        # if the shape is given, we may need that to resize the 'grid'
        # argument conveniently. So let's complete 'n' if m was given.

        for param in 'mn':
            if param in kwargs:
                if not ( isinstance(kwargs[param], int) and kwargs[param] > 0 ):
                    raise ValueError(f"Parameter '{param}' must be an positive"
                                     f" integer, but I got {kwargs[param]}.")
                setattr(self, param, kwargs[param])
            elif 'm' in kwargs: # param not in kwarg
                self.n = self.m
    
        if 'm' in kwargs:
            self.N = self.m * self.n

        if 'grid' in kwargs:
            # it must be possible to cast it into an array.
            try: grid = array( kwargs['grid'], dtype = int )
            except:
                raise ValueError("Parameter 'grid' must be an object suitable"
                                 " for numpy.array() with dtype = int.")
            N = grid.ndim
            print(f"ndim = {N}")
            if N == 2:
                n, N = grid.shape
                if n != N:
                    raise ValueError("The grid must be a square matrix.")
                
            elif N == 1:
                # grid was given "flattened" (1D list of all elements)
                n = grid.shape[0]
                if n != (N := round(n**.5))**2:
                    raise ValueError("A sudoku grid must be square,"
                                     f" got total size {n} != N x N.")
                grid = grid.reshape((N,N))

            else:
                raise ValueError("The sudoku grid must be 2-dimensional.")

            if 'm' in kwargs:
                if self.N != N:
                    raise ValueError("The given size N = m*n is different from"
                                     " the given grid's size!")
            else:
                # N = m*n was not given, only the grid. Guess m,n.
                n = round(N**.5)
                if n*n > N: n-=1
                while n > 1 and N % n: n-=1
                if n <= 1:
                    raise ValueError(
                        f"The size {N} of the given grid can't be written as m*n!")
                print(f"Guessing that the size of the regions is {(N//n,n)}.")
                self.N, self.m, self.n = N, N // n, n

            self.grid = grid
            
        #else: grid not given
        elif 'm' in kwargs:
            self.grid = zeros((self.N, self.N), dtype=int)

        else:
            raise ValueError("Either the size or the grid must be given.")
        
    def __str__(self):
        return f"Sudoku grid of size {self.N} x {self.N} (m,n = "+\
                f"{self.m},{self.n}):\n"+str(self.grid)
    
    def __repr__(self):
        return f"Sudoku(m={self.m}, n={self.n}, grid=\n"+repr(self.grid)+")"

    def possible(self, i, j):
        "Return list of numbers that can be placed at (i,j)."
        if self.grid[i,j]: return set()
        S = set(range(1,self.N+1))
        S -= set(self.grid[i,:]) ; S -= set(self.grid[:,j])
        S -= set(self.grid[x,y] for x,y in self.region(i,j))
        return S
    
    def region(self, i, j):
        "Generator of all (x,y) in the same region as (i,j)."
        i,j = i//self.m * self.m, j//self.n * self.n
        return((x,y) for x in range(i, i + self.m)
                     for y in range(j, j + self.n))
    def row(self, i): return ((i,j) for j in range(self.N))
    def col(self, j): return ((i,j) for i in range(self.N))
    
    def all(self):
        "Generator of all indices (x,y)."
        return((x,y) for x in range(self.N) for y in range(self.N))
    def make_poss_dict(self, fill=True):
        "Make dict of possible fill's for each cell (x,y)."
        self.poss = {ij:self.possible(*ij)for ij in self.all()}
    def set(self, i, j, value):
        "Set cell i,j to value, update dict 'possible'."
        assert self.grid[i,j]==0
        self.grid[i,j] = value ; self.poss[i,j]=set()
        for x in range(self.N):
            self.poss[i,x].discard(value)
            self.poss[x,j].discard(value)
        for ij in self.region(i,j):
            self.poss[ij].discard(value)
    def only_in_range(self, rng):
        if not getattr(self,'poss',0): self.make_poss_dict()
        found={}
        for xy in rng:
            for val in (p := self.poss[xy]):
                found[val] = 0 if val in found else xy
        return { found[val]: val for val in found if found[val] }

    def find_only(self):
        for k in range(self.N):
            for rng in (self.row(k), self.col(k), self.region(k,k%self.m*self.n)):
                for xy in self.only_in_range(rng).items(): yield xy

    def solve(self):
        change = 1
        while change:
            change = 0
            for xy,z in self.find_only():
                print(end = f"{xy}={z}, "); self.set(*xy,z)
                change=1
                
S = Sudoku([[0,0,0, 4,0,0, 2,9,0],
            [7,0,2, 0,5,0, 0,8,0],
            [0,4,0, 0,0,0, 0,0,0],
            [1,0,0, 2,0,0, 5,0,0],
            [0,5,0, 8,0,3, 0,1,0],
            [0,0,7, 0,0,4, 0,0,3],
            [0,0,0, 0,0,0, 0,7,0],
            [0,7,0, 0,4,0, 1,0,6],
            [0,3,9, 0,0,6, 0,0,0]])

if 1:
    found = 1
    while found:
        found = 0
        for i in range(9):
            for j in range(9):
                if not S.grid[i,j] and len(R := S.possible(i,j))==1:
                    S[i,j] = found = min(R)
                    print(end = f"{ (i,j) } = { found }, ")
