#
#   _Exporters.py
#
#   Defines Export_Publication(), which exports one set of headwords
#   from a publication.
#
#   Craig Farrow
#   July 2024
#

#----------------------------------------------------------------
def Export_Publication(project, report, pubName):

    report.Info(f"Exporting all headwords in '{pubName}'...")

    headwordsFile = f"{project.ProjectName()}_{pubName}.txt"

    pubType = project.PublicationType(pubName)
    if not pubType:
        report.Error(f"{pubName} isn't in the list of publications for this project:")
        report.Info("   " + ", ".join(project.GetPublications()))
        return

    headwords = []
    for e in project.LexiconAllEntries():       
        if pubType in e.PublishIn:
            headword = project.LexiconGetHeadword(e)
            headwords.append(headword)

    with open(headwordsFile, mode="w", encoding="utf-8") as output:
        for headword in sorted(headwords, key=lambda s: s.lower()):
            output.write(headword + '\n')

    report.Info(f"Exported {len(headwords)} headwords to file {headwordsFile}",
                report.FileURL(headwordsFile))
