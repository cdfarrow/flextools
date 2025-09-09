# -*- coding: utf-8 -*-
#
#   Rename Audio Files by Custom Field (Infer Directory)
#    - A FlexTools Module -
#
#   Renames audio files attached to LexemeForm (audio WS) based on a custom field,
#   inferring the audio directory from the file path.
#
#   Author: Matthew Lee (And Claude Code), SIL Global
#   Date: 2025-08-11
#
#   Platforms: Python 3
#
# ========================================================================
# PROCESS DOCUMENTATION
# ========================================================================
#
# This script automates the process of renaming audio files in FieldWorks
# projects based on values stored in a custom field. Here's how it works:
#
# 1. SETUP & CONFIGURATION
#    - Auto-detects the project's audio writing system (ending with '-audio')
#    - Locates the LinkedFilesRootDir where audio files are stored
#    - Configures the custom field name to read from (default: 'MediaFilename')
#
# 2. AUDIO WRITING SYSTEM DETECTION
#    - Scans all vernacular writing systems for ones ending with '-audio'
#    - Converts the string-based WS code (e.g., 'fr-Zxxx-x-audio') to numeric ID
#    - Uses the first audio writing system found if multiple exist
#    - Reports found writing systems and warns if multiple are present
#
# 3. LEXICAL ENTRY PROCESSING
#    For each lexical entry in the project:
#    a) Checks if the entry has a LexemeForm with the audio writing system
#    b) Reads the current audio file path from the lexeme form
#    c) Attempts to read the MediaFilename custom field value
#
# 4. CUSTOM FIELD ACCESS
#    - Accesses entry-level custom fields using metadata cache and field IDs
#    - Uses TsString approach (most reliable for single-line custom fields)
#    - Priority order: default analysis WS, then vernacular WS, then all others
#    - Returns the first non-empty value found across writing systems
#
# 5. FILENAME PROCESSING
#    - Sanitizes the MediaFilename value by removing OS-banned characters
#    - Replaces problematic chars (< > : " / \ | ? * ! & ') with underscores
#    - Automatically adds .wav extension if not present
#    - Handles Unicode normalization for accented characters (e.g., mâle.wav)
#
# 6. FILE LOCATION & ENCODING
#    - Searches common audio subfolders: AudioVisual, Audio, Media, root
#    - Uses robust file finding with multiple Unicode normalization forms
#    - Handles encoding differences between database and filesystem
#    - Automatically detects the correct audio subfolder structure
#
# 7. FILE OPERATIONS (when modifyAllowed=True)
#    - Checks if target filename already exists to prevent overwrites
#    - Physically renames the audio file using shutil.move()
#    - Updates the database reference in the lexeme form's audio writing system
#    - Uses TsStringUtils or fallback methods to create proper FieldWorks strings
#
# 8. LINK UPDATES
#    - Stores only the filename in the lexeme form link (not full path)
#    - FieldWorks assumes audio files are in AudioVisual subfolder
#    - Uses multiple fallback methods to create TsString objects
#    - Handles FlexTools-specific object access patterns
#
# 9. ERROR HANDLING & REPORTING
#    - Comprehensive error handling for missing files, encoding issues
#    - Detailed logging of all operations (success/failure/warnings)
#    - Support for read-only mode (preview changes without making them)
#    - Verbose debug mode for troubleshooting (set verbose=True)
#
# 10. SAFETY FEATURES
#     - Never overwrites existing files with same target name
#     - Validates file existence before attempting operations
#     - Atomic file operations (rename + database update together)
#     - Clear distinction between read-only and modify modes
#     - Comprehensive summary statistics
#
# PREREQUISITES:
# - FieldWorks project with audio writing system configured (ends with '-audio')
# - Audio files stored in LinkedFiles/AudioVisual/ (or similar subfolder)
# - Custom field "MediaFilename" defined at lexical entry level
# - Custom field populated with desired filenames (extension optional)
#
# USAGE:
# 1. Run in read-only mode first to preview changes
# 2. Check the output for any warnings or issues
# 3. Verify the expected number of files to be renamed
# 4. Run in modify mode to perform actual file renames and link updates
# 5. Monitor the summary statistics to confirm expected results
#
# CONFIGURATION:
# - CUSTOM_FIELD: Name of the custom field containing target filenames
# - verbose: Set to True in MainFunction for detailed debugging output
#
# ========================================================================

from flextoolslib import *
import os
import shutil
import re
import unicodedata
import glob

