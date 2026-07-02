import ast
import operator
from typing import Any

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models import ParameterCalculation, ParameterCalculationSource, RekamPasienParameter


ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _evaluate_node(node: ast.AST, variables: dict[str, float]) -> float:
    if isinstance(node, ast.Expression):
        return _evaluate_node(node.body, variables)

    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)

    if isinstance(node, ast.Name):
        if node.id not in variables:
            raise ValueError(f"Variable '{node.id}' tidak ditemukan")
        return variables[node.id]

    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        left = _evaluate_node(node.left, variables)
        right = _evaluate_node(node.right, variables)
        return ALLOWED_OPERATORS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
        return ALLOWED_OPERATORS[type(node.op)](_evaluate_node(node.operand, variables))

    raise ValueError("Formula hanya boleh berisi angka, variable, dan operator + - * / **")


def evaluate_formula(formula: str, variables: dict[str, float]) -> float:
    try:
        parsed = ast.parse(formula, mode="eval")
        return _evaluate_node(parsed, variables)
    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="Formula kalkulasi menghasilkan pembagian dengan nol")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Formula kalkulasi tidak valid: {exc}")


def sync_parameter_calculation(db: Session, target_parameter_id: int, calculation_payload: Any | None):
    existing = (
        db.query(ParameterCalculation)
        .options(joinedload(ParameterCalculation.sources))
        .filter(
            ParameterCalculation.target_parameter_id == target_parameter_id,
        )
        .first()
    )

    if calculation_payload is None:
        if existing:
            existing.deleted_at = func.now()
        return

    variables = {}
    for source in calculation_payload.sources:
        if source.variable_name in variables:
            raise HTTPException(status_code=400, detail="Variable kalkulasi tidak boleh duplikat")
        variables[source.variable_name] = 1.0

    evaluate_formula(calculation_payload.formula, variables)

    if existing:
        existing.formula = calculation_payload.formula
        existing.rounding = calculation_payload.rounding
        existing.is_active = calculation_payload.is_active
        existing.deleted_at = None
        for source in existing.sources:
            db.delete(source)
        calculation = existing
    else:
        calculation = ParameterCalculation(
            target_parameter_id=target_parameter_id,
            formula=calculation_payload.formula,
            rounding=calculation_payload.rounding,
            is_active=calculation_payload.is_active,
        )
        db.add(calculation)
        db.flush()

    for source in calculation_payload.sources:
        db.add(ParameterCalculationSource(
            calculation_id=calculation.id,
            source_parameter_id=source.source_parameter_id,
            variable_name=source.variable_name,
        ))


def _upsert_parameter_answer(db: Session, rekam_pasien_id: int, parameter_id: int, jawaban: str):
    existing = db.query(RekamPasienParameter).filter(
        RekamPasienParameter.rekam_pasien_id == rekam_pasien_id,
        RekamPasienParameter.parameter_id == parameter_id,
        RekamPasienParameter.deleted_at.is_(None),
    ).first()

    if existing:
        existing.jawaban = jawaban
        existing.opsi_parameter_id = None
        return

    db.add(RekamPasienParameter(
        rekam_pasien_id=rekam_pasien_id,
        parameter_id=parameter_id,
        jawaban=jawaban,
        opsi_parameter_id=None,
    ))


def calculate_rekam_pasien_parameters(db: Session, rekam_pasien_id: int):
    calculations = (
        db.query(ParameterCalculation)
        .options(joinedload(ParameterCalculation.sources))
        .filter(
            ParameterCalculation.is_active.is_(True),
            ParameterCalculation.deleted_at.is_(None),
        )
        .all()
    )

    answers = (
        db.query(RekamPasienParameter)
        .filter(
            RekamPasienParameter.rekam_pasien_id == rekam_pasien_id,
            RekamPasienParameter.deleted_at.is_(None),
        )
        .all()
    )
    answer_map = {answer.parameter_id: answer.jawaban for answer in answers}

    for calculation in calculations:
        variables = {}
        skip = False

        for source in calculation.sources:
            if source.deleted_at is not None:
                continue

            raw_value = answer_map.get(source.source_parameter_id)
            if raw_value in (None, ""):
                skip = True
                break

            try:
                variables[source.variable_name] = float(raw_value)
            except ValueError:
                skip = True
                break

        if skip:
            continue

        result = evaluate_formula(calculation.formula, variables)
        if calculation.rounding is not None:
            result = round(result, calculation.rounding)

        _upsert_parameter_answer(
            db,
            rekam_pasien_id,
            calculation.target_parameter_id,
            str(result),
        )
