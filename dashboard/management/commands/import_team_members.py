# yourapp/management/commands/import_team_members.py

import os
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.crypto import get_random_string
from ...models import TeamMember, Faculty

class Command(BaseCommand):
    help = 'Import team members from Excel, XLSX, or CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel/CSV file')
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing users instead of skipping them',
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        update_existing = options['update']
        
        if not os.path.exists(file_path):
            raise CommandError(f'File {file_path} does not exist')
        
        try:
            # Detect file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif file_ext == '.csv':
                df = pd.read_csv(file_path)
            else:
                raise CommandError('Unsupported file format. Use Excel (.xlsx, .xls) or CSV (.csv)')
            
            # Display column information for debugging
            self.stdout.write(f"Columns in file: {df.columns.tolist()}")
            
            # Mapping Arabic column names to model fields
            # Based on the image of your Excel file, the columns are:
            # كلمة السر (password), البريد (email), الكلية (faculty), اللقب (last name), الاسم (first name)
            
            created_count = 0
            updated_count = 0
            skipped_count = 0
            error_count = 0
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # Map the Arabic column names
                        email = row['البريد'].strip() if 'البريد' in df.columns else None
                        password = row['كلمة السر'] if 'كلمة السر' in df.columns and not pd.isna(row['كلمة السر']) else get_random_string(12)
                        first_name = row['الاسم'].strip() if 'الاسم' in df.columns else ''
                        last_name = row['اللقب'].strip() if 'اللقب' in df.columns else ''
                        faculty_name = row['الكلية'].strip() if 'الكلية' in df.columns else ''
                        print("email:" , row['البريد'])
                        if not email:
                            self.stdout.write(self.style.WARNING(f"Skipping row {index+1}: No email provided"))
                            skipped_count += 1
                            continue
                        
                        # Check if user already exists
                        user_exists = User.objects.filter(email=email).exists()
                        
                        if user_exists and not update_existing:
                            self.stdout.write(f"Skipping existing user: {email}")
                            skipped_count += 1
                            continue
                        
                        # Get or create the faculty
                        faculty = None
                        if faculty_name:
                            faculty, _ = Faculty.objects.get_or_create(
                                arabic_name=faculty_name,
                                defaults={
                                    'latin_name': faculty_name,  # Use Arabic name as default
                                    'abreviated_name': faculty_name[:4]  # Use first 20 chars as abbreviation
                                }
                            )
                        
                        if user_exists:
                            # Update existing user
                            user = User.objects.get(email=email)
                            user.first_name = first_name
                            user.last_name = last_name
                            if password and not pd.isna(password):
                                user.set_password(str(password))
                            user.save()
                            
                            # Update team member
                            team_member = TeamMember.objects.get(user=user)
                            if faculty:
                                team_member.faculty = faculty
                            team_member.save()
                            
                            self.stdout.write(f"Updated user: {email}")
                            updated_count += 1
                        else:
                            # Create new user
                            username = email.split('@')[0]
                            
                            # Make sure username is unique
                            base_username = username
                            counter = 1
                            while User.objects.filter(username=username).exists():
                                username = f"{base_username}{counter}"
                                counter += 1
                            
                            # Create user
                            user = User.objects.create_user(
                                username=username,
                                email=email,
                                password=str(password),
                                first_name=first_name,
                                last_name=last_name
                            )
                            
                            # Update team member (it was created by the signal)
                            team_member = TeamMember.objects.get(user=user)
                            if faculty:
                                team_member.faculty = faculty
                            team_member.save()
                            
                            self.stdout.write(f"Created user: {email}")
                            created_count += 1
                    
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error processing row {index+1}: {str(e)}"))
                        error_count += 1
            
            self.stdout.write(self.style.SUCCESS(
                f"Import completed. Created: {created_count}, Updated: {updated_count}, "
                f"Skipped: {skipped_count}, Errors: {error_count}")
            )
            
        except Exception as e:
            raise CommandError(f'Error reading file: {str(e)}')