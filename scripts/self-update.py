#!/usr/bin/env python3
"""
Self-updating script for the Universal Build System.
Automatically updates the build system components from the repository.
"""

import os
import sys
import json
import subprocess
import shutil
import hashlib
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import requests
import time

class SelfUpdater:
    """Handles self-updating of the build system."""
    
    def __init__(self, repo_url: str = None, branch: str = "main"):
        self.repo_url = repo_url or self._detect_repo_url()
        self.branch = branch
        self.current_dir = Path(__file__).parent.parent
        self.update_manifest = self.current_dir / "update-manifest.json"
        self.backup_dir = self.current_dir / "backups"
        
    def _detect_repo_url(self) -> str:
        """Detect repository URL from git remote."""
        try:
            result = subprocess.run([
                'git', 'remote', 'get-url', 'origin'
            ], capture_output=True, text=True, cwd=self.current_dir)
            
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        return "https://github.com/CoastalGuardFencing/Praxis-os-dashboard"
    
    def check_for_updates(self) -> Dict:
        """Check if updates are available."""
        print("🔍 Checking for updates...")
        
        try:
            # Get latest commit info
            if self.repo_url.startswith('https://github.com'):
                latest_info = self._get_github_latest_commit()
            else:
                latest_info = self._get_git_latest_commit()
            
            current_info = self._get_current_version_info()
            
            update_available = latest_info['sha'] != current_info.get('sha')
            
            return {
                'update_available': update_available,
                'current_version': current_info,
                'latest_version': latest_info,
                'changes': self._get_changes_since_version(current_info.get('sha'), latest_info['sha']) if update_available else []
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'update_available': False
            }
    
    def _get_github_latest_commit(self) -> Dict:
        """Get latest commit info from GitHub API."""
        # Extract owner/repo from URL
        parts = self.repo_url.replace('https://github.com/', '').replace('.git', '').split('/')
        owner, repo = parts[0], parts[1]
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{self.branch}"
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        commit_data = response.json()
        return {
            'sha': commit_data['sha'],
            'message': commit_data['commit']['message'],
            'author': commit_data['commit']['author']['name'],
            'date': commit_data['commit']['author']['date'],
            'url': commit_data['html_url']
        }
    
    def _get_git_latest_commit(self) -> Dict:
        """Get latest commit info using git commands."""
        # Fetch latest changes
        subprocess.run(['git', 'fetch', 'origin', self.branch], 
                      cwd=self.current_dir, check=True)
        
        # Get latest commit info
        result = subprocess.run([
            'git', 'log', f'origin/{self.branch}', '-1', 
            '--format=%H|%s|%an|%ad', '--date=iso'
        ], capture_output=True, text=True, cwd=self.current_dir, check=True)
        
        sha, message, author, date = result.stdout.strip().split('|', 3)
        
        return {
            'sha': sha,
            'message': message,
            'author': author,
            'date': date,
            'url': f"{self.repo_url}/commit/{sha}"
        }
    
    def _get_current_version_info(self) -> Dict:
        """Get current version information."""
        try:
            # Try to get from git
            result = subprocess.run([
                'git', 'log', '-1', '--format=%H|%s|%an|%ad', '--date=iso'
            ], capture_output=True, text=True, cwd=self.current_dir)
            
            if result.returncode == 0:
                sha, message, author, date = result.stdout.strip().split('|', 3)
                return {
                    'sha': sha,
                    'message': message,
                    'author': author,
                    'date': date
                }
        except Exception:
            pass
        
        # Fallback to manifest file
        if self.update_manifest.exists():
            with open(self.update_manifest, 'r') as f:
                return json.load(f)
        
        return {'sha': 'unknown', 'message': 'Unknown version'}
    
    def _get_changes_since_version(self, current_sha: str, latest_sha: str) -> List[Dict]:
        """Get list of changes since current version."""
        try:
            if current_sha == 'unknown':
                return []
            
            if self.repo_url.startswith('https://github.com'):
                return self._get_github_commits_between(current_sha, latest_sha)
            else:
                return self._get_git_commits_between(current_sha, latest_sha)
        except Exception:
            return []
    
    def _get_github_commits_between(self, base_sha: str, head_sha: str) -> List[Dict]:
        """Get commits between two SHAs using GitHub API."""
        parts = self.repo_url.replace('https://github.com/', '').replace('.git', '').split('/')
        owner, repo = parts[0], parts[1]
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}/compare/{base_sha}...{head_sha}"
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        compare_data = response.json()
        
        changes = []
        for commit in compare_data.get('commits', []):
            changes.append({
                'sha': commit['sha'][:8],
                'message': commit['commit']['message'].split('\n')[0],
                'author': commit['commit']['author']['name'],
                'date': commit['commit']['author']['date']
            })
        
        return changes
    
    def _get_git_commits_between(self, base_sha: str, head_sha: str) -> List[Dict]:
        """Get commits between two SHAs using git commands."""
        result = subprocess.run([
            'git', 'log', f'{base_sha}..{head_sha}', 
            '--format=%h|%s|%an|%ad', '--date=short'
        ], capture_output=True, text=True, cwd=self.current_dir)
        
        if result.returncode != 0:
            return []
        
        changes = []
        for line in result.stdout.strip().split('\n'):
            if line:
                sha, message, author, date = line.split('|', 3)
                changes.append({
                    'sha': sha,
                    'message': message,
                    'author': author,
                    'date': date
                })
        
        return changes
    
    def update(self, force: bool = False, backup: bool = True) -> Dict:
        """Perform the update."""
        print("🔄 Starting update process...")
        
        update_result = {
            'status': 'success',
            'backup_created': False,
            'files_updated': [],
            'errors': []
        }
        
        try:
            # Check for updates first
            update_info = self.check_for_updates()
            
            if not update_info.get('update_available') and not force:
                return {
                    'status': 'no_update',
                    'message': 'No updates available'
                }
            
            # Create backup if requested
            if backup:
                backup_path = self._create_backup()
                update_result['backup_created'] = True
                update_result['backup_path'] = str(backup_path)
                print(f"✅ Backup created at {backup_path}")
            
            # Perform update
            if self._is_git_repo():
                updated_files = self._update_via_git()
            else:
                updated_files = self._update_via_download()
            
            update_result['files_updated'] = updated_files
            
            # Update manifest
            self._update_manifest(update_info.get('latest_version', {}))
            
            # Validate update
            validation_result = self._validate_update()
            if not validation_result['valid']:
                raise Exception(f"Update validation failed: {validation_result['error']}")
            
            print("✅ Update completed successfully!")
            print("ℹ️ Please restart any running build processes to use the updated version.")
            
        except Exception as e:
            update_result['status'] = 'failed'
            update_result['errors'].append(str(e))
            print(f"❌ Update failed: {e}")
            
            # Attempt rollback if backup exists
            if backup and update_result.get('backup_path'):
                try:
                    self._rollback_from_backup(update_result['backup_path'])
                    update_result['rolled_back'] = True
                    print("✅ Rolled back to previous version")
                except Exception as rollback_error:
                    update_result['rollback_error'] = str(rollback_error)
                    print(f"❌ Rollback failed: {rollback_error}")
        
        return update_result
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        return (self.current_dir / '.git').exists()
    
    def _update_via_git(self) -> List[str]:
        """Update using git pull."""
        print("📥 Updating via git...")
        
        # Stash any local changes
        subprocess.run(['git', 'stash'], cwd=self.current_dir)
        
        # Pull latest changes
        result = subprocess.run([
            'git', 'pull', 'origin', self.branch
        ], capture_output=True, text=True, cwd=self.current_dir)
        
        if result.returncode != 0:
            raise Exception(f"Git pull failed: {result.stderr}")
        
        # Get list of updated files
        changed_files_result = subprocess.run([
            'git', 'diff', '--name-only', 'HEAD@{1}', 'HEAD'
        ], capture_output=True, text=True, cwd=self.current_dir)
        
        return changed_files_result.stdout.strip().split('\n') if changed_files_result.stdout.strip() else []
    
    def _update_via_download(self) -> List[str]:
        """Update by downloading latest version."""
        print("📥 Updating via download...")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download repository
            if self.repo_url.startswith('https://github.com'):
                download_url = f"{self.repo_url}/archive/{self.branch}.zip"
                self._download_and_extract_github(download_url, temp_dir)
            else:
                raise Exception("Download update only supports GitHub repositories")
            
            # Copy updated files
            return self._copy_updated_files(temp_dir)
    
    def _download_and_extract_github(self, download_url: str, temp_dir: str):
        """Download and extract GitHub repository."""
        import zipfile
        
        zip_path = Path(temp_dir) / "repo.zip"
        
        # Download
        response = requests.get(download_url, timeout=60)
        response.raise_for_status()
        
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        # Extract
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
    
    def _copy_updated_files(self, temp_dir: str) -> List[str]:
        """Copy updated files from temporary directory."""
        # Find the extracted directory (GitHub repos extract to reponame-branch/)
        temp_path = Path(temp_dir)
        extracted_dirs = [d for d in temp_path.iterdir() if d.is_dir() and d.name != '__pycache__']
        
        if not extracted_dirs:
            raise Exception("No extracted directory found")
        
        source_dir = extracted_dirs[0]
        updated_files = []
        
        # Define files/directories to update
        update_paths = [
            'scripts/',
            'config/',
            'hooks/',
            'automation/',
            '.github/workflows/'
        ]
        
        for update_path in update_paths:
            source_path = source_dir / update_path
            target_path = self.current_dir / update_path
            
            if source_path.exists():
                if source_path.is_dir():
                    if target_path.exists():
                        shutil.rmtree(target_path)
                    shutil.copytree(source_path, target_path)
                    updated_files.extend([str(f.relative_to(self.current_dir)) for f in target_path.rglob('*') if f.is_file()])
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, target_path)
                    updated_files.append(str(target_path.relative_to(self.current_dir)))
        
        return updated_files
    
    def _create_backup(self) -> Path:
        """Create backup of current version."""
        timestamp = int(time.time())
        backup_path = self.backup_dir / f"backup-{timestamp}"
        
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup key directories
        backup_paths = [
            'scripts/',
            'config/',
            'hooks/',
            'automation/'
        ]
        
        for backup_source in backup_paths:
            source_path = self.current_dir / backup_source
            if source_path.exists():
                target_path = backup_path / backup_source
                if source_path.is_dir():
                    shutil.copytree(source_path, target_path)
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, target_path)
        
        return backup_path
    
    def _rollback_from_backup(self, backup_path: str):
        """Rollback from backup."""
        backup_dir = Path(backup_path)
        
        if not backup_dir.exists():
            raise Exception(f"Backup directory not found: {backup_path}")
        
        # Restore backed up directories
        for item in backup_dir.iterdir():
            target_path = self.current_dir / item.name
            
            if target_path.exists():
                if target_path.is_dir():
                    shutil.rmtree(target_path)
                else:
                    target_path.unlink()
            
            if item.is_dir():
                shutil.copytree(item, target_path)
            else:
                shutil.copy2(item, target_path)
    
    def _update_manifest(self, version_info: Dict):
        """Update the version manifest file."""
        with open(self.update_manifest, 'w') as f:
            json.dump({
                **version_info,
                'update_timestamp': time.time(),
                'updated_by': 'self-updater'
            }, f, indent=2)
    
    def _validate_update(self) -> Dict:
        """Validate that the update was successful."""
        try:
            # Check that key files exist
            required_files = [
                'scripts/universal-builder.py',
                'config/lang-config.yaml',
                'scripts/cli-wizard.py'
            ]
            
            for file_path in required_files:
                if not (self.current_dir / file_path).exists():
                    return {
                        'valid': False,
                        'error': f"Required file missing: {file_path}"
                    }
            
            # Try to import/run basic checks
            import importlib.util
            
            builder_spec = importlib.util.spec_from_file_location(
                "universal_builder", 
                self.current_dir / "scripts/universal-builder.py"
            )
            
            if builder_spec is None:
                return {
                    'valid': False,
                    'error': "Could not load universal-builder.py"
                }
            
            return {'valid': True}
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def cleanup_old_backups(self, keep_count: int = 5):
        """Clean up old backup directories."""
        if not self.backup_dir.exists():
            return
        
        backups = sorted([
            d for d in self.backup_dir.iterdir() 
            if d.is_dir() and d.name.startswith('backup-')
        ], key=lambda x: x.stat().st_mtime, reverse=True)
        
        for old_backup in backups[keep_count:]:
            print(f"🧹 Removing old backup: {old_backup}")
            shutil.rmtree(old_backup)

