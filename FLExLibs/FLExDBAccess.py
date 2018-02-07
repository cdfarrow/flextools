#
#   FLExDBAccess.py
#
#   Class: Fieldworks Language Explorer database access functions 
#          via FDO (FieldWorks Data Objects) API.
#
#
#   Platform: Python.NET
#             (ITsString doesn't work in IRONPython)
#             FieldWorks Version 7 & 8
#
#   By: Craig Farrow
#       2008 - 2014
#
#

import codecs
import sys
sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

# Initialise low-level FDO access
import FLExFDO

import clr
clr.AddReference("System")
import System

from SIL.FieldWorks.FDO import (ICmObjectRepository,
    ILexEntryRepository, ILexEntry, LexEntryTags,
                         ILexSense, LexSenseTags,
    IWfiWordformRepository, WfiWordformTags,
                            WfiGlossTags,
    IWfiAnalysisRepository, IWfiAnalysis, WfiAnalysisTags,
                            WfiMorphBundleTags,
    ITextRepository,
    IReversalIndex, IReversalIndexEntry, ReversalIndexEntryTags,
    IMoMorphType,
    SpecialWritingSystemCodes,
    IMultiStringAccessor,
                                
    FDOInvalidFieldException,
    IUndoStackManager,
    )

import SIL.FieldWorks.Common.FwUtils

from SIL.CoreImpl import CellarPropertyType
from SIL.FieldWorks.Common.COMInterfaces import ITsString, ITsStrBldr
##from SIL.FieldWorks.Common.COMInterfaces import TsStrFactoryClass, ITsStrFactory

##from SIL.FieldWorks.Common.FwUtils import LanguageDefinitionFactory
##from SIL.FieldWorks.Common.FwUtils import LanguageDefinition


#--- Exceptions ------------------------------------------------------

class FDA_DatabaseError(Exception):
    """Exception raised for any problems opening or using the database.

    Attributes:
        - message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message

class FDA_ReadOnlyError(FDA_DatabaseError):
    def __init__(self):
        FDA_DatabaseError.__init__(self,
            "Module error: Trying to write to the database without database changes enabled.")
    
class FDA_WritingSystemError(FDA_DatabaseError):
    def __init__(self, writingSystemName):
        FDA_DatabaseError.__init__(self,
            "Module error: Invalid Writing System for this database: %s" % writingSystemName)

class FDA_DLLError(Exception):
    """Exception raised for a COM error, which indicates that the
       FwKernel and Language DLLs can't be found.

    Attributes:
        - message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message

#-----------------------------------------------------------
   
