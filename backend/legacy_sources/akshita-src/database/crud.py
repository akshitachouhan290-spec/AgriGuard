import sys

from sqlalchemy.orm import Session

from src.database import models
from src.logger import get_logger
from src.exception import CustomException

logger = get_logger(__name__)


# ---------------- Farmer ----------------

def create_farmer(
    db: Session,
    name,
    phone,
    language="English",
    village=None,
    district=None,
    state=None,
    latitude=None,
    longitude=None
):
    try:
        farmer = models.Farmer(
            name=name,
            phone=phone,
            language=language,
            village=village,
            district=district,
            state=state,
            latitude=latitude,
            longitude=longitude,
        )

        db.add(farmer)
        db.commit()
        db.refresh(farmer)

        logger.info(f"Farmer created: id={farmer.id}")
        return farmer

    except Exception as e:
        db.rollback()
        logger.error("Failed to create farmer")
        raise CustomException(e, sys)


def get_farmer_by_id(db: Session, farmer_id: int):
    try:
        return db.query(models.Farmer).filter(
            models.Farmer.id == farmer_id
        ).first()

    except Exception as e:
        raise CustomException(e, sys)


def get_farmer_by_phone(db: Session, phone: str):
    try:
        return db.query(models.Farmer).filter(
            models.Farmer.phone == phone
        ).first()

    except Exception as e:
        raise CustomException(e, sys)


def update_farmer(
    db: Session,
    farmer_id: int,
    name=None,
    phone=None,
    language=None,
    village=None,
    district=None,
    state=None,
    latitude=None,
    longitude=None
):
    try:
        farmer = db.query(models.Farmer).filter(
            models.Farmer.id == farmer_id
        ).first()

        if not farmer:
            raise ValueError(f"Farmer with id={farmer_id} not found")

        if name is not None:
            farmer.name = name

        if phone is not None:
            farmer.phone = phone

        if language is not None:
            farmer.language = language

        if village is not None:
            farmer.village = village

        if district is not None:
            farmer.district = district

        if state is not None:
            farmer.state = state

        if latitude is not None:
            farmer.latitude = latitude

        if longitude is not None:
            farmer.longitude = longitude

        db.commit()
        db.refresh(farmer)

        logger.info(f"Farmer updated: id={farmer.id}")
        return farmer

    except Exception as e:
        db.rollback()
        logger.error("Failed to update farmer")
        raise CustomException(e, sys)


def delete_farmer(db: Session, farmer_id: int):
    try:
        farmer = db.query(models.Farmer).filter(
            models.Farmer.id == farmer_id
        ).first()

        if not farmer:
            raise ValueError(f"Farmer with id={farmer_id} not found")

        db.delete(farmer)
        db.commit()

        logger.info(f"Farmer deleted: id={farmer_id}")
        return True

    except Exception as e:
        db.rollback()
        logger.error("Failed to delete farmer")
        raise CustomException(e, sys)


# ---------------- Crop (master/reference table) ----------------

def get_crop_by_id(db: Session, crop_id: int):
    try:
        return db.query(models.Crop).filter(
            models.Crop.id == crop_id
        ).first()

    except Exception as e:
        raise CustomException(e, sys)


def get_crop_by_name(db: Session, name: str):
    try:
        return db.query(models.Crop).filter(
            models.Crop.name == name
        ).first()

    except Exception as e:
        raise CustomException(e, sys)


def get_all_crops(db: Session):
    try:
        return db.query(models.Crop).all()

    except Exception as e:
        raise CustomException(e, sys)


# ---------------- Field ----------------

def create_field(
    db: Session,
    farmer_id,
    field_name,
    crop_id,
    area=None,
    latitude=None,
    longitude=None
):
    try:
        field = models.Field(
            farmer_id=farmer_id,
            field_name=field_name,
            crop_id=crop_id,
            area=area,
            latitude=latitude,
            longitude=longitude,
        )

        db.add(field)
        db.commit()
        db.refresh(field)

        logger.info(f"Field created: id={field.id}")
        return field

    except Exception as e:
        db.rollback()
        logger.error("Failed to create field")
        raise CustomException(e, sys)


def get_field_by_id(db: Session, field_id: int):
    try:
        return db.query(models.Field).filter(
            models.Field.id == field_id
        ).first()

    except Exception as e:
        raise CustomException(e, sys)


def get_fields_by_farmer(db: Session, farmer_id: int):
    try:
        return db.query(models.Field).filter(
            models.Field.farmer_id == farmer_id
        ).all()

    except Exception as e:
        raise CustomException(e, sys)


def update_field(
    db: Session,
    field_id: int,
    field_name=None,
    crop_id=None,
    area=None,
    latitude=None,
    longitude=None
):
    try:
        field = db.query(models.Field).filter(
            models.Field.id == field_id
        ).first()

        if not field:
            raise ValueError(f"Field with id={field_id} not found")

        if field_name is not None:
            field.field_name = field_name

        if crop_id is not None:
            field.crop_id = crop_id

        if area is not None:
            field.area = area

        if latitude is not None:
            field.latitude = latitude

        if longitude is not None:
            field.longitude = longitude

        db.commit()
        db.refresh(field)

        logger.info(f"Field updated: id={field.id}")
        return field

    except Exception as e:
        db.rollback()
        logger.error("Failed to update field")
        raise CustomException(e, sys)


