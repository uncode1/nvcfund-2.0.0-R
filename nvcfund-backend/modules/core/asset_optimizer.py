"""
Asset Optimization Module for NVC Banking Platform
Handles CSS/JS minification, compression, and asset management
"""

import os
import re
import gzip
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from flask import current_app, url_for
import logging

logger = logging.getLogger(__name__)

class AssetOptimizer:
    """Main asset optimization class"""
    
    def __init__(self, static_folder: str = None):
        self.static_folder = Path(static_folder or current_app.static_folder)
        self.optimized_folder = self.static_folder / 'optimized'
        self.manifest_file = self.optimized_folder / 'manifest.json'
        self.manifest = self._load_manifest()
        
        # Ensure optimized folder exists
        self.optimized_folder.mkdir(exist_ok=True)
    
    def _load_manifest(self) -> Dict:
        """Load asset manifest file"""
        if self.manifest_file.exists():
            try:
                with open(self.manifest_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load manifest: {e}")
        return {}
    
    def _save_manifest(self):
        """Save asset manifest file"""
        try:
            with open(self.manifest_file, 'w') as f:
                json.dump(self.manifest, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save manifest: {e}")
    
    def _generate_hash(self, content: str) -> str:
        """Generate hash for content versioning"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:8]
    
    def optimize_css(self, css_files: List[str], output_name: str = 'bundle') -> str:
        """Optimize and bundle CSS files (SASS compilation removed)"""

        # SASS compilation removed - application now uses direct CSS files
        
        combined_content = []
        
        for css_file in css_files:
            file_path = self.static_folder / css_file
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Process imports and relative URLs
                    content = self._process_css_imports(content, file_path.parent)
                    combined_content.append(content)
            else:
                logger.warning(f"CSS file not found: {css_file}")
        
        # Combine all CSS
        combined_css = '\n'.join(combined_content)
        
        # Minify CSS
        minified_css = self._minify_css(combined_css)
        
        # Generate versioned filename
        content_hash = self._generate_hash(minified_css)
        output_filename = f"{output_name}.{content_hash}.min.css"
        output_path = self.optimized_folder / output_filename
        
        # Write optimized file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(minified_css)
        
        # Create gzipped version
        self._create_gzipped_version(output_path, minified_css)
        
        # Update manifest
        self.manifest[f"{output_name}.css"] = output_filename
        self._save_manifest()
        
        return output_filename
    
    def optimize_js(self, js_files: List[str], output_name: str = 'bundle') -> str:
        """Optimize and bundle JavaScript files"""
        combined_content = []
        
        for js_file in js_files:
            file_path = self.static_folder / js_file
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    combined_content.append(content)
            else:
                logger.warning(f"JS file not found: {js_file}")
        
        # Combine all JavaScript
        combined_js = '\n;\n'.join(combined_content)  # Add semicolons between files
        
        # Minify JavaScript
        minified_js = self._minify_js(combined_js)
        
        # Generate versioned filename
        content_hash = self._generate_hash(minified_js)
        output_filename = f"{output_name}.{content_hash}.min.js"
        output_path = self.optimized_folder / output_filename
        
        # Write optimized file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(minified_js)
        
        # Create gzipped version
        self._create_gzipped_version(output_path, minified_js)
        
        # Update manifest
        self.manifest[f"{output_name}.js"] = output_filename
        self._save_manifest()
        
        return output_filename
    
    def _minify_css(self, css_content: str) -> str:
        """Minify CSS content"""
        # Remove comments
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Remove extra whitespace
        css_content = re.sub(r'\s+', ' ', css_content)
        
        # Remove whitespace around specific characters
        css_content = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css_content)
        
        # Remove trailing semicolons before closing braces
        css_content = re.sub(r';\s*}', '}', css_content)
        
        # Remove unnecessary quotes from URLs
        css_content = re.sub(r'url\(["\']([^"\']*)["\']', r'url(\1', css_content)
        
        # Convert hex colors to shorter form where possible
        css_content = re.sub(r'#([0-9a-fA-F])\1([0-9a-fA-F])\2([0-9a-fA-F])\3', r'#\1\2\3', css_content)
        
        # Remove unnecessary zeros
        css_content = re.sub(r'\b0+(\.\d+)', r'\1', css_content)
        css_content = re.sub(r'(\d)\.0+\b', r'\1', css_content)
        
        return css_content.strip()
    
    def _minify_js(self, js_content: str) -> str:
        """Basic JavaScript minification"""
        # Remove single-line comments (but preserve URLs)
        js_content = re.sub(r'(?<!:)//.*$', '', js_content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        
        # Remove extra whitespace
        js_content = re.sub(r'\s+', ' ', js_content)
        
        # Remove whitespace around operators and punctuation
        js_content = re.sub(r'\s*([{}();,=+\-*/<>!&|?:])\s*', r'\1', js_content)
        
        # Remove unnecessary semicolons
        js_content = re.sub(r';\s*}', '}', js_content)
        
        return js_content.strip()
    
    def _process_css_imports(self, css_content: str, base_path: Path) -> str:
        """Process CSS @import statements and relative URLs"""
        # Handle @import statements
        def replace_import(match):
            import_path = match.group(1).strip('\'"')
            import_file = base_path / import_path
            
            if import_file.exists():
                with open(import_file, 'r', encoding='utf-8') as f:
                    imported_content = f.read()
                    # Recursively process imports
                    return self._process_css_imports(imported_content, import_file.parent)
            else:
                logger.warning(f"CSS import not found: {import_path}")
                return match.group(0)  # Keep original import
        
        css_content = re.sub(r'@import\s+["\']([^"\']+)["\'];?', replace_import, css_content)
        
        # Handle relative URLs in url() statements
        def replace_url(match):
            url_path = match.group(1).strip('\'"')
            if not url_path.startswith(('http://', 'https://', 'data:', '/')):
                # Convert relative path to absolute
                abs_path = base_path / url_path
                rel_to_static = abs_path.relative_to(self.static_folder)
                return f'url("/{rel_to_static}")'
            return match.group(0)
        
        css_content = re.sub(r'url\(["\']?([^"\']*)["\']?\)', replace_url, css_content)
        
        return css_content
    
    def _create_gzipped_version(self, file_path: Path, content: str):
        """Create gzipped version of the file"""
        gzip_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        with gzip.open(gzip_path, 'wt', encoding='utf-8') as f:
            f.write(content)
    
    def get_asset_url(self, asset_name: str) -> str:
        """Get URL for optimized asset"""
        if asset_name in self.manifest:
            optimized_name = self.manifest[asset_name]
            return url_for('static', filename=f'optimized/{optimized_name}')
        else:
            # Fallback to original asset
            return url_for('static', filename=asset_name)
    
    def clean_old_assets(self, keep_versions: int = 3):
        """Clean old asset versions"""
        if not self.optimized_folder.exists():
            return
        
        # Group files by base name
        file_groups = {}
        for file_path in self.optimized_folder.glob('*'):
            if file_path.is_file() and not file_path.name.endswith('.gz'):
                # Extract base name (remove hash and extension)
                base_name = re.sub(r'\.[a-f0-9]{8}\.min\.(css|js)$', '', file_path.name)
                if base_name not in file_groups:
                    file_groups[base_name] = []
                file_groups[base_name].append(file_path)
        
        # Keep only the latest versions
        for base_name, files in file_groups.items():
            if len(files) > keep_versions:
                # Sort by modification time (newest first)
                files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                
                # Remove old versions
                for old_file in files[keep_versions:]:
                    try:
                        old_file.unlink()
                        # Also remove gzipped version
                        gz_file = old_file.with_suffix(old_file.suffix + '.gz')
                        if gz_file.exists():
                            gz_file.unlink()
                        logger.info(f"Removed old asset: {old_file.name}")
                    except Exception as e:
                        logger.error(f"Failed to remove old asset {old_file}: {e}")

class AssetBundler:
    """Asset bundling configuration"""
    
    def __init__(self):
        self.bundles = {
            'css': {
                'unified': [
                    'css/unified-template-system.css',
                    'css/unified-navigation.css',
                    'css/unified-forms.css',
                    'css/unified-cards.css'
                ],
                'auth': [
                    'css/auth-styles.css',
                    'css/login-forms.css'
                ],
                'banking': [
                    'css/banking-dashboard.css',
                    'css/transaction-styles.css',
                    'css/account-management.css'
                ],
                'admin': [
                    'css/admin-dashboard.css',
                    'css/admin-tables.css',
                    'css/admin-forms.css'
                ],
                'public': [
                    'css/public-unified.css'
                ]
            },
            'js': {
                'unified': [
                    'js/unified-interactions.js',
                    'js/form-validation.js',
                    'js/notification-system.js'
                ],
                'banking': [
                    'js/banking-operations.js',
                    'js/transaction-management.js',
                    'js/account-dashboard.js'
                ],
                'admin': [
                    'js/admin-dashboard.js',
                    'js/user-management.js',
                    'js/system-monitoring.js'
                ],
                'public': [
                    'js/public-unified.js'
                ]
            }
        }
    
    def create_bundles(self, optimizer: AssetOptimizer):
        """Create all asset bundles"""
        created_bundles = {}
        
        # Create CSS bundles
        for bundle_name, css_files in self.bundles['css'].items():
            try:
                output_file = optimizer.optimize_css(css_files, f'css-{bundle_name}')
                created_bundles[f'css-{bundle_name}'] = output_file
                logger.info(f"Created CSS bundle: {bundle_name}")
            except Exception as e:
                logger.error(f"Failed to create CSS bundle {bundle_name}: {e}")
        
        # Create JS bundles
        for bundle_name, js_files in self.bundles['js'].items():
            try:
                output_file = optimizer.optimize_js(js_files, f'js-{bundle_name}')
                created_bundles[f'js-{bundle_name}'] = output_file
                logger.info(f"Created JS bundle: {bundle_name}")
            except Exception as e:
                logger.error(f"Failed to create JS bundle {bundle_name}: {e}")
        
        return created_bundles

class ImageOptimizer:
    """Image optimization utilities"""
    
    @staticmethod
    def optimize_images(image_folder: Path, quality: int = 85):
        """Optimize images in a folder"""
        try:
            from PIL import Image
        except ImportError:
            logger.warning("PIL not available for image optimization")
            return
        
        supported_formats = {'.jpg', '.jpeg', '.png', '.webp'}
        
        for image_path in image_folder.rglob('*'):
            if image_path.suffix.lower() in supported_formats:
                try:
                    with Image.open(image_path) as img:
                        # Convert to RGB if necessary
                        if img.mode in ('RGBA', 'LA', 'P'):
                            img = img.convert('RGB')
                        
                        # Optimize and save
                        img.save(image_path, optimize=True, quality=quality)
                        logger.info(f"Optimized image: {image_path.name}")
                        
                except Exception as e:
                    logger.error(f"Failed to optimize image {image_path}: {e}")

def setup_asset_optimization(app):
    """Setup asset optimization for Flask app"""
    optimizer = AssetOptimizer(app.static_folder)
    bundler = AssetBundler()
    
    # Create bundles in production
    if not app.debug:
        try:
            bundles = bundler.create_bundles(optimizer)
            app.config['ASSET_BUNDLES'] = bundles
            logger.info("Asset optimization completed")
        except Exception as e:
            logger.error(f"Asset optimization failed: {e}")
    
    # Add template helper for asset URLs
    @app.template_global()
    def asset_url(asset_name):
        """Template helper to get optimized asset URLs"""
        if app.debug:
            # In debug mode, use original assets
            return url_for('static', filename=asset_name)
        else:
            return optimizer.get_asset_url(asset_name)
    
    # Clean old assets periodically
    if not app.debug:
        try:
            optimizer.clean_old_assets()
        except Exception as e:
            logger.error(f"Failed to clean old assets: {e}")

# CLI command for asset optimization
def optimize_assets_command():
    """CLI command to optimize assets"""
    from flask import current_app
    
    optimizer = AssetOptimizer(current_app.static_folder)
    bundler = AssetBundler()
    
    print("Starting asset optimization...")
    
    # Create bundles
    bundles = bundler.create_bundles(optimizer)
    
    print(f"Created {len(bundles)} asset bundles:")
    for bundle_name, filename in bundles.items():
        print(f"  {bundle_name}: {filename}")
    
    # Clean old assets
    optimizer.clean_old_assets()
    print("Cleaned old asset versions")
    
    # Optimize images
    image_folder = Path(current_app.static_folder) / 'images'
    if image_folder.exists():
        ImageOptimizer.optimize_images(image_folder)
        print("Optimized images")
    
    print("Asset optimization completed!")

if __name__ == '__main__':
    # Can be run standalone for asset optimization
    optimize_assets_command()