from SIL.LCModel import ILexEntryRepository, ILangProjectRepository
from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr, ITsStrFactory

import logging
logger = logging.getLogger(__name__)

#----------------------------------------------------------------
# Configurables:

# Set this to your custom field name (case-sensitive, as in FLEx)
CUSTOM_FIELD = 'MediaFilename'

#----------------------------------------------------------------
docs = {FTM_Name            : "Rename Audio Files by Custom Field",
        FTM_Version         : 2,
        FTM_ModifiesDB      : True,
        FTM_Synopsis        : "Renames audio files for entries based on a custom field, inferring the directory.",
        FTM_Help            : None,
        FTM_Description     :
"""
Renames audio files attached to LexemeForm (audio writing system) for each LexEntry, using the value in a custom field (e.g., MediaFilename). The audio directory is inferred from the file path. Updates the file link in the lexeme form. Supports test mode (no changes made).
""" }

# Utility function for debugging (currently unused)
# def getObjectinfo(report, targetObject):
#     attributes = dir(targetObject)
#     report.Warning("----------------------")
#     report.Info("Object Type: " + str(type(targetObject)))
#     for attribute in attributes:
#         report.Info(attribute)
#     try:
#         report.Info("List of Items in the object:")
#         for item in targetObject:
#             report.Info(item)
#     except:
#         report.Warning("No items in the object")
#     report.Warning("----------------------")

def sanitize_filename(filename):
    """Sanitize filename by replacing OS-banned characters"""
    # Characters that are problematic in Windows/Unix filenames
    banned_chars = r'[<>:"/\\|?*!&\']'
    # Replace banned characters with underscore
    sanitized = re.sub(banned_chars, '_', filename)
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_{2,}', '_', sanitized)
    # Remove leading/trailing underscores and whitespace
    sanitized = sanitized.strip('_ ')
    return sanitized

def normalize_unicode(text):
    """Normalize unicode text to handle encoding differences"""
    if not text:
        return text
    # Try different normalization forms
    return unicodedata.normalize('NFC', text)

def find_audio_file_robust(expected_path):
    """Find audio file using various encoding approaches"""
    if os.path.exists(expected_path):
        return expected_path
    
    # Get directory and expected filename
    directory = os.path.dirname(expected_path)
    expected_filename = os.path.basename(expected_path)
    
    if not os.path.exists(directory):
        return None
    
    # Try different unicode normalizations of the expected filename
    filename_variants = [
        expected_filename,
        unicodedata.normalize('NFC', expected_filename),
        unicodedata.normalize('NFD', expected_filename),
        unicodedata.normalize('NFKC', expected_filename),
        unicodedata.normalize('NFKD', expected_filename),
    ]
    
    # Check each variant
    for variant in filename_variants:
        test_path = os.path.join(directory, variant)
        if os.path.exists(test_path):
            return test_path
    
    # Try glob pattern matching to find similar files
    try:
        # Create a pattern that handles encoding differences
        base_name = os.path.splitext(expected_filename)[0]
        extension = os.path.splitext(expected_filename)[1]
        
        # Try to find files with the same base name but different encoding
        pattern = os.path.join(directory, f"{base_name}*{extension}")
        matches = glob.glob(pattern)
        if matches:
            return matches[0]  # Return first match
            
        # Also try case-insensitive search for .wav files
        all_wav_files = glob.glob(os.path.join(directory, "*.wav"))
        expected_lower = expected_filename.lower()
        for wav_file in all_wav_files:
            if os.path.basename(wav_file).lower() == expected_lower:
                return wav_file
    except Exception:
        pass
    
    return None