def delete_field(db: Session, field_id: int):
    try:
        field = db.query(models.Field).filter(
            models.Field.id == field_id
        ).first()

        if not field:
            raise ValueError(f"Field with id={field_id} not found")

        db.delete(field)
        db.commit()

        logger.info(f"Field deleted: id={field_id}")
        return True

    except Exception as e:
        db.rollback()
        logger.error("Failed to delete field")
        raise CustomException(e, sys)


# ---------------- DiseaseAnalysis ----------------

def create_disease_analysis(
    db: Session,
    farmer_id,
    field_id,
    image_ref,
    crop,
    disease,
    confidence,
    severity,
    status=models.AnalysisStatus.auto_confirmed
):
    try:
        analysis = models.DiseaseAnalysis(
            farmer_id=farmer_id,
            field_id=field_id,
            image_ref=image_ref,
            crop=crop,
            disease=disease,
            confidence=confidence,
            severity=severity,
            status=status,
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        logger.info(f"Disease analysis created: id={analysis.id}")
        return analysis

    except Exception as e:
        db.rollback()
        logger.error("Failed to create disease analysis")
        raise CustomException(e, sys)


def get_analyses_by_field(db: Session, field_id: int):
    try:
        return db.query(models.DiseaseAnalysis).filter(
            models.DiseaseAnalysis.field_id == field_id
        ).all()

    except Exception as e:
        raise CustomException(e, sys)


def update_disease_analysis(
    db: Session,
    analysis_id: int,
    disease=None,
    confidence=None,
    severity=None,
    status=None,
    confirmed_disease=None,
    follow_up_date=None
):
    try:
        analysis = db.query(models.DiseaseAnalysis).filter(
            models.DiseaseAnalysis.id == analysis_id
        ).first()

        if not analysis:
            raise ValueError(
                f"Disease analysis with id={analysis_id} not found"
            )

        if disease is not None:
            analysis.disease = disease

        if confidence is not None:
            analysis.confidence = confidence

        if severity is not None:
            analysis.severity = severity

        if status is not None:
            analysis.status = status

        if confirmed_disease is not None:
            analysis.confirmed_disease = confirmed_disease

        if follow_up_date is not None:
            analysis.follow_up_date = follow_up_date

        db.commit()
        db.refresh(analysis)

        logger.info(f"Disease analysis updated: id={analysis.id}")
        return analysis

    except Exception as e:
        db.rollback()
        logger.error("Failed to update disease analysis")
        raise CustomException(e, sys)


def delete_disease_analysis(db: Session, analysis_id: int):
    try:
        analysis = db.query(models.DiseaseAnalysis).filter(
            models.DiseaseAnalysis.id == analysis_id
        ).first()

        if not analysis:
            raise ValueError(
                f"Disease analysis with id={analysis_id} not found"
            )

        db.delete(analysis)
        db.commit()

        logger.info(f"Disease analysis deleted: id={analysis_id}")
        return True

    except Exception as e:
        db.rollback()
        logger.error("Failed to delete disease analysis")
        raise CustomException(e, sys)


# ---------------- Risk ----------------

def create_risk(
    db: Session,
    analysis_id,
    risk_level,
    risk_score,
    reason
):
    try:
        risk = models.Risk(
            analysis_id=analysis_id,
            risk_level=risk_level,
            risk_score=risk_score,
            reason=reason,
        )

        db.add(risk)
        db.commit()
        db.refresh(risk)

        logger.info(f"Risk record created: id={risk.id}")
        return risk

    except Exception as e:
        db.rollback()
        logger.error("Failed to create risk record")
        raise CustomException(e, sys)


def get_risk_by_analysis_id(db: Session, analysis_id: int):
    try:
        return db.query(models.Risk).filter(
            models.Risk.analysis_id == analysis_id
        ).first()

    except Exception as e:
        raise CustomException(e, sys)


def update_risk(
    db: Session,
    risk_id: int,
    risk_level=None,
    risk_score=None,
    reason=None
):
    try:
        risk = db.query(models.Risk).filter(
            models.Risk.id == risk_id
        ).first()

        if not risk:
            raise ValueError(f"Risk with id={risk_id} not found")

        if risk_level is not None:
            risk.risk_level = risk_level

        if risk_score is not None:
            risk.risk_score = risk_score

        if reason is not None:
            risk.reason = reason

        db.commit()
        db.refresh(risk)

        logger.info(f"Risk updated: id={risk.id}")
        return risk

    except Exception as e:
        db.rollback()
        logger.error("Failed to update risk")
        raise CustomException(e, sys)


def delete_risk(db: Session, risk_id: int):
    try:
        risk = db.query(models.Risk).filter(
            models.Risk.id == risk_id
        ).first()

        if not risk:
            raise ValueError(f"Risk with id={risk_id} not found")

        db.delete(risk)
        db.commit()

        logger.info(f"Risk deleted: id={risk_id}")
        return True

    except Exception as e:
        db.rollback()
        logger.error("Failed to delete risk")
        raise CustomException(e, sys)

#------------------only for admin not for farmers (access control is being done at API layer)
def create_crop(
    db: Session,
    name,
    category=None,
    typical_growth_duration_days=None,
    common_diseases_note=None
):
    try:
        crop = models.Crop(
            name=name,
            category=category,
            typical_growth_duration_days=typical_growth_duration_days,
            common_diseases_note=common_diseases_note,
        )

        db.add(crop)
        db.commit()
        db.refresh(crop)

        logger.info(f"Crop created: id={crop.id}")
        return crop

    except Exception as e:
        db.rollback()
        logger.error("Failed to create crop")
        raise CustomException(e, sys)