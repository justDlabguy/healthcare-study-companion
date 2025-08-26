import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole, Topic, Document, DocumentStatus, QAHistory, Flashcard, FlashcardReview
from app.auth import get_password_hash

def create_test_data():
    """Create test data for the database."""
    db: Session = next(get_db())
    
    try:
        # Create test users
        admin_user = User(
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)
        
        test_user = User(
            email="user@example.com",
            password_hash=get_password_hash("user123"),
            full_name="Test User",
            role=UserRole.USER,
            is_active=True
        )
        db.add(test_user)
        db.flush()  # Flush to get user IDs
        
        # Create topics
        medical_topics = [
            ("Cardiology Basics", "Fundamentals of heart function and common cardiac conditions"),
            ("Pharmacology 101", "Introduction to common medications and their mechanisms"),
            ("Anatomy Review", "Essential human anatomy for healthcare professionals"),
            ("Medical Terminology", "Common medical terms and abbreviations"),
            ("Emergency Procedures", "Basic emergency medical procedures and protocols")
        ]
        
        topics = []
        for i, (title, description) in enumerate(medical_topics):
            topic = Topic(
                owner_id=admin_user.id if i % 2 == 0 else test_user.id,
                title=title,
                description=description,
                is_public=(i % 3 != 0)  # Make some topics public
            )
            topics.append(topic)
            db.add(topic)
        
        db.flush()  # Flush to get topic IDs
        
        # Create documents for each topic
        document_titles = [
            "Introduction to {}",
            "Advanced Concepts in {}",
            "Clinical Cases: {}",
            "Review Questions: {}",
            "Research Papers on {}"
        ]
        
        for topic in topics:
            for i, title_template in enumerate(document_titles[:3]):  # 3 docs per topic
                doc = Document(
                    topic_id=topic.id,
                    filename=f"{topic.title.lower().replace(' ', '_')}_{i+1}.pdf",
                    content_type="application/pdf",
                    file_size=random.randint(100000, 5000000),  # 100KB to 5MB
                    status=DocumentStatus.PROCESSED if i % 2 == 0 else DocumentStatus.UPLOADED,
                    text=f"This is sample extracted text for {title_template.format(topic.title)}. "
                         f"It contains important information about {topic.title}.",
                    file_metadata={"pages": random.randint(5, 50), "source": "test_data"},
                    vector_dim=768 if i % 2 == 0 else None,
                    processed_at=datetime.utcnow() if i % 2 == 0 else None
                )
                db.add(doc)
        
        # Create flashcards
        flashcard_data = [
            ("What is the normal range for blood pressure?", "120/80 mmHg"),
            ("What does ACE stand for in pharmacology?", "Angiotensin-Converting Enzyme"),
            ("Which part of the heart pumps blood to the lungs?", "Right ventricle"),
            ("What is the medical term for high blood pressure?", "Hypertension"),
            ("What is the largest organ in the human body?", "Skin")
        ]
        
        for i, (front, back) in enumerate(flashcard_data):
            flashcard = Flashcard(
                topic_id=topics[i % len(topics)].id,
                front=front,
                back=back,
                is_active=True,
                last_reviewed=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                next_review=datetime.utcnow() + timedelta(days=random.randint(1, 30)),
                ease_factor=round(random.uniform(1.5, 2.5), 2),
                review_count=random.randint(0, 10)
            )
            db.add(flashcard)
        
        # Create QA history
        qa_pairs = [
            ("What are the symptoms of a heart attack?", 
             "Common symptoms include chest pain, shortness of breath, nausea, and pain in the arms, neck, or jaw."),
            ("How does aspirin work as a blood thinner?",
             "Aspirin inhibits the production of thromboxane, which is involved in platelet aggregation, thus acting as a blood thinner."),
            ("What is the function of the cerebellum?",
             "The cerebellum coordinates voluntary movements, balance, and muscle tone."),
            ("What does PRN stand for in medical terms?",
             "PRN stands for 'pro re nata', which means 'as needed' in Latin.")
        ]
        
        for i, (question, answer) in enumerate(qa_pairs):
            qa = QAHistory(
                topic_id=topics[i % len(topics)].id,
                user_id=admin_user.id if i % 2 == 0 else test_user.id,
                question=question,
                answer=answer,
                score=round(random.uniform(3.0, 5.0), 1),
                feedback="Helpful response" if i % 2 == 0 else "Needs more detail"
            )
            db.add(qa)
        
        db.commit()
        print("✅ Successfully created test data!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating test data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Seeding test data...")
    create_test_data()