class FLExDBAccess (object):
    """
    Class for accessing a FieldWorks database. The methods here
    hide the gory details of FDO.
    For quick testing, db and lp can be used directly; However, for
    continued use new methods should be added to this class.
    """
    
    def GetDatabaseNames(self):
        """
        Return a list of the FieldWorks databases available on this machine.
        """
        
        return FLExFDO.GetListOfDatabases()

    def OpenDatabase(self, dbName, writeEnabled = False, verbose = False):
        """
        Open the database given by dbName:
            - Either the full path including ".fwdata" suffix, or
            - The name only, opened from the default project location.
            
        The verbose flag controls logging/debug messages to the console.
        The writeEnabled flag configures FW to accept database changes, and
        saves those when this object is deleted. It will also be used to
        open the FW database in read-only mode so that FW doesn't have to
        be closed for read-only operations. (Awaiting support in a future
        release of FW)
        """

        try:
            self.db = FLExFDO.OpenDatabase(dbName, writeEnabled)
            
        except FLExFDO.StartupException, e:
            raise FDA_DatabaseError("Fieldworks database is locked. Close Fieldworks or this program and try again.")

        except (System.IO.FileNotFoundException,
                System.Runtime.InteropServices.COMException), e:
            # Problem with Fieldworks DLLs.
            raise FDA_DLLError(e.Message)

        if self.db:
            if verbose:
                print
                print "\tFieldworks Database:",  self.db.ProjectId.UiName
                print 
        else:
            msg = "OpenDatabase failed! Check database name: '%s'" % dbName
            if verbose: print msg
            raise FDA_DatabaseError(msg)


        self.lp    = self.db.LangProject
        self.lexDB = self.lp.LexDbOA
        
        # Set up FieldWorks for making changes to the database.
        # All changes will be automatically saved when this object is
        # deleted.

        self.writeEnabled = writeEnabled
        
        if self.writeEnabled:
            try:
                # This must be called before calling any methods that change
                # the database.
                self.db.MainCacheAccessor.BeginNonUndoableTask()
            except System.InvalidOperationException:
                raise FDA_DatabaseError("BeginNonUndoableTask() failed.")


            
    def __del__(self):
        if hasattr(self, "db"):
            if self.writeEnabled:
                # This must be called to mirror the call to BeginNonUndoableTask().
                self.db.MainCacheAccessor.EndNonUndoableTask()
                # Save all changes to disk. (EndNonUndoableTask)
                usm = self.db.ServiceLocator.GetInstance(IUndoStackManager)
                usm.Save()                
            try:
                #print "Calling self.db.Dispose()"
                # TODO: This is failing with a COM error (memory disposal problem)
                # with the Lela-Teli dbs only.
                self.db.Dispose()
                del self.db
                #print "FLExDBAccess.__del__: success"
                return
            except:
                #import traceback
                #print "FLExDBAccess.__del__:\n %s\n" % (traceback.format_exc())
                raise
                pass
            #print "FLExDBAccess.__del__: failed"


    # --- String Utilities ---

    def BestStr(self, stringObj):
        """
        Generic string extraction function returning the best Analysis or Vernacular string.
        """
        if not stringObj: raise ValueError
        
        s = ITsString(stringObj.BestAnalysisVernacularAlternative).Text
        return u"" if s == "***" else s
        
    # --- FDO Utilities ---
    
    def UnpackNestedPossibilityList(self, possibilityList, flat):
        """
        Returns a nested or flat list of a Fieldworks Possibility List.
        
        Return items are objects with properties/methods:
            - Hvo         - ID (value not the same across databases)
            - Guid        - Global Unique ID (same across all databases)
            - ToString()  - String representation.
        """
        for i in possibilityList:
            yield i
            if flat:
                for j in self.UnpackNestedPossibilityList(i.SubPossibilitiesOS, flat):
                    yield j
            else:
                l = list(self.UnpackNestedPossibilityList(i.SubPossibilitiesOS, flat))
                if l: yield l
    
    # --- Global: Writing Systems ---

    def GetAllVernacularWSs(self):
        """
        Returns a set of language tags for all vernacular writing systems used
        in this database.
        """
        return set(self.lp.CurVernWss.split())
            
    def GetAllAnalysisWSs(self):
        """
        Returns a set of language tags for all analysis writing systems used
        in this database.
        """
        return set(self.lp.CurAnalysisWss.split())

    def GetWritingSystems(self):
        """
        Returns the Writing Systems that are active in this database as a
        list of tuples: (Name, Language-tag, Handle, IsVernacular).
        Use the Language-tag when specifying Writing System to other
        functions.
        """

        VernWSSet = self.GetAllVernacularWSs()
        AnalWSSet = self.GetAllAnalysisWSs()
        
        WSList = []
        # The names of WS associated with this DB.
        # Sorted and with no duplicates.
        for x in self.db.ServiceLocator.WritingSystems.AllWritingSystems:
            if x.Id in VernWSSet:
                isVern = True
            elif x.Id in AnalWSSet:
                isVern = False
            else:
                continue        # Skip non-active WSs
            WSList.append( (x.DisplayLabel, x.Id, x.Handle, isVern) )
        return WSList

    def WSUIName(self, languageTagOrHandle):
        """
        Returns the UI name of the writing system for the given languageTag or Handle.
        Ignores case and '-'/'_' differences.
        Returns None if the language tag is not found.
        """

        if isinstance(languageTagOrHandle, (str, unicode)):
            languageTagOrHandle = self.__NormaliseLangTag(languageTagOrHandle)
        
        try:
            return self.__WSNameCache[languageTagOrHandle]
        except AttributeError:
            # Create a lookup table on-demand.
            self.__WSNameCache = {}
            for x in self.db.ServiceLocator.WritingSystems.AllWritingSystems:
                langTag = self.__NormaliseLangTag(x.Id)
                self.__WSNameCache[langTag] = x.DisplayLabel
                self.__WSNameCache[x.Handle] = x.DisplayLabel
            # Recursive:
            return self.WSUIName(languageTagOrHandle)
        except KeyError:
            return None

    def WSHandle(self, languageTag):
        """
        Returns the Handle of the writing system for the given languageTag.
        Ignores case and '-'/'_' differences.
        Returns None if the language tag is not found.
        """
        
        languageTag = self.__NormaliseLangTag(languageTag)
        
        try:
            return self.__WSLCIDCache[languageTag]
        except AttributeError:
            # Create a lookup table on-demand.
            self.__WSLCIDCache = {}
            for x in self.db.ServiceLocator.WritingSystems.AllWritingSystems:
                langTag = self.__NormaliseLangTag(x.Id)
                self.__WSLCIDCache[langTag] = x.Handle
            # Recursive:
            return self.WSHandle(languageTag)
        except KeyError:
            return None
                
    def GetDefaultVernacularWS(self):
        """
        Returns the Default Vernacular Writing System: (Language-tag, Name)
        """
        return (self.lp.DefaultVernacularWritingSystem.Id,
                self.lp.DefaultVernacularWritingSystem.DisplayLabel)
    
    def GetDefaultAnalysisWS(self):
        """
        Returns the Default Analysis Writing System: (Language-tag, Name)
        """
        return (self.lp.DefaultAnalysisWritingSystem.Id,
                self.lp.DefaultAnalysisWritingSystem.DisplayLabel)

    # --- Global: other information ---
    
    def GetDateLastModified(self):
        return self.lp.DateModified
    
    def GetPartsOfSpeech(self):
        """
        Returns a list of the Parts of Speech defined in this
        database.
        """
        pos = self.lp.AllPartsOfSpeech
        
        return map (lambda (x) : x.ToString(), pos)

    def GetAllSemanticDomains(self, flat=False):
        """
        Returns a nested or flat list of all Semantic Domains defined
        in this database. The list is ordered.
        
        Return items are objects with properties/methods:
            - Hvo         - ID (value not the same across databases)
            - Guid        - Global Unique ID (same across all databases)
            - ToString()  - String representation of the semantic domain.
        """

        # Recursively extract the semantic domains
        return list(self.UnpackNestedPossibilityList(
                        self.lp.SemanticDomainListOA.PossibilitiesOS,
                        flat))


    # --- Global utility functions ---
    
    def BuildGotoURL(self, objectOrGuid):
        """
        Builds a URL that can be used with os.startfile() to jump to the
        object in Fieldworkds. Currently supports:
        - Lexical Entries
        - Reversal Entries
        - Wordforms
        """

        if isinstance(objectOrGuid, System.Guid):
            guidString = unicode(objectOrGuid)
            objRepository = self.db.ServiceLocator.GetInstance(ICmObjectRepository)
            object = objRepository.GetObject(objectOrGuid)

        else:
             try:
                guidString = unicode(objectOrGuid.Guid)
                object = objectOrGuid
             except:
                raise TypeError("objectOrGuid is neither System.Guid or an object with attribute Guid")

        if object.ClassID == ReversalIndexEntryTags.kClassId:
            tool = u"reversalToolEditComplete"

        elif object.ClassID in (WfiWordformTags.kClassId,
                                WfiAnalysisTags.kClassId,
                                WfiGlossTags.kClassId):
            tool = u"Analyses"

        else:
            tool = u"lexiconEdit"                # Default tool is Lexicon Edit

        return r"%26".join([r"silfw://localhost/link?app%3dflex",
                            r"database%3d" + self.db.ProjectId.UiName.replace(" ", "+"),
                            r"tool%3d" + tool,
                            r"guid%3d" + guidString,])


    # --- Generic Repository Access ---

    def ObjectCountFor(self, repository):
        """
        Returns the number of objects in the given repository.
        repository is specified by the interface class, such as:
        
            - ITextRepository
            - ILexEntryRepository

        (All repository names can be viewed by opening a project in
        FDOBrowser, which can be launched via the Help menu.)
        """
        
        repo = self.db.ServiceLocator.GetInstance(repository)
        return repo.Count
    
    def ObjectsIn(self, repository):
        """
        Returns an iterator over all the objects in the given repository.
        repository is specified by the interface class, such as:
        
            - ITextRepository
            - ILexEntryRepository
            
        (All repository names can be viewed by opening a project in
        FDOBrowser, which can be launched via the Help menu.)
        
        """

        repo = self.db.ServiceLocator.GetInstance(repository)
        return iter(repo.AllInstances())
        
    # --- Lexicon ---

    def LexiconNumberOfEntries(self):
        return self.ObjectCountFor(ILexEntryRepository)
        
    def LexiconAllEntries(self):
        """
        Returns an iterator over all entries in the lexicon.
        
        Each entry is of type:
          SIL.FieldWorks.FDO.ILexEntry, which contains:
              - HomographNumber :: integer
              - HomographForm :: string
              - LexemeFormOA ::  SIL.FieldWorks.FDO.Ling.MoForm
                   - Form :: SIL.FieldWorks.FDO.MultiUnicodeAccessor
                      - GetAlternative : Get String for given WS type
                      - SetAlternative : Set string for given WS type
              - SensesOS :: Ordered collection of SIL.FieldWorks.FDO.Ling.LexSense 
                  - Gloss :: SIL.FieldWorks.FDO.MultiUnicodeAccessor
                  - Definition :: SIL.FieldWorks.FDO.MultiStringAccessor
                  - SenseNumber :: string
                  - ExamplesOS :: Ordered collection of LexExampleSentence
                      - Example :: MultiStringAccessor
        """
        
        return self.ObjectsIn(ILexEntryRepository)


    #  (Writing system utilities)
    
    def __WSHandle(self, languageTagOrHandle, defaultWS):
        if languageTagOrHandle == None:
            handle = defaultWS
        else:
            #print "Specified ws =", languageTagOrHandle
            if isinstance(languageTagOrHandle, (str, unicode)):
                handle = self.WSHandle(languageTagOrHandle)
            else:
                handle = languageTagOrHandle
        if not handle:
            raise FDA_WritingSystemError(languageTagOrHandle)
        return handle

    def __WSHandleVernacular(self, languageTagOrHandle):
        return self.__WSHandle(languageTagOrHandle,
                               self.db.DefaultVernWs)

    def __WSHandleAnalysis(self, languageTagOrHandle):
        return self.__WSHandle(languageTagOrHandle,
                               self.db.DefaultAnalWs)
    
    def __NormaliseLangTag(self, languageTag):
        return languageTag.replace("-", "_").lower()
    
    #  (Vernacular WS fields)
    
    def LexiconGetHeadword(self, entry):
        """
        Returns the headword for the entry
        """
        return entry.ReferenceName

    def LexiconGetLexemeForm(self, entry, languageTagOrHandle=None):
        """
        Returns the lexeme form for the entry in the Default Vernacular WS
        or other WS as specified by languageTagOrHandle.
        """
        WSHandle = self.__WSHandleVernacular(languageTagOrHandle)

        # MultiUnicodeAccessor
        form = ITsString(entry.LexemeFormOA.Form.get_String(WSHandle)).Text
        if form == None: return u""
        else: return form            

    def LexiconGetCitationForm(self, entry, languageTagOrHandle=None):
        """
        Returns the citation form for the entry in the Default Vernacular WS
        or other WS as specified by languageTagOrHandle.
        """
        WSHandle = self.__WSHandleVernacular(languageTagOrHandle)

        # MultiUnicodeAccessor
        form = ITsString(entry.CitationForm.get_String(WSHandle)).Text
        if form == None: return u""
        else: return form

    def LexiconGetPublishInCount(self, entry):
        """
        Returns the PublishIn Count
        """
        return entry.PublishIn.Count

    def LexiconGetPronunciation(self, pronunciation, languageTagOrHandle=None):
        """
        Returns the Form for the Pronunciation in the Default Vernacular WS
        or other WS as specified by languageTagOrHandle.
        """
        WSHandle = self.__WSHandleVernacular(languageTagOrHandle)

        # MultiUnicodeAccessor
        form = ITsString(pronunciation.Form.get_String(WSHandle)).Text
        if form == None: return u""
        else: return form

    def LexiconGetExample(self, example, languageTagOrHandle=None):
        """
        Returns the example text in the Default Vernacular WS or
        other WS as specified by languageTagOrHandle.
        Note: Analysis language translations of example sentences are
        stored as a collection (list). E.g.: 
            for translation in example.TranslationsOC:
                print DB.LexiconGetExampleTranslation(translation)
        """
        WSHandle = self.__WSHandleVernacular(languageTagOrHandle)
        
        # Example is a MultiString
        ex = ITsString(example.Example.get_String(WSHandle)).Text
        if ex == None: return u""
        else: return ex

    def LexiconSetExample(self, example, newString, languageTagOrHandle=None):
        """
        Set the Default Vernacular string for the given Example:
        
            - newString must be unicode.
            - languageTagOrHandle specifies a different writing system.

        NOTE: using this function will lose any formatting that might
        have been present in the example string.
        """

        if not self.writeEnabled: raise FDA_ReadOnlyError
        if not example: raise ValueError

        WSHandle = self.__WSHandleVernacular(languageTagOrHandle)

        # Example is a MultiString
        example.Example.set_String(WSHandle, newString)
        return

    def LexiconGetExampleTranslation(self, translation, languageTagOrHandle=None):
        """
        Returns the translation of an example in the Default Analysis WS or
        other WS as specified by languageTagOrHandle.
        """
        WSHandle = self.__WSHandleAnalysis(languageTagOrHandle)
        
        # Translation is a MultiString
        tr = ITsString(translation.Translation.get_String(WSHandle)).Text
        if tr == None: return u""
        else: return tr

    
    #  (Analysis WS fields)

    def LexiconGetSenseGloss(self, sense, languageTagOrHandle=None):
        """
        Returns the gloss for the sense in the Default Analysis WS or
        other WS as specified by languageTagOrHandle.
        """
        WSHandle = self.__WSHandleAnalysis(languageTagOrHandle)
        
        # MultiUnicodeAccessor
        gloss = ITsString(sense.Gloss.get_String(WSHandle)).Text
        if gloss == None: return u""
        else: return gloss

        
    def LexiconSetSenseGloss(self, sense, gloss, languageTagOrHandle=None):
        """
        Set the Default Analysis gloss for the given sense:
        
            - gloss must be unicode.
            - languageTagOrHandle specifies a different writing system.
        """

        if not self.writeEnabled: raise FDA_ReadOnlyError

        WSHandle = self.__WSHandleAnalysis(languageTagOrHandle)
        
        # MultiUnicodeAccessor
        # set_String handles building a tss for us.
        sense.Gloss.set_String(WSHandle, gloss)
        return
    
    def LexiconGetSenseDefinition(self, sense, languageTagOrHandle=None):
        """
        Returns the definition for the sense in the Default Analysis WS or
        other WS as specified by languageTagOrHandle.
        """
        WSHandle = self.__WSHandleAnalysis(languageTagOrHandle)
        
        # Definition is a MultiString
        defn = ITsString(sense.Definition.get_String(WSHandle)).Text
        if defn == None: return u""
        else: return defn

    #  (Non-string types)
    
    def LexiconGetSensePOS(self, sense):
        """
        Returns the part of speech abbreviation for the sense.
        """
        if sense.MorphoSyntaxAnalysisRA <> None:
            return sense.MorphoSyntaxAnalysisRA.InterlinearAbbr
        else:
            return ""

    def LexiconGetSenseSemanticDomains(self, sense):
        """
        Returns a list of Semantic Domain objects belonging to the sense.
        ToString() and Hvo are available.
        """

        ## SemanticDomainsRC::
        ##      Count
        ##      Add(Hvo)
        ##      Contains(Hvo)
        ##      Remove(Hvo)
        ##      RemoveAll()
        
        return list(sense.SemanticDomainsRC)

    def LexiconEntryAnalysesCount(self, entry):
        # This is replicated from LexEntry.EntryAnalysesCount (v8.0.10)
        # JohnT: You could call it by reflection (it's actually a public method which any
        # instance of ILexEntry will implement; but it's not part of the interface ILexEntry,
        # and you can't cast to LexEntry outside the FDO assembly because LexEntry is internal).
        # Assuming you have a reference to PalasoUIWindowsForms and are using ReflectionHelper,
        # you should be able to get it with
        # (int)ReflectionHelper.GetProperty(someILexEntry, "EntryAnalysesCount").
        """
        Returns a count of the occurences of the entry in the text corpus.
        Note: as of Fieldworks 8.0.10 this calculation can be slightly off (the same analysis
        in the same text segment is only counted once), but is the same as reported in 
        Fieldworks in the Number of Analyses column. See LT-13997.
        """
        count = 0
        forms = list()
        if entry.LexemeFormOA:
            forms.append(entry.LexemeFormOA)
        for mfo in entry.AlternateFormsOS:
            forms.append(mfo)
        for mfo in forms:
            for cmo in mfo.ReferringObjects:
                if self.db.ClassIsOrInheritsFrom(cmo.ClassID,
                                                 WfiMorphBundleTags.kClassId):
                    c = IWfiAnalysis(cmo.Owner).OccurrencesInTexts.Count
                    #report.Info(u"   %s = %i" % (ITsString(IWfiAnalysis(cmo.Owner).ChooserNameTS).Text, c))
                    count += c
        return count

    # --- Lexicon: field functions ---

    def GetCustomFieldValue(self, senseOrEntryOrHvo, flid):
        """
        Returns the field value for String, MultiString and Integer fields.
        Returns None for other field types.
        """

        if not senseOrEntryOrHvo: raise ValueError

        try:
            hvo = senseOrEntryOrHvo.Hvo
        except AttributeError:
            hvo = senseOrEntryOrHvo
            
        # Adapted from XDumper.cs::GetCustomFieldValue
        mdc = self.db.MetaDataCacheAccessor
        cellarPropertyType = mdc.GetFieldType(flid)

        if cellarPropertyType in FLExFDO.CellarStringTypes:
            return ITsString(self.db.DomainDataByFlid.\
                             get_StringProp(hvo, flid))
        elif cellarPropertyType in FLExFDO.CellarUnicodeTypes:
            mua = self.db.DomainDataByFlid.get_MultiStringProp(hvo, flid)
            return ITsString(mua.BestAnalysisVernacularAlternative)

        elif cellarPropertyType == CellarPropertyType.Integer:
            return self.db.DomainDataByFlid.get_IntProp(hvo, flid)
            
        return None

    def LexiconFieldIsStringType(self, fieldID):
        """
        Returns True if the given field is a string type suitable for use
        with LexiconAddTagToField(), otherwise returns False.
        """
        mdc = self.db.MetaDataCacheAccessor
        cellarPropertyType = mdc.GetFieldType(fieldID)
        return cellarPropertyType in FLExFDO.CellarStringTypes

    def LexiconGetFieldText(self, senseOrEntryOrHvo, fieldID):
        """
        Return the text value for the given entry/sense and field (ID).
        Provided for use with custom fields.
        """
        if not fieldID: raise ValueError
        if not senseOrEntryOrHvo: raise ValueError

        value = self.GetCustomFieldValue(senseOrEntryOrHvo, fieldID)

        if value and value.Text <> u"***":
            return value.Text
        else:
            return u""
        
    def LexiconSetFieldText(self, senseOrEntryOrHvo, fieldID, text, languageTagOrHandle=None):
        """
        Set the text value for the given entry/sense and field (ID).
        NOTE: writes the string in one writing system only (defaults
        to the default analysis WS.)
        Provided for use with custom fields.
        """

        if not self.writeEnabled: raise FDA_ReadOnlyError()

        if not fieldID: raise ValueError
        if not senseOrEntryOrHvo: raise ValueError
        
        WSHandle = self.__WSHandleAnalysis(languageTagOrHandle)

        try:
            hvo = senseOrEntryOrHvo.Hvo
        except AttributeError:
            hvo = senseOrEntryOrHvo

        mdc = self.db.MetaDataCacheAccessor
        if mdc.GetFieldType(fieldID) <> CellarPropertyType.String:
            raise RuntimeError("LexiconSetFieldText: field is not String type")

        tss = self.db.TsStrFactory.MakeString(text, WSHandle)

        try:
            self.db.DomainDataByFlid.SetString(hvo, fieldID, tss)
        except FDOInvalidFieldException, msg:
            raise FDA_DatabaseError("FDOInvalidFieldException: Trying to write in read-only mode?")
            

    def LexiconSetFieldInteger(self, senseOrEntryOrHvo, fieldID, integer):
        """
        Set the integer value for the given entry/sense and field (ID).
        Provided for use with custom fields.
        """

        if not self.writeEnabled: raise FDA_ReadOnlyError()

        if not fieldID: raise ValueError
        if not senseOrEntryOrHvo: raise ValueError
        
        try:
            hvo = senseOrEntryOrHvo.Hvo
        except AttributeError:
            hvo = senseOrEntryOrHvo

        mdc = self.db.MetaDataCacheAccessor
        if mdc.GetFieldType(fieldID) <> CellarPropertyType.Integer:
            raise RuntimeError("LexiconSetFieldInteger: field is not Integer type")

        if self.db.DomainDataByFlid.get_IntProp(hvo, fieldID) <> integer:
            try:
                self.db.DomainDataByFlid.SetInt(hvo, fieldID, integer)
            except FDOInvalidFieldException, msg:
                raise FDA_DatabaseError("FDOInvalidFieldException: Trying to write in read-only mode?")


    def LexiconAddTagToField(self, senseOrEntryOrHvo, fieldID, tag):
        """
        Appends the tag string to the end of the given field in the
        sense or entry inserting a semicolon between tags.
        If the tag is already in the field then it isn't added.
        """
        if not fieldID: return

        s = self.LexiconGetFieldText(senseOrEntryOrHvo, fieldID)
                
        if s:
            if tag in s: return
            newText = "; ".join((s, tag))
        else:
            newText = tag

        self.LexiconSetFieldText(senseOrEntryOrHvo,
                                 fieldID,
                                 newText)

        return
    

    # --- Lexicon: Custom fields ---
    
    def __GetCustomFieldsOfType(self, classID):
        """
        Generator for finding all the custom fields at Sense or Entry level.
        Returns tuples of (flid, label)
        """

        # The MetaDataCache defines the database structure: we can
        # find the custom fields in here.
        mdc = self.db.MetaDataCacheAccessor
        for flid in mdc.GetFields(classID, False, -1):
            if self.db.GetIsCustomField(flid):
                yield ((flid, mdc.GetFieldLabel(flid)))

    def __FindCustomField(self, classID, fieldName):
        for flid, name in self.__GetCustomFieldsOfType(classID):
            if name == fieldName:
                return flid
        return None

    def LexiconGetEntryCustomFields(self):
        """
        Returns a list of the custom fields defined at Entry level.
        Each item in the list is a tuple of (flid, label)
        """
        return list(self.__GetCustomFieldsOfType(LexEntryTags.kClassId))

    def LexiconGetSenseCustomFields(self):
        """
        Returns a list of the custom fields defined at Sense level.
        Each item in the list is a tuple of (flid, label)
        """
        return list(self.__GetCustomFieldsOfType(LexSenseTags.kClassId))

    def LexiconGetEntryCustomFieldNamed(self, fieldName):
        """
        Return the entry-level field (its ID) given its name.
        NOTE: fieldName is case-sensitive.
        """
        return self.__FindCustomField(LexEntryTags.kClassId, fieldName)

    def LexiconGetSenseCustomFieldNamed(self, fieldName):
        """
        Return the sense-level field (its ID) given its name.
        NOTE: fieldName is case-sensitive.
        """
        return self.__FindCustomField(LexSenseTags.kClassId, fieldName)

        
    # --- Reversal Indices ---

    def ReversalIndex(self, languageTag):
        """
        Returns the ReversalIndex that matches the given languageTag string
        (eg 'en'). Returns None if there is no reversal index for
        that writing system.
        """
        languageTag = self.__NormaliseLangTag(languageTag)
        
        for ri in self.lexDB.ReversalIndexesOC:
            #print ri.WritingSystem
            if self.__NormaliseLangTag(ri.WritingSystem) == languageTag:
                return ri

        return None

    def ReversalEntries(self, languageTag):
        """
        Returns an iterator for the reversal entries for the given language
        tag (eg 'en'). Returns None if there is no reversal index for
        that writing system.
        """
        ri = self.ReversalIndex(languageTag)
        if ri:
            return iter(ri.EntriesOC)
        else:
            return None

    def ReversalGetForm(self, entry, languageTagOrHandle=None):
        """
        Returns the citation form for the reversal entry in the Default
        Vernacular WS or other WS as specified by languageTagOrHandle.
        """
        WSHandle = self.__WSHandleAnalysis(languageTagOrHandle)
        
        form = ITsString(entry.ReversalForm.get_String(WSHandle)).Text
        if form == None: return u""
        else: return form

    def ReversalSetForm(self, entry, form, languageTagOrHandle=None):
        """
        Set the Default Analysis reversal form for the given reversal entry:
        
            - form must be unicode.
            - languageTagOrHandle can be used to specify a different writing system.
        """

        if not self.writeEnabled: raise FDA_ReadOnlyError

        WSHandle = self.__WSHandleAnalysis(languageTagOrHandle)
        
        # ReversalForm is a MultiUnicodeAccessor
        # set_String handles building a tss for us.
        entry.ReversalForm.set_String(WSHandle, form)
        return
    
    # --- Texts ---

    def TextsGetAll(self, supplyName=True, supplyText=True):
        """
        A Generator that returns tuples of (Name, Text) where:
        
            - Name is the best vernacular or analysis name.
            - Text is a string with newlines separating paragraphs.
            
        Passing supplyName/Text=False returns only the texts or names.
        """
        
        if not supplyText:
            for t in self.ObjectsIn(ITextRepository):
                yield ITsString(t.Name.BestVernacularAnalysisAlternative).Text
        else:
            for t in self.ObjectsIn(ITextRepository):
                content = []
                if t.ContentsOA:
                    for p in t.ContentsOA.ParagraphsOS:
                        if ITsString(p.Contents).Text:
                            content.append(ITsString(p.Contents).Text)
                
                if supplyName:
                    name = ITsString(t.Name.BestVernacularAnalysisAlternative).Text
                    yield name, u"\n".join(content)        
                else:                
                    yield u"\n".join(content)        

    # --- ---

if __name__ == '__main__':
    reload(__builtins__)
    help (FLExDBAccess)
    db = FLExDBAccess()
    try:
        db.OpenDatabase("Sena 3")
    except FDA_DLLError:
        print "These DLLs need to be in the same directory as the "
        print "Python .NET executable:"
        print "\tLanguage.dll"
        print "\tFwKernel.dll"
        
    del db
    