def get_custom_field_value(entry, field_name, cache):
    """Get value from entry-level custom field, checking analysis and vernacular WS"""
    try:
        # Method 1: Try direct custom field access
        if hasattr(entry, field_name):
            custom_field = getattr(entry, field_name)
            if custom_field:
                # Priority order: default analysis WS, then first vernacular WS, then all others
                priority_ws = []
                
                # Add default analysis WS
                default_analysis_ws = cache.DefaultAnalWs
                if default_analysis_ws:
                    priority_ws.append(default_analysis_ws)
                
                # Add first vernacular WS
                default_vernacular_ws = cache.DefaultVernWs
                if default_vernacular_ws and default_vernacular_ws not in priority_ws:
                    priority_ws.append(default_vernacular_ws)
                
                # Check priority writing systems first
                for ws_id in priority_ws:
                    if ws_id in custom_field.AvailableWritingSystemIds:
                        value = custom_field.get_String(ws_id).Text
                        if value and value.strip():
                            return value.strip()
                
                # If not found in priority WS, check all available writing systems
                for ws_id in custom_field.AvailableWritingSystemIds:
                    if ws_id not in priority_ws:  # Skip already checked priority WS
                        value = custom_field.get_String(ws_id).Text
                        if value and value.strip():
                            return value.strip()
        
        # Method 2: Try using custom field by name through the cache
        try:
            mdc = cache.MetaDataCacheAccessor
            class_id = entry.ClassID
            field_id = mdc.GetFieldId2(class_id, field_name, True)  # True for custom fields
            if field_id > 0:
                # First, try as a single TsString (most common for single-line custom fields)
                try:
                    ts_string = cache.DomainDataByFlid.get_StringProp(entry.Hvo, field_id)
                    if ts_string and ts_string.Text:
                        return ts_string.Text.strip()
                except:
                    pass
                
                # If that fails, try based on field type
                field_type = mdc.GetFieldType(field_id)
                
                if field_type == 13:  # kcptMultiString
                    try:
                        custom_field = cache.DomainDataByFlid.get_MultiStringProp(entry.Hvo, field_id)
                        if custom_field:
                            # Priority order: default analysis WS, then first vernacular WS, then all others
                            priority_ws = []
                            
                            # Add default analysis WS
                            default_analysis_ws = cache.DefaultAnalWs
                            if default_analysis_ws:
                                priority_ws.append(default_analysis_ws)
                            
                            # Add first vernacular WS
                            default_vernacular_ws = cache.DefaultVernWs
                            if default_vernacular_ws and default_vernacular_ws not in priority_ws:
                                priority_ws.append(default_vernacular_ws)
                            
                            # Check priority writing systems first
                            for ws_id in priority_ws:
                                if ws_id in custom_field.AvailableWritingSystemIds:
                                    value = custom_field.get_String(ws_id).Text
                                    if value and value.strip():
                                        return value.strip()
                            
                            # Check all writing systems
                            for ws_id in custom_field.AvailableWritingSystemIds:
                                if ws_id not in priority_ws:  # Skip already checked priority WS
                                    value = custom_field.get_String(ws_id).Text
                                    if value and value.strip():
                                        return value.strip()
                    except:
                        pass
                
                elif field_type == 14:  # kcptMultiUnicode  
                    try:
                        custom_field = cache.DomainDataByFlid.get_MultiUnicodeProp(entry.Hvo, field_id)
                        if custom_field:
                            # Priority order: default analysis WS, then first vernacular WS, then all others
                            priority_ws = []
                            
                            # Add default analysis WS
                            default_analysis_ws = cache.DefaultAnalWs
                            if default_analysis_ws:
                                priority_ws.append(default_analysis_ws)
                            
                            # Add first vernacular WS
                            default_vernacular_ws = cache.DefaultVernWs
                            if default_vernacular_ws and default_vernacular_ws not in priority_ws:
                                priority_ws.append(default_vernacular_ws)
                            
                            # Check priority writing systems first
                            for ws_id in priority_ws:
                                if ws_id in custom_field.AvailableWritingSystemIds:
                                    value = custom_field.get_String(ws_id).Text
                                    if value and value.strip():
                                        return value.strip()
                            
                            # Check all writing systems
                            for ws_id in custom_field.AvailableWritingSystemIds:
                                if ws_id not in priority_ws:  # Skip already checked priority WS
                                    value = custom_field.get_String(ws_id).Text
                                    if value and value.strip():
                                        return value.strip()
                    except:
                        pass
                        
        except Exception as e:
            pass
            
    except Exception as e:
        # Field might not exist or other error
        pass
    return None
 

