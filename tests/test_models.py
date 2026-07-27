from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SyncSession

from app.models.base import Base
from app.models.user import User, UserRole
from app.models.session import Session
from app.models.evaluation import Evaluation, EvaluationStatus


def test_model_creation_and_relationships() -> None:
    """
    Validates model mappings, indexes, foreign key configurations, and relationship cascades
    using an in-memory SQLite database setup.
    """
    # Create an in-memory database and instantiate tables
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with SyncSession(engine) as db:
        # 1. Create Teacher and Parent users
        teacher = User(
            name="Jane Teacher",
            email="jane@example.com",
            password_hash="secret_pbkdf2",
            role=UserRole.TEACHER
        )
        parent_student = User(
            name="John Parent",
            email="john@example.com",
            password_hash="secret_pbkdf2",
            role=UserRole.PARENT
        )
        db.add_all([teacher, parent_student])
        db.commit()

        # Verify database generated primary keys
        assert teacher.id is not None
        assert parent_student.id is not None

        # 2. Create a Session referencing the teacher and parent_student
        class_session = Session(
            title="English Literature",
            description="Introduction to Shakespeare",
            teacher_id=teacher.id,
            student_id=parent_student.id
        )
        db.add(class_session)
        db.commit()

        # 3. Create an Evaluation for the Session
        eval_record = Evaluation(
            session_id=class_session.id,
            status=EvaluationStatus.PENDING
        )
        db.add(eval_record)
        db.commit()

        # Refresh objects to reload relationship attributes
        db.refresh(teacher)
        db.refresh(parent_student)
        db.refresh(class_session)
        db.refresh(eval_record)

        # 4. Assert relationship traversals (back-populations)
        # Teacher -> Sessions
        assert len(teacher.teaches_sessions) == 1
        assert teacher.teaches_sessions[0].title == "English Literature"

        # Student -> Sessions
        assert len(parent_student.student_sessions) == 1
        assert parent_student.student_sessions[0].title == "English Literature"

        # Session -> Users
        assert class_session.teacher.email == "jane@example.com"
        assert class_session.student.email == "john@example.com"

        # Session -> Evaluations
        assert len(class_session.evaluations) == 1
        assert class_session.evaluations[0].status == EvaluationStatus.PENDING

        # Evaluation -> Session
        assert eval_record.session.title == "English Literature"

        # 5. Verify cascade deletion of child evaluation when session is deleted
        db.delete(class_session)
        db.commit()

        remaining_evals = db.query(Evaluation).filter_by(id=eval_record.id).first()
        assert remaining_evals is None
