#!/usr/bin/env python3
"""
Fix for flashcard generation issues - diagnostic and repair script.
"""
import asyncio
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def diagnose_and_fix_flashcard_issues():
    """Diagnose and fix common flashcard generation issues."""
    try:
        from app.config import settings
        from app.models import Topic, Document, Flashcard
        from app.services.flashcard_generator import flashcard_generator
        from app.services.flashcard_types import FlashcardType
        
        print("🔍 Diagnosing flashcard generation issues...")
        print(f"Database URL: {settings.database_url}")
        print(f"LLM Provider: {settings.llm_provider}")
        print(f"API Key configured: {'Yes' if settings.get_api_key_for_provider() else 'No'}")
        print()
        
        # Connect to database
        engine = create_engine(settings.database_url)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            # Check topics and documents
            topics = db.query(Topic).all()
            print(f"📚 Found {len(topics)} topics in database")
            
            for topic in topics[:5]:  # Show first 5 topics
                documents = db.query(Document).filter(Document.topic_id == topic.id).all()
                processed_docs = [d for d in documents if d.status == "processed"]
                flashcards = db.query(Flashcard).filter(Flashcard.topic_id == topic.id).all()
                
                print(f"  Topic: {topic.title}")
                print(f"    Documents: {len(documents)} total, {len(processed_docs)} processed")
                print(f"    Flashcards: {len(flashcards)}")
                
                # Show document statuses
                if documents:
                    status_counts = {}
                    for doc in documents:
                        status_counts[doc.status] = status_counts.get(doc.status, 0) + 1
                    print(f"    Document statuses: {status_counts}")
                
                # If there are processed documents but no flashcards, try to generate some
                if processed_docs and len(flashcards) == 0:
                    print(f"    🔧 Attempting to generate flashcards for topic '{topic.title}'...")
                    try:
                        generated_flashcards = await flashcard_generator.generate_flashcards_from_documents(
                            documents=processed_docs,
                            num_cards=2,
                            card_type=FlashcardType.BASIC,
                            topic_context=f"Topic: {topic.title}. {topic.description or ''}"
                        )
                        
                        # Save to database
                        for gen_card in generated_flashcards:
                            db_flashcard = Flashcard(
                                topic_id=topic.id,
                                front=gen_card.front,
                                back=gen_card.back,
                                flashcard_metadata=gen_card.metadata,
                                is_active=True
                            )
                            db.add(db_flashcard)
                        
                        db.commit()
                        print(f"    ✅ Generated {len(generated_flashcards)} flashcards successfully!")
                        
                    except Exception as e:
                        print(f"    ❌ Failed to generate flashcards: {e}")
                        db.rollback()
                
                print()
            
            # Check for common issues
            print("🔍 Checking for common issues...")
            
            # Issue 1: Documents stuck in processing
            stuck_docs = db.query(Document).filter(Document.status == "processing").all()
            if stuck_docs:
                print(f"⚠️  Found {len(stuck_docs)} documents stuck in 'processing' status")
                print("   Consider reprocessing these documents or checking the document processor")
            
            # Issue 2: Documents with errors
            error_docs = db.query(Document).filter(Document.status == "error").all()
            if error_docs:
                print(f"❌ Found {len(error_docs)} documents with 'error' status")
                for doc in error_docs[:3]:
                    print(f"   - {doc.filename}: {doc.error_message}")
            
            # Issue 3: Documents without text content
            empty_docs = db.query(Document).filter(
                Document.status == "processed",
                (Document.text == None) | (Document.text == "")
            ).all()
            if empty_docs:
                print(f"⚠️  Found {len(empty_docs)} processed documents without text content")
            
            if not stuck_docs and not error_docs and not empty_docs:
                print("✅ No common issues found!")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f'❌ Error during diagnosis: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(diagnose_and_fix_flashcard_issues())