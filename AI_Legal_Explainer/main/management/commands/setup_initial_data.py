"""
Django management command to setup initial data for AI Legal Explainer
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from main.models import LegalTerm
from main.ai_services import GlossaryService

class Command(BaseCommand):
    help = 'Setup initial data for AI Legal Explainer'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data for AI Legal Explainer...')
        
        try:
            with transaction.atomic():
                self.setup_legal_terms()
                self.stdout.write(
                    self.style.SUCCESS('Successfully setup initial data!')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up initial data: {str(e)}')
            )

    def setup_legal_terms(self):
        """Setup initial legal terms"""
        self.stdout.write('Setting up legal terms...')
        
        # Check if terms already exist
        if LegalTerm.objects.exists():
            self.stdout.write('Legal terms already exist, skipping...')
            return
        
        # Get default terms from glossary service
        glossary_service = GlossaryService()
        default_terms = glossary_service._load_default_terms()
        
        # Create legal terms
        created_terms = []
        for term_data in default_terms:
            term, created = LegalTerm.objects.get_or_create(
                term=term_data['term'],
                defaults={
                    'definition': term_data['definition'],
                    'plain_language_explanation': term_data['plain_language_explanation'],
                    'examples': term_data.get('examples', ''),
                    'category': term_data['category']
                }
            )
            
            if created:
                created_terms.append(term.term)
                self.stdout.write(f'Created term: {term.term}')
            else:
                self.stdout.write(f'Term already exists: {term.term}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(created_terms)} new legal terms')
        )
