"""
By Filipe Chagas
June-2022
"""

from typing import *
from subsimulation import SubSimulationEnv, ContextType

class MonteCarloSimulationEnv():
    def __init__(self, variables: List[Tuple[str, type, object]], n_subsimulations: int, n_steps: int) -> None:
        assert isinstance(n_subsimulations, int), f'Argument of \'n_subsimulations\' must be integer. Given {type(n_subsimulations)}.'
        assert n_subsimulations > 0, f'n_subsimulations must be positive. Given {n_subsimulations}.'
        assert isinstance(n_steps, int), f'Argument of \'n_steps\' must be integer. Given {type(n_steps)}.'
        assert n_steps > 0, f'n_steps must be positive. Given {n_steps}.'
        assert isinstance(variables, list), f'Argument of \'variables\' must be a list, but a {type(variables)} object was received.'
        assert all([isinstance(var_name, str) for var_name, var_type, var_default in variables]), f'\'variables\' list must be in the format [(string, type, object)].'
        assert all([isinstance(var_type, type) for var_name, var_type, var_default in variables]), f'\'variables\' list must be in the format [(string, type, object)].'
        assert all([isinstance(var_default, var_type) for var_name, var_type, var_default in variables]), f'Some default value in \'variables\' list does not correspond to its variable\'s type.'
        assert all([var_name not in ('past', 'getstate', 'setstate') for var_name, var_type, var_default in variables]), 'Names \'past\', \'getstate\' and \'setstate\' are internally reserved and forbidden for variables.'
        
        self._variables = variables
        self._n_subsims = n_subsimulations
        self._n_steps = n_steps
        self._subsim_begin_function = None
        self._subsim_step_function = None
        self._subsim_envs = None

    def subsim_begin(self) -> Callable:
        """Returns a decorator that subscribes a function as the beginning function of all subsimulations.

        Returns:
            Callable: Wrapped decorator.
        """
        def wrapped(function: Callable[[ContextType], None]) -> Callable:
            self._subsim_begin_function = function
            return function
        return wrapped

    def subsim_step(self) -> Callable:
        """Returns a decorator that subscribes a function as the step-function of all subsimulations.

        Returns:
            Callable: Wrapped decorator.
        """
        def wrapped(function: Callable[[ContextType], None]) -> Callable:
            self._subsim_step_function = function
            return function
        return wrapped

    def run(self):
        """Run all the independent subsimulations.
        """
        self._subsim_envs = [SubSimulationEnv(self._variables, self._subsim_begin_function, self._subsim_step_function) for i in range(self._n_subsims)]
        
        for env in self._subsim_envs:
            env.run_steps(self._n_steps)