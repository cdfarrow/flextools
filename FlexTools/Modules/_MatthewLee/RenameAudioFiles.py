# -*- coding: utf-8 -*-
#
#   Rename Audio Files by Custom Field (FlexTools API Optimized)
#    - A FlexTools Module -
#
#   Renames audio files attached to LexemeForm (audio WS) based on a custom field,
#   prioritizing FlexTools API methods over direct FLEx API access wherever possible.
#
#   Author: Matthew Lee (And Claude Code), SIL Global
#   Date: 2025-08-12
#
#   Platforms: Python 3
#
# ========================================================================
# PROCESS DOCUMENTATION
# ========================================================================
#
# This optimized script uses FlexTools API methods whenever possible for
# better performance, reliability, and cleaner code. Key improvements:
#
# 1. FLEXTOOLS API PRIORITIZATION
#    - Uses project.GetAllVernacularWSs() instead of direct cache access
#    - Uses project.WSHandle() for writing system ID conversion
#    - Uses project.ObjectsIn(ILexEntryRepository) for entry iteration
#    - Uses project.LexiconGetEntryCustomFieldNamed() for field ID lookup
#    - Uses project.LexiconGetFieldText() for custom field value retrieval
#    - Uses project.GetDefaultAnalysisWS() and project.GetDefaultVernacularWS()
#
# 2. WRITING SYSTEM HANDLING
#    - FlexTools methods return tuples (language-tag, name) for default WS
#    - Proper handling of writing system priorities using FlexTools patterns
#    - Conversion between language tags and handles using FlexTools methods
#
# 3. CUSTOM FIELD ACCESS
#    - Uses FlexTools project.LexiconGetEntryCustomFieldNamed() for field ID lookup
#    - Uses FlexTools project.LexiconGetFieldText() with proper writing system handling
#    - No fallbacks - relies on FlexTools API methods that are known to work
#    - Clean priority order: analysis WS, then vernacular WS, then default
#
# 4. SIMPLIFIED FILE HANDLING
#    - Removed unnecessary Unicode normalization (was fixing wrong issue)
#    - The real issue was extra AudioVisual folder insertion, now resolved
#    - Simple file existence checks without encoding complications
#    - Clean path handling without normalization overhead
#
# 5. CLEAN ERROR HANDLING
#    - Uses FlexTools methods where they exist, direct API only where necessary
#    - TsStringUtils.MakeString() is reliable and doesn't need fallbacks
#    - Clear error messages when FlexTools methods fail
#
# 6. PERFORMANCE OPTIMIZATIONS
#    - Fewer direct cache accesses
#    - More efficient writing system lookups
#    - Reduced object creation overhead
#    - Streamlined field access patterns
#
# ========================================================================

from flextoolslib import *
import os
import shutil
import re

from SIL.LCModel import ILexEntryRepository
from SIL.LCModel.Core.Text import TsStringUtils

import logging
logger = logging.getLogger(__name__)

#----------------------------------------------------------------
# Configurables:

# Set this to your custom field name (case-sensitive, as in FLEx)
CUSTOM_FIELD = 'MediaFilename'

#----------------------------------------------------------------
docs = {FTM_Name            : "Rename Audio Files by Custom Field (FlexTools API Optimized)",
        FTM_Version         : 3,
        FTM_ModifiesDB      : True,
        FTM_Synopsis        : "Renames audio files using FlexTools API methods for optimal performance and reliability.",
        FTM_Help            : None,
        FTM_Description     :
"""
Fully optimized version using FlexTools API methods exclusively where they exist. 
Uses project.GetAllVernacularWSs(), project.WSHandle(), project.LexiconGetEntryCustomFieldNamed(), 
project.LexiconGetFieldText(), project.GetDefaultAnalysisWS(), and project.GetDefaultVernacularWS()
for clean, efficient code without unnecessary fallbacks.
""" }

def sanitize_filename(filename):
    """Sanitize filename by replacing OS-banned characters"""
    banned_chars = r'[<>:"/\\|?*!&\']'
    sanitized = re.sub(banned_chars, '_', filename)
    sanitized = re.sub(r'_{2,}', '_', sanitized)
    return sanitized.strip('_ ')