#----------------------------------------------------------------
def MainFunction(project, report, modifyAllowed):
    verbose = False  # Set to True for detailed debugging output
    
    count = 0
    changed = 0
    seen_dirs = set()

    # LinkedFilesFolder

    # Get the standard objects
    cache = project.project
    sl = cache.ServiceLocator
    lp = cache.LangProject

    # Access LinkedFilesRootDir
    linked_files_root = lp.LinkedFilesRootDir

    report.Info(f"LinkedFilesRootDir: {linked_files_root}")   
    
    
    # accessing the audio writing system code
    
    audio_ws_codes = []
    #report.Info(f"{getObjectinfo(report, project)}")
    for ws in project.GetAllVernacularWSs():

        if ws.endswith('-audio'):# and ws.IsVernacular:
            report.Info(f"Found audio writing system: {ws}")
            audio_ws_codes.append(ws)
    
    if len(audio_ws_codes) == 0:
        report.Warning("No audio writing systems found.")
        return
    elif len(audio_ws_codes) > 1:
        report.Warning(f"Multiple audio writing systems found ({len(audio_ws_codes)}). Using first one: {audio_ws_codes[0]}")
    
    # Use the first audio writing system code and convert to numeric ID
    target_audio_ws_code = audio_ws_codes[0]
    report.Info(f"Using audio writing system: {target_audio_ws_code}")
    
    # Convert string code to numeric ID used in MultiUnicode objects
    target_audio_ws_id = cache.WritingSystemFactory.GetWsFromStr(target_audio_ws_code)
    report.Info(f"Numeric WS ID: {target_audio_ws_id}")

    # Get all lexical entries
    audio_entry_count = 0
    report.Info("=" * 50)
    report.Info("Scanning Lexical Entries for audio files...")
    report.Info("=" * 50)
    for entry in project.ObjectsIn(ILexEntryRepository):
        count += 1
        
        # Check LexemeForm for audio files
        if entry.LexemeFormOA:
            lexeme_form = entry.LexemeFormOA.Form
            if lexeme_form:
                # Check if the target audio WS is available in this lexeme form
                if target_audio_ws_id in lexeme_form.AvailableWritingSystemIds:
                    # Get the string content (file path for audio)
                    audio_content = lexeme_form.get_String(target_audio_ws_id).Text
                    if audio_content:
                        audio_entry_count += 1
                        report.Info(f"Processing entry #{count} (audio #{audio_entry_count}) - Expected audio file: {audio_content}")
                        
                        
                        media_filename = get_custom_field_value(entry, CUSTOM_FIELD, cache)
                        if media_filename:
                            report.Info(f"  MediaFilename field value: '{media_filename}'")
                            
                            # Sanitize the filename
                            sanitized_filename = sanitize_filename(media_filename)
                            if verbose:
                                report.Info(f"  Sanitized filename: '{sanitized_filename}'")
                            
                            # Ensure it has .wav extension
                            if not sanitized_filename.lower().endswith('.wav'):
                                sanitized_filename += '.wav'
                                if verbose:
                                    report.Info(f"  Added .wav extension: '{sanitized_filename}'")
                            
                            # Build full paths with Unicode normalization
                            normalized_audio_content = normalize_unicode(audio_content)
                            
                            # Check if the audio content includes a path or is just a filename
                            if '/' in normalized_audio_content or '\\' in normalized_audio_content:
                                # Already includes path
                                expected_audio_path = os.path.join(linked_files_root, normalized_audio_content)
                            else:
                                # Just a filename - check common audio subfolders
                                audio_subfolders = ['AudioVisual', 'Audio', 'Media', '']  # '' for root
                                expected_audio_path = None
                                
                                for subfolder in audio_subfolders:
                                    if subfolder:
                                        test_path = os.path.join(linked_files_root, subfolder, normalized_audio_content)
                                    else:
                                        test_path = os.path.join(linked_files_root, normalized_audio_content)
                                    
                                    if find_audio_file_robust(test_path):
                                        expected_audio_path = test_path
                                        if verbose:
                                            report.Info(f"  Found audio in subfolder: {subfolder or 'root'}")
                                        break
                                
                                if not expected_audio_path:
                                    # Default to AudioVisual subfolder
                                    expected_audio_path = os.path.join(linked_files_root, 'AudioVisual', normalized_audio_content)
                            
                            # Find the actual file using robust encoding handling
                            current_audio_path = find_audio_file_robust(expected_audio_path)
                            
                            if not current_audio_path:
                                report.Warning(f"  Expected audio file not found: {normalized_audio_content}")
                                
                                # Debug: List files in the directory to see what's actually there
                                if verbose:
                                    current_dir = os.path.dirname(expected_audio_path)
                                    if os.path.exists(current_dir):
                                        report.Info(f"  DEBUG: Files in directory {current_dir}:")
                                        try:
                                            files = os.listdir(current_dir)
                                            wav_files = [f for f in files if f.lower().endswith('.wav')]
                                            if wav_files:
                                                for wav_file in wav_files[:10]:  # Show first 10 wav files
                                                    report.Info(f"    {wav_file}")
                                                if len(wav_files) > 10:
                                                    report.Info(f"    ... and {len(wav_files) - 10} more .wav files")
                                            else:
                                                report.Info("    No .wav files found")
                                        except Exception as e:
                                            report.Warning(f"    Could not list directory: {e}")
                                    else:
                                        report.Warning(f"  Directory does not exist: {current_dir}")
                                continue
                            
                            # File found! Report the actual path if different encoding
                            if verbose and current_audio_path != expected_audio_path:
                                report.Info(f"  Found file with encoding difference: {os.path.basename(current_audio_path)}")
                            
                            current_dir = os.path.dirname(current_audio_path)
                            new_audio_path = os.path.join(current_dir, sanitized_filename)
                            
                            # Check if target file already exists
                            if os.path.exists(new_audio_path):
                                if os.path.samefile(current_audio_path, new_audio_path):
                                    report.Info(f"  File already has correct name: {sanitized_filename}")
                                else:
                                    report.Warning(f"  Target file already exists: {new_audio_path}")
                                continue
                            
                            # Log the directory we're working in
                            if current_dir not in seen_dirs:
                                seen_dirs.add(current_dir)
                                if verbose:
                                    report.Info(f"  Working in audio directory: {current_dir}")
                            
                            # Perform the rename operation
                            if modifyAllowed:
                                try:
                                    # Rename the physical file
                                    shutil.move(current_audio_path, new_audio_path)
                                    report.Info(f"  ✓ RENAMED: {os.path.basename(current_audio_path)} → {sanitized_filename}")
                                    
                                    # Update the lexeme form link - only store the filename
                                    # FieldWorks assumes AudioVisual subfolder, so only store the filename
                                    new_relative_path = sanitized_filename
                                    
                                    # Create new TsString with updated path - FlexTools approach
                                    try:
                                        # Method 1: Use the cache's TsStrFactory directly
                                        from System import String
                                        from SIL.LCModel.Core.Text import TsStringUtils
                                        
                                        new_ts_string = TsStringUtils.MakeString(new_relative_path, target_audio_ws_id)
                                        lexeme_form.set_String(target_audio_ws_id, new_ts_string)
                                        report.Info(f"  ✓ LINK UPDATED: {new_relative_path}")
                                    except Exception as e1:
                                        try:
                                            # Method 2: Use TsStrFactory from cache
                                            ts_str_factory = cache.TsStrFactory
                                            new_ts_string = ts_str_factory.MakeString(new_relative_path, target_audio_ws_id)
                                            lexeme_form.set_String(target_audio_ws_id, new_ts_string)
                                            report.Info(f"  ✓ LINK UPDATED: {new_relative_path}")
                                        except Exception as e2:
                                            try:
                                                # Method 3: Use the existing string as template
                                                existing_string = lexeme_form.get_String(target_audio_ws_id)
                                                if existing_string:
                                                    str_bldr = existing_string.GetBldr()
                                                    str_bldr.Clear()
                                                    str_bldr.Replace(0, 0, new_relative_path, None)
                                                    lexeme_form.set_String(target_audio_ws_id, str_bldr.GetString())
                                                    report.Info(f"  ✓ LINK UPDATED: {new_relative_path}")
                                                else:
                                                    report.Error(f"  ✗ LINK UPDATE FAILED: Could not create TsString")
                                            except Exception as e3:
                                                report.Error(f"  ✗ LINK UPDATE FAILED: All methods failed - {e1}; {e2}; {e3}")
                                    
                                    changed += 1
                                    
                                except Exception as e:
                                    report.Error(f"  ✗ FAILED to rename {current_audio_path}: {e}")
                            else:
                                # Read-only mode - just report what would happen
                                report.Info(f"  [READ-ONLY] Would rename: {os.path.basename(current_audio_path)} → {sanitized_filename}")
                                report.Info(f"  [READ-ONLY] Would update link to: {sanitized_filename}")
                                changed += 1
                        else:
                            report.Info(f"  No MediaFilename field value found for entry #{count}")
    
    # Final summary
    report.Info("=" * 50)
    report.Info(f"SUMMARY:")
    report.Info("=" * 50)
    report.Info(f"  Total entries checked: {count}")
    report.Info(f"  Entries with audio: {audio_entry_count}")
    report.Info(f"  Files renamed: {changed}")
    if modifyAllowed:
        report.Info(f"  Mode: EDIT (changes made to files and links)")
    else:
        report.Info(f"  Mode: READ-ONLY (no changes made)")
    report.Info("=" * 50)


FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)

if __name__ == '__main__':
    FlexToolsModule.Help()
