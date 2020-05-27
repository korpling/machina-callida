export enum CaseValue {
    nominative = 'nominative' as any,
    genitive = 'genitive' as any,
    dative = 'dative' as any,
    accusative = 'accusative' as any,
    ablative = 'ablative' as any,
    vocative = 'vocative' as any,
    locative = 'locative' as any,
}

export enum CaseTranslations {
    nominative = 'CASE_NOMINATIVE' as any,
    genitive = 'CASE_GENITIVE' as any,
    dative = 'CASE_DATIVE' as any,
    accusative = 'CASE_ACCUSATIVE' as any,
    ablative = 'CASE_ABLATIVE' as any,
    vocative = 'CASE_VOCATIVE' as any,
    locative = 'CASE_LOCATIVE' as any,
}

export enum CitationLevel {
    default = 'default' as any
}

export enum DependencyValue {
    adjectivalClause = 'adjectivalClause' as any,
    adjectivalModifier = 'adjectivalModifier' as any,
    adverbialClauseModifier = 'adverbialClauseModifier' as any,
    adverbialModifier = 'adverbialModifier' as any,
    appositionalModifier = 'appositionalModifier' as any,
    auxiliary = 'auxiliary' as any,
    caseMarking = 'caseMarking' as any,
    classifier = 'classifier' as any,
    clausalComplement = 'clausalComplement' as any,
    conjunct = 'conjunct' as any,
    coordinatingConjunction = 'coordinatingConjunction' as any,
    copula = 'copula' as any,
    determiner = 'determiner' as any,
    discourseElement = 'discourseElement' as any,
    dislocated = 'dislocated' as any,
    expletive = 'expletive' as any,
    goesWith = 'goesWith' as any,
    list = 'list' as any,
    marker = 'marker' as any,
    multiwordExpression = 'multiwordExpression' as any,
    nominalModifier = 'nominalModifier' as any,
    numericModifier = 'numericModifier' as any,
    object = 'object' as any,
    oblique = 'oblique' as any,
    orphan = 'orphan' as any,
    parataxis = 'parataxis' as any,
    root = 'root' as any,
    punctuation = 'punctuation' as any,
    subject = 'subject' as any,
    vocative = 'vocative' as any,
}

export enum DependencyTranslation {
    adjectivalClause = 'DEPENDENCY_ADJECTIVAL_CLAUSE' as any,
    adjectivalModifier = 'DEPENDENCY_ADJECTIVAL_MODIFIER' as any,
    adverbialClauseModifier = 'DEPENDENCY_ADVERBIAL_CLAUSE_MODIFIER' as any,
    adverbialModifier = 'DEPENDENCY_ADVERBIAL_MODIFIER' as any,
    appositionalModifier = 'DEPENDENCY_APPOSITIONAL_MODIFIER' as any,
    auxiliary = 'DEPENDENCY_AUXILIARY' as any,
    caseMarking = 'DEPENDENCY_CASE_MARKING' as any,
    classifier = 'DEPENDENCY_CLASSIFIER' as any,
    clausalComplement = 'DEPENDENCY_CLAUSAL_COMPLEMENT' as any,
    conjunct = 'DEPENDENCY_CONJUNCT' as any,
    coordinatingConjunction = 'DEPENDENCY_COORDINATING_CONJUNCTION' as any,
    copula = 'DEPENDENCY_COPULA' as any,
    determiner = 'DEPENDENCY_DETERMINER' as any,
    discourseElement = 'DEPENDENCY_DISCOURSE_ELEMENT' as any,
    dislocated = 'DEPENDENCY_DISLOCATED' as any,
    expletive = 'DEPENDENCY_EXPLETIVE' as any,
    goesWith = 'DEPENDENCY_GOES_WITH' as any,
    list = 'DEPENDENCY_LIST' as any,
    marker = 'DEPENDENCY_MARKER' as any,
    multiwordExpression = 'DEPENDENCY_MULTIWORD_EXPRESSION' as any,
    nominalModifier = 'DEPENDENCY_NOMINAL_MODIFIER' as any,
    numericModifier = 'DEPENDENCY_NUMERIC_MODIFIER' as any,
    object = 'DEPENDENCY_OBJECT' as any,
    oblique = 'DEPENDENCY_OBLIQUE_NOMINAL' as any,
    orphan = 'DEPENDENCY_ORPHAN' as any,
    parataxis = 'DEPENDENCY_PARATAXIS' as any,
    punctuation = 'DEPENDENCY_PUNCTUATION' as any,
    root = 'DEPENDENCY_ROOT' as any,
    subject = 'DEPENDENCY_SUBJECT' as any,
    vocative = 'DEPENDENCY_VOCATIVE' as any,
}

export enum ExerciseType {
    cloze = 'cloze' as any,
    kwic = 'kwic' as any,
    markWords = 'markWords' as any,
    matching = 'matching' as any,
}

