"""
cnf_transform.py — Transformaciones a Forma Normal Conjuntiva (CNF).
El pipeline completo to_cnf() llama a todas las transformaciones en orden.
"""

from __future__ import annotations

from src.logic_core import And, Atom, Formula, Not, Or


# --- FUNCION GUÍA SUMINISTRADA COMPLETA ---


def eliminate_double_negation(formula: Formula) -> Formula:
    """
    Elimina dobles negaciones recursivamente.

    Transformacion:
        Not(Not(a)) -> a

    Se aplica recursivamente hasta que no queden dobles negaciones.

    Ejemplo:
        >>> eliminate_double_negation(Not(Not(Atom('p'))))
        Atom('p')
        >>> eliminate_double_negation(Not(Not(Not(Atom('p')))))
        Not(Atom('p'))
    """
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Not):
        if isinstance(formula.operand, Not):
            return eliminate_double_negation(formula.operand.operand)
        return Not(eliminate_double_negation(formula.operand))
    if isinstance(formula, And):
        return And(*(eliminate_double_negation(c) for c in formula.conjuncts))
    if isinstance(formula, Or):
        return Or(*(eliminate_double_negation(d) for d in formula.disjuncts))
    return formula


# --- FUNCIONES QUE DEBEN IMPLEMENTAR ---


def eliminate_iff(formula: Formula) -> Formula:
    """
    Elimina bicondicionales recursivamente.

    Transformacion:
        Iff(a, b) -> And(Implies(a, b), Implies(b, a))

    Debe aplicarse recursivamente a todas las sub-formulas.

    Ejemplo:
        >>> eliminate_iff(Iff(Atom('p'), Atom('q')))
        And(Implies(Atom('p'), Atom('q')), Implies(Atom('q'), Atom('p')))

    Hint: Usa pattern matching sobre el tipo de la formula.
          Para cada tipo, aplica eliminate_iff recursivamente a los operandos,
          y solo transforma cuando encuentras un Iff.
    """
    # === YOUR CODE HERE ===
    from src.logic_core import Iff, Implies

    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Iff):
        left = eliminate_iff(formula.left)
        right = eliminate_iff(formula.right)
        return And(Implies(left, right), Implies(right, left))
    if isinstance(formula, Not):
        return Not(eliminate_iff(formula.operand))
    if isinstance(formula, And):
        return And(*(eliminate_iff(c) for c in formula.conjuncts))
    if isinstance(formula, Or):
        return Or(*(eliminate_iff(d) for d in formula.disjuncts))
    if isinstance(formula, Implies):
        return Implies(eliminate_iff(formula.antecedent), eliminate_iff(formula.consequent))
    return formula
    # === END YOUR CODE ===


def eliminate_implication(formula: Formula) -> Formula:
    """
    Elimina implicaciones recursivamente.

    Transformacion:
        Implies(a, b) -> Or(Not(a), b)

    Debe aplicarse recursivamente a todas las sub-formulas.

    Ejemplo:
        >>> eliminate_implication(Implies(Atom('p'), Atom('q')))
        Or(Not(Atom('p')), Atom('q'))

    Hint: Similar a eliminate_iff. Recorre recursivamente y transforma
          solo los nodos Implies.
    """
    # === YOUR CODE HERE ===
    from src.logic_core import Implies

    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Implies):
        antecedent = eliminate_implication(formula.antecedent)
        consequent = eliminate_implication(formula.consequent)
        return Or(Not(antecedent), consequent)
    if isinstance(formula, Not):
        return Not(eliminate_implication(formula.operand))
    if isinstance(formula, And):
        return And(*(eliminate_implication(c) for c in formula.conjuncts))
    if isinstance(formula, Or):
        return Or(*(eliminate_implication(d) for d in formula.disjuncts))
    return formula
    # === END YOUR CODE ===