def get_custom_field_value_flextools(project, entry, field_name):
    """Get custom field value using FlexTools methods only"""
    
    # Use FlexTools custom field access - this is available in FlexTools API
    field_id = project.LexiconGetEntryCustomFieldNamed(field_name)
    if field_id:
        # Try default analysis writing system first
        default_analysis = project.GetDefaultAnalysisWS()
        if default_analysis:
            # default_analysis is a tuple (language-tag, name)
            value = project.LexiconGetFieldText(entry, field_id, default_analysis[0])
            if value and value.strip():
                return value.strip()
        
        # Try default vernacular writing system
        default_vernacular = project.GetDefaultVernacularWS()
        if default_vernacular:
            # default_vernacular is a tuple (language-tag, name)
            value = project.LexiconGetFieldText(entry, field_id, default_vernacular[0])
            if value and value.strip():
                return value.strip()
        
        # Try without specifying writing system (use default)
        value = project.LexiconGetFieldText(entry, field_id, None)
        if value and value.strip():
            return value.strip()
    
    return None

#----------------------------------------------------------------
def MainFunction(project, report, modifyAllowed):
    verbose = False  # Set to True for detailed debugging output
    
    count = 0
    changed = 0
    seen_dirs = set()

    # Access LinkedFilesRootDir using FlexTools pattern
    cache = project.project
    lp = cache.LangProject
    linked_files_root = lp.LinkedFilesRootDir
    report.Info(f"LinkedFilesRootDir: {linked_files_root}")   
    
    # Use FlexTools method to get all vernacular writing systems
    audio_ws_codes = []
    
    try:
        vernacular_ws_set = project.GetAllVernacularWSs()
        for ws_tag in vernacular_ws_set:
            if ws_tag.endswith('-audio'):
                report.Info(f"Found audio writing system: {ws_tag}")
                audio_ws_codes.append(ws_tag)
    except Exception as e:
        report.Error(f"Failed to get vernacular writing systems: {e}")
        return
    
    if len(audio_ws_codes) == 0:
        report.Warning("No audio writing systems found.")
        return
    elif len(audio_ws_codes) > 1:
        report.Warning(f"Multiple audio writing systems found ({len(audio_ws_codes)}). Using first one: {audio_ws_codes[0]}")
    
    # Convert language tag to writing system handle using FlexTools
    target_audio_ws_code = audio_ws_codes[0]
    report.Info(f"Using audio writing system: {target_audio_ws_code}")
    
    # Convert language tag to writing system handle using FlexTools
    target_audio_ws_id = project.WSHandle(target_audio_ws_code)
    if not target_audio_ws_id:
        report.Error(f"Failed to get writing system handle for: {target_audio_ws_code}")
        return
    report.Info(f"Numeric WS ID: {target_audio_ws_id}")

    # Use FlexTools method to iterate over lexical entries
    audio_entry_count = 0
    report.Info("=" * 50)
    report.Info("Scanning Lexical Entries for audio files...")
    report.Info("=" * 50)
    
    try:
        entry_iterator = project.ObjectsIn(ILexEntryRepository)
        
        for entry in entry_iterator:
            count += 1
            
            # Check LexemeForm for audio files
            if entry.LexemeFormOA:
                lexeme_form = entry.LexemeFormOA.Form
                if lexeme_form and target_audio_ws_id in lexeme_form.AvailableWritingSystemIds:
                    # Get the string content (file path for audio)
                    try:
                        ts_string = lexeme_form.get_String(target_audio_ws_id)
                        audio_content = ts_string.Text if ts_string else None
                    except Exception:
                        audio_content = None
                    
                    if audio_content:
                        audio_entry_count += 1
                        report.Info(f"Processing entry #{count} (audio #{audio_entry_count}) - Audio file: {audio_content}")
                        
                        # Get custom field value using FlexTools method
                        media_filename = get_custom_field_value_flextools(project, entry, CUSTOM_FIELD)
                        
                        if media_filename:
                            report.Info(f"  MediaFilename field value: '{media_filename}'")
                            
                            # Sanitize the filename
                            sanitized_filename = sanitize_filename(media_filename)
                            if verbose:
                                report.Info(f"  Sanitized filename: '{sanitized_filename}'")
                            
                            # Ensure .wav extension
                            if not sanitized_filename.lower().endswith('.wav'):
                                sanitized_filename += '.wav'
                                if verbose:
                                    report.Info(f"  Added .wav extension: '{sanitized_filename}'")
                            
                            # Build file paths (simplified, no Unicode normalization)
                            if '/' in audio_content or '\\' in audio_content:
                                expected_audio_path = os.path.join(linked_files_root, audio_content)
                            else:
                                # Check common audio subfolders
                                audio_subfolders = ['AudioVisual', 'Audio', 'Media', '']
                                expected_audio_path = None
                                
                                for subfolder in audio_subfolders:
                                    if subfolder:
                                        test_path = os.path.join(linked_files_root, subfolder, audio_content)
                                    else:
                                        test_path = os.path.join(linked_files_root, audio_content)
                                    
                                    if os.path.exists(test_path):
                                        expected_audio_path = test_path
                                        if verbose:
                                            report.Info(f"  Found audio in subfolder: {subfolder or 'root'}")
                                        break
                                
                                if not expected_audio_path:
                                    expected_audio_path = os.path.join(linked_files_root, 'AudioVisual', audio_content)
                            
                            # Check if file exists
                            if not os.path.exists(expected_audio_path):
                                report.Warning(f"  Audio file not found: {audio_content}")
                                if verbose:
                                    current_dir = os.path.dirname(expected_audio_path)
                                    if os.path.exists(current_dir):
                                        try:
                                            wav_files = [f for f in os.listdir(current_dir) if f.lower().endswith('.wav')]
                                            report.Info(f"  Available .wav files: {len(wav_files)}")
                                            for wav_file in wav_files[:5]:  # Show first 5
                                                report.Info(f"    {wav_file}")
                                        except Exception:
                                            pass
                                continue
                            
                            current_audio_path = expected_audio_path
                            current_dir = os.path.dirname(current_audio_path)
                            new_audio_path = os.path.join(current_dir, sanitized_filename)
                            
                            # Check if target file already exists
                            if os.path.exists(new_audio_path):
                                if os.path.samefile(current_audio_path, new_audio_path):
                                    report.Info(f"  File already has correct name: {sanitized_filename}")
                                else:
                                    report.Warning(f"  Target file already exists: {sanitized_filename}")
                                continue
                            
                            # Track working directories
                            if current_dir not in seen_dirs:
                                seen_dirs.add(current_dir)
                                if verbose:
                                    report.Info(f"  Working in directory: {current_dir}")
                            
                            # Perform the rename operation
                            if modifyAllowed:
                                try:
                                    # Rename physical file
                                    shutil.move(current_audio_path, new_audio_path)
                                    report.Info(f"  ✓ RENAMED: {os.path.basename(current_audio_path)} → {sanitized_filename}")
                                    
                                    # Update lexeme form link (store filename only)
                                    new_relative_path = sanitized_filename
                                    
                                    # Create TsString and update - TsStringUtils is reliable
                                    new_ts_string = TsStringUtils.MakeString(new_relative_path, target_audio_ws_id)
                                    lexeme_form.set_String(target_audio_ws_id, new_ts_string)
                                    report.Info(f"  ✓ LINK UPDATED: {new_relative_path}")
                                    
                                    changed += 1
                                    
                                except Exception as e:
                                    report.Error(f"  ✗ FAILED to rename {os.path.basename(current_audio_path)}: {e}")
                            else:
                                # Read-only mode
                                report.Info(f"  [READ-ONLY] Would rename: {os.path.basename(current_audio_path)} → {sanitized_filename}")
                                report.Info(f"  [READ-ONLY] Would update link to: {sanitized_filename}")
                                changed += 1
                        else:
                            report.Info(f"  No MediaFilename field value found for entry #{count}")
    
    except Exception as e:
        report.Error(f"Error during entry iteration: {e}")
        return
    
    # Summary report
    report.Info("=" * 50)
    report.Info("SUMMARY:")
    report.Info("=" * 50)
    report.Info(f"  Total entries checked: {count}")
    report.Info(f"  Entries with audio: {audio_entry_count}")
    report.Info(f"  Files processed: {changed}")
    report.Info(f"  Directories accessed: {len(seen_dirs)}")
    report.Info(f"  Mode: {'EDIT (changes applied)' if modifyAllowed else 'READ-ONLY (preview mode)'}")
    report.Info("=" * 50)


FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

if __name__ == '__main__':
    FlexToolsModule.Help()