export enum ExerciseTypeTranslation {
    cloze = 'EXERCISE_TYPE_CLOZE' as any,
    kwic = 'EXERCISE_TYPE_KWIC' as any,
    markWords = 'EXERCISE_TYPE_MARK_WORDS' as any,
    matching = 'EXERCISE_TYPE_MATCHING' as any,
}

export enum FileType {
    docx = 'docx' as any,
    pdf = 'pdf' as any,
    xml = 'xml' as any,
}

export enum InstructionsTranslation {
    cloze = 'INSTRUCTIONS_CLOZE' as any,
    kwic = 'INSTRUCTIONS_KWIC' as any,
    markWords = 'INSTRUCTIONS_MARK_WORDS' as any,
    matching = 'INSTRUCTIONS_MATCHING' as any,
}

export enum MoodleExerciseType {
    cloze = 'ddwtos' as any,
    kwic = 'kwic' as any,
    markWords = 'markWords' as any,
    matching = 'matching' as any,
}

export enum PartOfSpeechValue {
    adjective = 'adjective' as any,
    adverb = 'adverb' as any,
    auxiliary = 'auxiliary' as any,
    conjunction = 'conjunction' as any,
    interjection = 'interjection' as any,
    noun = 'noun' as any,
    numeral = 'numeral' as any,
    other = 'other' as any,
    particle = 'particle' as any,
    preposition = 'preposition' as any,
    pronoun = 'pronoun' as any,
    properNoun = 'properNoun' as any,
    punctuation = 'punctuation' as any,
    symbol = 'symbol' as any,
    verb = 'verb' as any,
}

export enum PartOfSpeechTranslation {
    adjective = 'PART_OF_SPEECH_ADJECTIVE' as any,
    adverb = 'PART_OF_SPEECH_ADVERB' as any,
    auxiliary = 'PART_OF_SPEECH_AUXILIARY' as any,
    interjection = 'PART_OF_SPEECH_INTERJECTION' as any,
    conjunction = 'PART_OF_SPEECH_CONJUNCTION' as any,
    noun = 'PART_OF_SPEECH_NOUN' as any,
    numeral = 'PART_OF_SPEECH_NUMERAL' as any,
    other = 'PART_OF_SPEECH_OTHER' as any,
    particle = 'PART_OF_SPEECH_PARTICLE' as any,
    preposition = 'PART_OF_SPEECH_PREPOSITION' as any,
    pronoun = 'PART_OF_SPEECH_PRONOUN' as any,
    properNoun = 'PART_OF_SPEECH_PROPER_NOUN' as any,
    punctuation = 'PART_OF_SPEECH_PUNCTUATION' as any,
    symbol = 'PART_OF_SPEECH_SYMBOL' as any,
    verb = 'PART_OF_SPEECH_VERB' as any,
}

export enum PhenomenonTranslation {
    dependency = 'PHENOMENON_DEPENDENCY' as any,
    feats = 'PHENOMENON_CASE' as any,
    lemma = 'PHENOMENON_LEMMA' as any,
    upostag = 'PHENOMENON_PART_OF_SPEECH' as any,
}

export enum SortingCategory {
    authorAsc = 'SORTING_CATEGORY_AUTHOR_ASCENDING' as any,
    authorDesc = 'SORTING_CATEGORY_AUTHOR_DESCENDING' as any,
    dateAsc = 'SORTING_CATEGORY_DATE_ASCENDING' as any,
    dateDesc = 'SORTING_CATEGORY_DATE_DESCENDING' as any,
    complexityAsc = 'SORTING_CATEGORY_TEXT_COMPLEXITY_ASCENDING' as any,
    complexityDesc = 'SORTING_CATEGORY_TEXT_COMPLEXITY_DESCENDING' as any,
    typeAsc = 'SORTING_CATEGORY_TYPE_ASCENDING' as any,
    typeDesc = 'SORTING_CATEGORY_TYPE_DESCENDING' as any,
    vocAsc = 'SORTING_CATEGORY_VOCABULARY_ASCENDING' as any,
    vocDesc = 'SORTING_CATEGORY_VOCABULARY_DESCENDING' as any,
}

export enum TestModuleState {
    inProgress = 'inProgress' as any,
    showResults = 'showResults' as any,
    showSolutions = 'showSolutions' as any,
}

export enum TestType {
    cloze = 'cloze' as any,
    list = 'list' as any,
}

export enum VocabularyCorpus {
    agldt = 'agldt' as any,
    bws = 'bws' as any,
    proiel = 'proiel' as any,
    viva = 'viva' as any,
}

export enum VocabularyCorpusTranslation {
    agldt = 'VOCABULARY_REFERENCE_CORPUS_AGLDT' as any,
    bws = 'VOCABULARY_REFERENCE_CORPUS_BWS' as any,
    proiel = 'VOCABULARY_REFERENCE_PROIEL' as any,
    viva = 'VOCABULARY_REFERENCE_CORPUS_VIVA' as any,
}
