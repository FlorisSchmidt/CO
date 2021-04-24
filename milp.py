import gurobipy as gp
import classes
import functions

def solve(instance):
    solution = classes.Solution(instance.Days)