def main():
    """Main entry point for self-updater."""
    parser = argparse.ArgumentParser(description='Self-updater for Universal Build System')
    parser.add_argument('--check', action='store_true',
                       help='Check for updates without updating')
    parser.add_argument('--update', action='store_true',
                       help='Perform update if available')
    parser.add_argument('--force', action='store_true',
                       help='Force update even if no updates detected')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip creating backup')
    parser.add_argument('--repo-url', 
                       help='Repository URL (auto-detected if not provided)')
    parser.add_argument('--branch', default='main',
                       help='Branch to update from')
    parser.add_argument('--cleanup-backups', action='store_true',
                       help='Clean up old backups')
    
    args = parser.parse_args()
    
    try:
        updater = SelfUpdater(args.repo_url, args.branch)
        
        if args.cleanup_backups:
            updater.cleanup_old_backups()
            return
        
        if args.check or (not args.update and not args.force):
            # Check for updates
            update_info = updater.check_for_updates()
            
            if 'error' in update_info:
                print(f"❌ Error checking for updates: {update_info['error']}")
                sys.exit(1)
            
            if update_info['update_available']:
                print("✅ Updates available!")
                print(f"Current: {update_info['current_version'].get('sha', 'unknown')[:8]} - {update_info['current_version'].get('message', 'Unknown')}")
                print(f"Latest:  {update_info['latest_version']['sha'][:8]} - {update_info['latest_version']['message']}")
                
                if update_info['changes']:
                    print(f"\n📝 Changes ({len(update_info['changes'])} commits):")
                    for change in update_info['changes'][:10]:  # Show max 10
                        print(f"  • {change['sha']} - {change['message']}")
                    
                    if len(update_info['changes']) > 10:
                        print(f"  ... and {len(update_info['changes']) - 10} more")
                
                print("\nRun with --update to apply updates.")
            else:
                print("✅ No updates available - you're running the latest version!")
        
        elif args.update or args.force:
            # Perform update
            result = updater.update(
                force=args.force,
                backup=not args.no_backup
            )
            
            if result['status'] == 'success':
                print(f"✅ Update completed successfully!")
                if result['files_updated']:
                    print(f"📝 Updated {len(result['files_updated'])} files")
            elif result['status'] == 'no_update':
                print("ℹ️ No updates available")
            else:
                print(f"❌ Update failed!")
                for error in result.get('errors', []):
                    print(f"   Error: {error}")
                sys.exit(1)
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n⚠️ Update interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Self-updater failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()