def push_negation_inward(formula: Formula) -> Formula:
    """
    Aplica las leyes de De Morgan y mueve negaciones hacia los atomos.
    """
    if isinstance(formula, Atom):
        return formula
        
    if isinstance(formula, Not):
        operand = formula.operand
        
        # Si es Not(Not(...)), lo dejamos para que eliminate_double_negation lo limpie después,
        # pero seguimos empujando la negación hacia adentro.
        if isinstance(operand, Not):
            return Not(push_negation_inward(operand))
            
        # De Morgan: Not(And(a, b, ...)) -> Or(Not(a), Not(b), ...)
        elif isinstance(operand, And):
            return Or(*(push_negation_inward(Not(c)) for c in operand.conjuncts))
            
        # De Morgan: Not(Or(a, b, ...)) -> And(Not(a), Not(b), ...)
        elif isinstance(operand, Or):
            return And(*(push_negation_inward(Not(d)) for d in operand.disjuncts))
            
        else:
            return Not(push_negation_inward(operand))

    # Si es And o Or sin negación, solo aplicamos recursión a los hijos
    if isinstance(formula, And):
        return And(*(push_negation_inward(c) for c in formula.conjuncts))
    if isinstance(formula, Or):
        return Or(*(push_negation_inward(d) for d in formula.disjuncts))
        
    return formula


def distribute_or_over_and(formula: Formula) -> Formula:
    """
    Distribuye Or sobre And para obtener CNF.
    """
    if isinstance(formula, Atom) or isinstance(formula, Not):
        return formula
        
    if isinstance(formula, And):
        return And(*(distribute_or_over_and(c) for c in formula.conjuncts))
        
    if isinstance(formula, Or):
        disjuncts = [distribute_or_over_and(d) for d in formula.disjuncts]
        
        and_idx = -1
        for i, d in enumerate(disjuncts):
            if isinstance(d, And):
                and_idx = i
                break
                
        if and_idx != -1:
            and_node = disjuncts[and_idx]
            rest = disjuncts[:and_idx] + disjuncts[and_idx+1:]
            
            new_conjuncts = []
            for c in and_node.conjuncts:
                new_or = Or(c, *rest)
                new_conjuncts.append(distribute_or_over_and(new_or))
                
            return And(*new_conjuncts)
        else:
            return Or(*disjuncts)
            
    return formula


def flatten(formula: Formula) -> Formula:
    """
    Aplana conjunciones y disyunciones anidadas.
    """
    if isinstance(formula, Atom):
        return formula
        
    if isinstance(formula, Not):
        return Not(flatten(formula.operand))
        
    if isinstance(formula, And):
        new_conjuncts = []
        for c in formula.conjuncts:
            flat_c = flatten(c)
            if isinstance(flat_c, And):
                new_conjuncts.extend(flat_c.conjuncts)
            else:
                new_conjuncts.append(flat_c)
                
        if len(new_conjuncts) == 1:
            return new_conjuncts[0]
        return And(*new_conjuncts)
        
    if isinstance(formula, Or):
        new_disjuncts = []
        for d in formula.disjuncts:
            flat_d = flatten(d)
            if isinstance(flat_d, Or):
                new_disjuncts.extend(flat_d.disjuncts)
            else:
                new_disjuncts.append(flat_d)
                
        if len(new_disjuncts) == 1:
            return new_disjuncts[0]
        return Or(*new_disjuncts)
        
    return formula


# --- PIPELINE COMPLETO ---


def to_cnf(formula: Formula) -> Formula:
    """
    [DADO] Pipeline completo de conversion a CNF.

    Aplica todas las transformaciones en el orden correcto:
    1. Eliminar bicondicionales (Iff)
    2. Eliminar implicaciones (Implies)
    3. Mover negaciones hacia adentro (Not)
    4. Eliminar dobles negaciones (Not Not)
    5. Distribuir Or sobre And
    6. Aplanar conjunciones/disyunciones

    Ejemplo:
        >>> to_cnf(Implies(Atom('p'), And(Atom('q'), Atom('r'))))
        And(Or(Not(Atom('p')), Atom('q')), Or(Not(Atom('p')), Atom('r')))
    """
    formula = eliminate_iff(formula)
    formula = eliminate_implication(formula)
    formula = push_negation_inward(formula)
    formula = eliminate_double_negation(formula)
    formula = distribute_or_over_and(formula)
    formula = flatten(formula)
    return formula
