# Kartavya Singh Singhk6 M14537829
# PL Homework 2: STIMPL
# Runtime for STIMPL

from typing import Any, Tuple, Optional

# Importing necessary modules from your implementation
from stimpl.expression import *
from stimpl.types import *
from stimpl.errors import *

"""
Interpreter State
"""

# Define the State class for maintaining the interpreter state
class State(object):
    def __init__(self, variable_name: str, variable_value: Expr, variable_type: Type, next_state: 'State') -> None:
        self.variable_name = variable_name
        self.value = (variable_value, variable_type)
        self.next_state = next_state

    def copy(self) -> 'State':
        variable_value, variable_type = self.value
        return State(self.variable_name, variable_value, variable_type, self.next_state)

    def set_value(self, variable_name, variable_value, variable_type):
        return State(variable_name, variable_value, variable_type, self)

    def get_value(self, variable_name) -> Any:
        current_state = self
        while current_state is not None:
            if isinstance(current_state, EmptyState):
                return None
            if current_state.variable_name == variable_name:
                return current_state.value
            current_state = current_state.next_state
        return None

    def __repr__(self) -> str:
        return f"{self.variable_name}: {self.value}, " + repr(self.next_state)

# Define the EmptyState class as a subclass of State
class EmptyState(State):
    def __init__(self):
        pass

    def copy(self) -> 'EmptyState':
        return EmptyState()

    def get_value(self, variable_name) -> None:
        return None

    def __repr__(self) -> str:
        return ""

"""
Main evaluation logic!
"""

