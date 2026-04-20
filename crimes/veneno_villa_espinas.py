"""
veneno_villa_espinas.py — El Veneno de Villa Espinas

La víctima fue encontrada muerta en la biblioteca con arsénico en su copa de vino.
El frasco de arsénico hallado en la bodega es el arma del crimen.
Las huellas dactilares de Reynaldo están en ese frasco.
Pablo estaba podando en el jardín exterior durante toda la noche; no pudo haber accedido a la bodega.
Bernardo estaba en el garaje durante toda la noche; tampoco pudo haber accedido a la bodega.
Pablo acusa directamente a Reynaldo.
Margot declara que Reynaldo estuvo con ella en la cocina toda la noche.
Reynaldo declara que Margot estuvo con él en la cocina toda la noche.
Reynaldo no tiene coartada verificada por ningún testigo independiente.

Como detective, he llegado a las siguientes conclusiones:
Quien tiene huellas en el arma del crimen tiene evidencia directa en su contra.
Quien estuvo lejos de la escena durante el crimen está descartado como culpable.
El testimonio de alguien descartado como culpable es confiable.
Quien tiene evidencia directa en su contra y no tiene coartada verificada es culpable.
Quien da coartada a un culpable lo está encubriendo.
Si dos personas se dan coartada mutuamente, existe una coartada cruzada entre ellas.
"""

from src.crime_case import CrimeCase, QuerySpec
from src.predicate_logic import ExistsGoal, KnowledgeBase, Predicate, Rule, Term


def crear_kb() -> KnowledgeBase:
    """Construye la KB según la narrativa del módulo."""
    kb = KnowledgeBase()

    # Constantes del caso
    reynaldo       = Term("reynaldo")
    margot         = Term("margot")
    pablo          = Term("pablo")
    bernardo       = Term("bernardo")
    frasco_arsenico = Term("frasco_arsenico")

    # =========================
    # HECHOS
    # =========================

    # Evidencia física: Reynaldo tiene huellas en el arma
    kb.add_fact(Predicate("huellas_en", (reynaldo, frasco_arsenico)))

    # Ubicaciones: Pablo y Bernardo estaban lejos de la escena
    kb.add_fact(Predicate("alejado_escena", (pablo,)))
    kb.add_fact(Predicate("alejado_escena", (bernardo,)))

    # Testimonios
    kb.add_fact(Predicate("acusa", (pablo, reynaldo)))

    # Coartadas (mutuas)
    kb.add_fact(Predicate("coartada", (margot, reynaldo)))
    kb.add_fact(Predicate("coartada", (reynaldo, margot)))

    # Reynaldo no tiene coartada verificada
    kb.add_fact(Predicate("no_coartada_verificada", (reynaldo,)))

    # =========================
    # REGLAS
    # =========================

    # 1. Huellas en el arma → evidencia directa
    kb.add_rule(Rule(
        head=Predicate("evidencia_directa", (Term("$X"),)),
        body=(Predicate("huellas_en", (Term("$X"), Term("$Y"))),)
    ))

    # 2. Alejado de la escena → descartado
    kb.add_rule(Rule(
        head=Predicate("descartado", (Term("$X"),)),
        body=(Predicate("alejado_escena", (Term("$X"),)),)
    ))

    # 3. Testimonio confiable:
    # Si alguien está descartado y acusa a otro → su testimonio es confiable
    kb.add_rule(Rule(
        head=Predicate("testimonio_confiable", (Term("$X"), Term("$Y"))),
        body=(
            Predicate("descartado", (Term("$X"),)),
            Predicate("acusa", (Term("$X"), Term("$Y")))
        )
    ))

    # 4. Evidencia directa + sin coartada verificada → culpable
    kb.add_rule(Rule(
        head=Predicate("culpable", (Term("$X"),)),
        body=(
            Predicate("evidencia_directa", (Term("$X"),)),
            Predicate("no_coartada_verificada", (Term("$X"),))
        )
    ))

    # 5. Dar coartada a un culpable → encubridor
    kb.add_rule(Rule(
        head=Predicate("encubridor", (Term("$Y"),)),
        body=(
            Predicate("coartada", (Term("$Y"), Term("$X"))),
            Predicate("culpable", (Term("$X"),))
        )
    ))

    # 6. Coartadas cruzadas
    kb.add_rule(Rule(
        head=Predicate("coartada_cruzada", (Term("$X"), Term("$Y"))),
        body=(
            Predicate("coartada", (Term("$X"), Term("$Y"))),
            Predicate("coartada", (Term("$Y"), Term("$X")))
        )
    ))

    return kb


CASE = CrimeCase(
    id="veneno_villa_espinas",
    title="El Veneno de Villa Espinas",
    suspects=("reynaldo", "margot", "pablo", "bernardo"),
    narrative=__doc__,
    description=(
        "La víctima fue envenenada con arsénico. "
        "El mayordomo tiene las huellas en el frasco y solo cuenta con la coartada de la cocinera, "
        "quien a su vez solo cuenta con la de él. Razona sobre evidencia física, testimonios "
        "confiables y encubrimiento."
    ),
    create_kb=crear_kb,
    queries=(
        QuerySpec(
            description="¿Pablo está descartado como culpable?",
            goal=Predicate("descartado", (Term("pablo"),)),
        ),
        QuerySpec(
            description="¿El testimonio de Pablo contra Reynaldo es confiable?",
            goal=Predicate("testimonio_confiable", (Term("pablo"), Term("reynaldo"))),
        ),
        QuerySpec(
            description="¿Reynaldo es culpable?",
            goal=Predicate("culpable", (Term("reynaldo"),)),
        ),
        QuerySpec(
            description="¿Margot está encubriendo al culpable?",
            goal=Predicate("encubridor", (Term("margot"),)),
        ),
        QuerySpec(
            description="¿Existe coartada cruzada entre Margot y Reynaldo?",
            goal=ExistsGoal("$X", Predicate("coartada_cruzada", (Term("$X"), Term("reynaldo")))),
        ),
    ),
)