# Define the evaluate function for interpreting expressions
def evaluate(expression: Expr, state: State) -> Tuple[Optional[Any], Type, State]:
    match expression:
        # Handling the Ren expression
        case Ren():
            return (None, Unit(), state)

        # Handling integer literal expression
        case IntLiteral(literal=l):
            return (l, Integer(), state)

        # Handling floating-point literal expression
        case FloatingPointLiteral(literal=l):
            return (l, FloatingPoint(), state)

        # Handling string literal expression
        case StringLiteral(literal=l):
            return (l, String(), state)

        # Handling boolean literal expression
        case BooleanLiteral(literal=l):
            return (l, Boolean(), state)

        # Handling the Print expression
        case Print(to_print=to_print):
            printable_value, printable_type, new_state = evaluate(to_print, state)

            match printable_type:
                case Unit():
                    print("Unit")
                case _:
                    print(f"{printable_value}")

            return (printable_value, printable_type, new_state)

        # Handling sequence and program expressions
        case Sequence(exprs=exprs) | Program(exprs=exprs):
            value_result = None
            value_type = Unit()
            new_state = state
            for expr in exprs:
                value_result, value_type, new_state = evaluate(expr, new_state)
            return (value_result, value_type, new_state)

        # Handling variable expression
        case Variable(variable_name=variable_name):
            value = state.get_value(variable_name)
            if value == None:
                raise InterpSyntaxError(
                    f"Cannot read from {variable_name} before assignment.")
            variable_value, variable_type = value
            return (variable_value, variable_type, state)

        # Handling assignment expression
        case Assign(variable=variable, value=value):
            value_result, value_type, new_state = evaluate(value, state)

            variable_from_state = new_state.get_value(variable.variable_name)
            _, variable_type = variable_from_state if variable_from_state else (
                None, None)

            if value_type != variable_type and variable_type != None:
                raise InterpTypeError(f"""Mismatched types for Assignment:
            Cannot assign {value_type} to {variable_type}""")

            new_state = new_state.set_value(
                variable.variable_name, value_result, value_type)
            return (value_result, value_type, new_state)

        # Handling addition expression
        case Add(left=left, right=right):
            result = 0
            left_result, left_type, new_state = evaluate(left, state)
            right_result, right_type, new_state = evaluate(right, new_state)

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Add:
            Cannot add {left_type} to {right_type}""")

            match left_type:
                case Integer() | String() | FloatingPoint():
                    result = left_result + right_result
                case _:
                    raise InterpTypeError(f"""Cannot add {left_type}s""")

            return (result, left_type, new_state)

        # Handling subtraction expression
        case Subtract(left=left, right=right):
            result = 0
            left_result, left_type, new_state = evaluate(left, state)
            right_result, right_type, new_state = evaluate(right, new_state)

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Subtract:
            Cannot subtract {left_type} from {right_type}""")

            match left_type:
                case Integer() | FloatingPoint():
                    result = left_result - right_result
                case _:
                    raise InterpTypeError(f"""Cannot subtract {left_type}s""")
            
            return (result, left_type, new_state)

        # Handling multiplication expression
        case Multiply(left=left, right=right):
            result = 0
            left_result, left_type, new_state = evaluate(left, state)
            right_result, right_type, new_state = evaluate(right, new_state)

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Multiply:
            Cannot multiply {left_type} with {right_type}""")

            match left_type:
                case Integer() | FloatingPoint():
                    result = left_result * right_result
                case _:
                    raise InterpTypeError(f"""Cannot multiply {left_type}s""")
            
            return (result, left_type, new_state)

        # Handling division expression
        case Divide(left=left, right=right):
            result = 0
            left_result, left_type, new_state = evaluate(left, state)
            right_result, right_type, new_state = evaluate(right, new_state)

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Divide:
            Cannot divide {left_type} and {right_type}""")

            if right_result == 0:
                raise InterpMathError(f"""Error with right value: Cannot divide by 0""")

            match left_type:
                case Integer():
                    result = left_result // right_result
                case FloatingPoint():
                    result = left_result / right_result
                case _:
                    raise InterpTypeError(f"""Cannot divide {left_type}s""")
            
            return (result, left_type, new_state)

        # Handling logical AND expression
        case And(left=left, right=right):
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for And:
            Cannot evaluate {left_type} and {right_type}""")
            match left_type:
                case Boolean():
                    result = left_value and right_value
                case _:
                    raise InterpTypeError(
                        "Cannot perform logical and on non-boolean operands.")

            return (result, left_type, new_state)

        # Handling logical OR expression
        case Or(left=left, right=right):
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Or:
            Cannot evaluate {left_type} or {right_type}""")
            match left_type:
                case Boolean():
                    result = left_value or right_value
                case _:
                    raise InterpTypeError(
                        "Cannot perform logical or on non-boolean operands.")

            return (result, left_type, new_state)

        # Handling logical NOT expression
        case Not(expr=expr):
            value, value_type, new_state = evaluate(expr, state)
            match value_type:
                case Boolean():
                    result = not value
                case _:
                    raise InterpTypeError(
                        "Cannot perform logical not on non-boolean operands.")

            return (result, value_type, new_state)

        # Handling IF-ELSE expression
        case If(condition=condition, true=true, false=false):
            condition_value, condition_type, new_state = evaluate(condition, state)

            if condition_type != Boolean():
                raise InterpTypeError(
                    "Condition in If statement must be of Boolean type.")

            if not condition_value:
                return evaluate(false, new_state)
            else:
                return evaluate(true, new_state)

        # Handling LESS THAN expression
        case Lt(left=left, right=right):
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Lt:
            Cannot compare {left_type} and {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value < right_value
                case Unit():
                    result = False
                case _:
                    raise InterpTypeError(
                        f"Cannot perform < on {left_type} type.")

            return (result, Boolean(), new_state)

        # Handling LESS THAN OR EQUAL TO expression
        case Lte(left=left, right=right):
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Lte:
            Cannot compare {left_type} and {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value <= right_value
                case Unit():
                    result = True
                case _:
                    raise InterpTypeError(
                        f"Cannot perform <= on {left_type} type.")

            return (result, Boolean(), new_state)

        # Handling GREATER THAN expression
        case Gt(left=left, right=right):
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Gt:
            Cannot compare {left_type} and {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value > right_value
                case Unit():
                    result = False
                case _:
                    raise InterpTypeError(
                        f"Cannot perform > on {left_type} type.")

            return (result, Boolean(), new_state)

        # Handling GREATER THAN OR EQUAL TO expression
        case Gte(left=left, right=right):
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Gte:
            Cannot compare {left_type} and {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value >= right_value
                case Unit():
                    result = True
                case _:
                    raise InterpTypeError(
                        f"Cannot perform >= on {left_type} type.")

            return (result, Boolean(), new_state)

        # Handling EQUAL TO expression
        case Eq(left=left, right=right):
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Eq:
            Cannot compare {left_type} and {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value == right_value
                case Unit():
                    result = True
                case _:
                    raise InterpTypeError(
                        f"Cannot perform == on {left_type} type.")

            return (result, Boolean(), new_state)

        # Handling NOT EQUAL TO expression
        case Ne(left=left, right=right):
            left_value, left_type, new_state = evaluate(left, state)
            right_value, right_type, new_state = evaluate(right, new_state)

            result = None

            if left_type != right_type:
                raise InterpTypeError(f"""Mismatched types for Ne:
            Cannot compare {left_type} and {right_type}""")

            match left_type:
                case Integer() | Boolean() | String() | FloatingPoint():
                    result = left_value != right_value
                case Unit():
                    result = False
                case _:
                    raise InterpTypeError(
                        f"Cannot perform != on {left_type} type.")

            return (result, Boolean(), new_state)

        # case While(condition=condition, body=body):
        #     condition_value, condition_type, new_state = evaluate(condition, state)

        #     if condition_type != Boolean():
        #         raise InterpTypeError(
        #             "Condition in While loop must be of Boolean type.")

        #     while condition_value:
        #         body_value, body_type, new_state = evaluate(body, new_state)
        #         condition_value, _, new_state = evaluate(condition, new_state)

        #     return (None, Unit(), new_state)
        #Handling While loop expression
        case While(condition=condition, body=body):
            condition_value, condition_type, new_state = evaluate(condition, state)
            body_value = None
            body_type = Unit()
            if condition_type != Boolean():
                raise InterpTypeError(
                    "Condition in While loop must be of Boolean type.")

            while condition_value:
                body_value, body_type, new_state = evaluate(body, new_state)
                condition_value, _, new_state = evaluate(condition, new_state)

            return (body_value, body_type, new_state)  # Use the final state of the while loop

        case _:
            raise InterpSyntaxError("Unhandled!")
    pass

# Define the run_stimpl function for running STIMPL programs
def run_stimpl(program, debug=False):
    state = EmptyState()
    program_value, program_type, program_state = evaluate(program, state)

    if debug:
        print(f"program: {program}")
        print(f"final_value: ({program_value}, {program_type})")
        print(f"final_state: {program_state}")

    return program_value, program_type, program_state