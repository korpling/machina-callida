/* tslint:disable:no-string-literal object-literal-shorthand */
import {Injectable} from '@angular/core';
import {CorpusMC} from 'src/app/models/corpusMC';
import {Author} from 'src/app/models/author';
import {TextRange} from 'src/app/models/textRange';
import {HttpClient, HttpErrorResponse, HttpParams} from '@angular/common/http';
import {TranslateService} from '@ngx-translate/core';
import {ToastController} from '@ionic/angular';
import {HelperService} from 'src/app/helper.service';
import {AnnisResponse} from 'src/app/models/annisResponse';
import {
    CaseTranslations,
    CaseValue,
    DependencyTranslation,
    DependencyValue,
    ExerciseType,
    ExerciseTypeTranslation,
    InstructionsTranslation,
    PartOfSpeechTranslation,
    PartOfSpeechValue,
    Phenomenon
} from 'src/app/models/enum';
import {NodeMC} from 'src/app/models/nodeMC';
import {LinkMC} from 'src/app/models/linkMC';
import {QueryMC} from 'src/app/models/queryMC';
import {Exercise} from 'src/app/models/exercise';
import {Feedback} from 'src/app/models/feedback';
import {PhenomenonMap, PhenomenonMapContent} from 'src/app/models/phenomenonMap';
import {FrequencyItem} from 'src/app/models/frequencyItem';
import {ReplaySubject} from 'rxjs';
import {ApplicationState} from './models/applicationState';
import {take} from 'rxjs/operators';
import {TextData} from './models/textData';
import {Storage} from '@ionic/storage';
import {UpdateInfo} from './models/updateInfo';
import configMC from '../configMC';

@Injectable({
    providedIn: 'root'
})
export class CorpusService {
    public annisResponse: AnnisResponse;
    public availableCorpora: CorpusMC[];
    public availableAuthors: Author[] = [];
    public baseUrn: string;
    public citationsUnavailableString: string;
    public corporaUnavailableString: string;
    public currentAuthor: Author;
    public currentCorpus: ReplaySubject<CorpusMC>;
    private currentCorpusCache: CorpusMC;
    public currentText = '';
    public currentTextRange: ReplaySubject<TextRange>;
    private currentTextRangeCache: TextRange = new TextRange({start: ['', '', ''], end: ['', '', '']});
    public currentUrn = '';
    public dataAlreadySentMessage: string;
    public dataSentSuccessMessage: string;
    public emptyQueryValueString: string;
    public exercise: Exercise = new Exercise({
        type: ExerciseType.cloze,
        typeTranslation: '',
        queryItems: [new QueryMC({
            phenomenon: Phenomenon.partOfSpeech,
            values: [PartOfSpeechValue.adjective],
        })],
        feedback: new Feedback({general: '', incorrect: '', partiallyCorrect: '', correct: ''}),
        instructionsTranslation: ''
    });
    public invalidQueryCorpusString: string;
    public invalidSentenceCountString: string;
    public invalidTextRangeString: string;
    public isTextRangeCorrect = false;
    public phenomenonMap: PhenomenonMap = new PhenomenonMap({
        case: new PhenomenonMapContent({translationObject: CaseTranslations}),
        dependency: new PhenomenonMapContent({translationObject: DependencyTranslation}),
        lemma: new PhenomenonMapContent({translationObject: null}),
        partOfSpeech: new PhenomenonMapContent({translationObject: PartOfSpeechTranslation})
    });
    public searchRegexMissingString: string;
    public shareLinkCopiedString: string;
    public textTooLongString: string;
    public tooManyHitsString: string;

    constructor(public translate: TranslateService,
                public http: HttpClient,
                public toastCtrl: ToastController,
                public helperService: HelperService,
                public storage: Storage
    ) {
    }

    adjustQueryValue(query: QueryMC, queryIndex: number): void {
        // when the phenomenon changes, choose the first value from the translated list as the default
        query.values = [this.getSortedQueryValues(query, queryIndex)[0]];
        this.updateBaseWord(query, queryIndex);
    }

    adjustTranslations(): Promise<void> {
        return new Promise<void>(resolve => {
            this.translate.get(ExerciseTypeTranslation[this.exercise.type]).subscribe(
                value => this.exercise.typeTranslation = value);
            if ([ExerciseType.cloze, ExerciseType.matching, ExerciseType.markWords].indexOf(this.exercise.type) > -1) {
                this.translate.get(InstructionsTranslation[this.exercise.type]).subscribe(
                    value => this.exercise.instructionsTranslation = value);
            }
            if (this.exercise.type === ExerciseType.matching) {
                this.exercise.queryItems = [new QueryMC({phenomenon: Phenomenon.partOfSpeech, values: []}),
                    new QueryMC({phenomenon: Phenomenon.partOfSpeech, values: []})];
                this.getFrequencyAnalysis().then(() => {
                    this.adjustQueryValue(this.exercise.queryItems[0], 0);
                    this.adjustQueryValue(this.exercise.queryItems[1], 1);
                    return resolve();
                });
            } else if (this.exercise.queryItems.length > 1) {
                this.exercise.queryItems.splice(1, 1);
                return resolve();
            }
        }).finally(() => this.adjustQueryValue(this.exercise.queryItems[0], 0));
    }

    checkAnnisResponse(): Promise<void> {
        return new Promise((resolve, reject) => {
            if (this.annisResponse) {
                return resolve();
            }
            this.helperService.applicationState.pipe(take(1)).subscribe((state: ApplicationState) => {
                if (state.mostRecentSetup) {
                    this.annisResponse = state.mostRecentSetup.annisResponse;
                    this.currentAuthor = state.mostRecentSetup.currentAuthor;
                    this.currentUrn = state.mostRecentSetup.currentUrn;
                    this.currentCorpusCache = state.mostRecentSetup.currentCorpus;
                    return resolve();
                } else {
                    return reject();
                }
            }, () => {
                return reject();
            });
        });
    }

    checkForUpdates(): Promise<void> {
        return new Promise((resolve, reject) => {
            this.storage.get(configMC.localStorageKeyUpdateInfo).then((jsonString: string) => {
                // check local storage for necessary updates
                const updateInfo: UpdateInfo = JSON.parse(jsonString) as UpdateInfo;
                this.getCorpora(updateInfo ? updateInfo.corpora : 0)
                    .then(() => {
                        return resolve();
                    }, () => {
                        return reject();
                    });
            });
        });
    }

    getCorpora(lastUpdateTimeMS: number = 0): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            this.availableCorpora = [];
            this.availableAuthors = [];
            // get corpora from REST API
            const url: string = configMC.backendBaseUrl + configMC.backendApiCorporaPath;
            const params: HttpParams = new HttpParams().set('last_update_time', lastUpdateTimeMS.toString());
            this.helperService.makeGetRequest(this.http, this.toastCtrl, url, params, this.corporaUnavailableString)
                .then((data: object[]) => {
                    if (data) {
                        const corpusList: CorpusMC[] = data as CorpusMC[];
                        this.storage.set(configMC.localStorageKeyCorpora, JSON.stringify(corpusList)).then();
                        this.storage.get(configMC.localStorageKeyUpdateInfo).then((jsonString: string) => {
                            const updateInfo: UpdateInfo = JSON.parse(jsonString) as UpdateInfo;
                            updateInfo.corpora = new Date().getTime();
                            this.storage.set(configMC.localStorageKeyUpdateInfo, JSON.stringify(updateInfo)).then();
                        });
                        this.processCorpora(corpusList);
                        return resolve();
                    } else {
                        this.loadCorporaFromLocalStorage().then(() => {
                            return resolve();
                        });
                    }
                }, async () => {
                    this.loadCorporaFromLocalStorage().then(() => {
                        return reject();
                    });
                });
        });
    }

    getCorpusListFromJSONstring(jsonString: string): CorpusMC[] {
        let jsonObject: object = JSON.parse(jsonString);
        // backwards compatibility
        const corpusProp = 'corpora';
        jsonObject = jsonObject.hasOwnProperty(corpusProp) ? jsonObject[corpusProp] : jsonObject;
        return jsonObject as CorpusMC[];
    }

    getCTStextPassage(urn: string): Promise<AnnisResponse> {
        return new Promise(((resolve, reject) => {
            const url: string = configMC.backendBaseUrl + configMC.backendApiRawtextPath;
            const params: HttpParams = new HttpParams().set('urn', urn);
            this.helperService.makeGetRequest(this.http, this.toastCtrl, url, params).then((ar: AnnisResponse) => {
                return resolve(ar);
            }, (error: HttpErrorResponse) => {
                return reject(error);
            });
        }));
    }

    getCTSvalidReff(urn: string): Promise<string[]> {
        return new Promise((resolve, reject) => {
            const fullUrl: string = configMC.backendBaseUrl + configMC.backendApiValidReffPath;
            const params: HttpParams = new HttpParams().set('urn', urn);
            this.helperService.makeGetRequest(this.http, this.toastCtrl, fullUrl, params).then((reff: string[]) => {
                resolve(reff);
            }, (error: HttpErrorResponse) => {
                reject(error);
            });
        });
    }

    getFrequencyAnalysis(): Promise<void> {
        return new Promise((resolve, reject) => {
            if (this.annisResponse.frequency_analysis.length) {
                return resolve();
            } else {
                const url: string = configMC.backendBaseUrl + configMC.backendApiFrequencyPath;
                const params: HttpParams = new HttpParams().set('urn', this.currentUrn);
                this.helperService.makeGetRequest(this.http, this.toastCtrl, url, params).then((fis: FrequencyItem[]) => {
                    this.annisResponse.frequency_analysis = fis;
                    this.helperService.applicationState.pipe(take(1)).subscribe((state: ApplicationState) => {
                        state.mostRecentSetup.annisResponse = this.annisResponse;
                        this.helperService.saveApplicationState(state).then();
                    });
                    return resolve();
                }, () => {
                    return reject();
                });
            }
        });
    }

    getSortedQueryValues(query: QueryMC, queryIndex: number): string[] {
        const pmc: PhenomenonMapContent = this.phenomenonMap[query.phenomenon];
        if (this.exercise.type === ExerciseType.matching) {
            if (queryIndex) {
                const relevantFIs: FrequencyItem[] = this.annisResponse.frequency_analysis.filter(
                    x => x.values[0] === this.exercise.queryItems[0].values[0] &&
                        x.phenomena[1] === query.phenomenon.toString());
                return Array.from(new Set<string>(relevantFIs.map(x => x.values[1]))).sort((a, b) => {
                    return pmc.translationValues[a] < pmc.translationValues[b] ? -1 : 1;
                });
            } else {
                const relevantFIs: FrequencyItem[] = this.annisResponse.frequency_analysis.filter(
                    x => x.phenomena[0] === query.phenomenon.toString());
                return Array.from(new Set<string>(relevantFIs.map(x => x.values[0]))).sort((a, b) => {
                    return pmc.translationValues[a] < pmc.translationValues[b] ? -1 : 1;
                });
            }
        }
        if (!pmc.specificValues) {
            return [];
        }
        return Object.keys(pmc.specificValues).sort((a, b) => {
            return pmc.translationValues[a] < pmc.translationValues[b] ? -1 : 1;
        });
    }

    getText(saveToCache: boolean = true): Promise<void> {
        return new Promise((resolve, reject) => {
            this.currentText = '';
            if (this.helperService.isVocabularyCheck) {
                return resolve();
            } else {
                this.getCTStextPassage(this.currentUrn).then((ar: AnnisResponse) => {
                    this.processAnnisResponse(ar, saveToCache);
                    return resolve();
                }, async (error: HttpErrorResponse) => {
                    return reject(error);
                });
            }
        });
    }

    getTranslations(): void {
        this.translate.get('ERROR_CORPORA_UNAVAILABLE').subscribe(value => this.corporaUnavailableString = value);
        this.translate.get('EXERCISE_FEEDBACK_CORRECT_DEFAULT').subscribe(value => this.exercise.feedback.correct = value);
        this.translate.get('EXERCISE_FEEDBACK_INCORRECT_DEFAULT').subscribe(value => this.exercise.feedback.incorrect = value);
        this.translate.get('EXERCISE_FEEDBACK_PARTIALLY_CORRECT_DEFAULT').subscribe((value) => {
            this.exercise.feedback.partiallyCorrect = value;
        });
        this.translate.get('EXERCISE_FEEDBACK_GENERAL_DEFAULT').subscribe(value => this.exercise.feedback.general = value);
        this.translate.get(ExerciseTypeTranslation[this.exercise.type]).subscribe(value => this.exercise.typeTranslation = value);
        this.translate.get(InstructionsTranslation[this.exercise.type]).subscribe((value) => {
            this.exercise.instructionsTranslation = value;
        });
        this.translate.get('INVALID_TEXT_RANGE').subscribe(value => this.invalidTextRangeString = value);
        this.translate.get('ERROR_CITATIONS_UNAVAILABLE').subscribe(value => this.citationsUnavailableString = value);
        this.translate.get('LINK_COPIED').subscribe(value => this.shareLinkCopiedString = value);
        this.translate.get('TEXT_TOO_LONG').subscribe(value => this.textTooLongString = value + configMC.maxTextLength);
        this.translate.get('QUERY_VALUE_EMPTY').subscribe(value => this.emptyQueryValueString = value);
        this.translate.get('DATA_SENT').subscribe(value => this.dataSentSuccessMessage = value);
        this.translate.get('DATA_ALREADY_SENT').subscribe(value => this.dataAlreadySentMessage = value);
        this.translate.get('SEARCH_REGEX_MISSING').subscribe(value => this.searchRegexMissingString = value);
        this.translate.get('TOO_MANY_SEARCH_RESULTS').subscribe(value => this.tooManyHitsString = value);
        this.translate.get('INVALID_SENTENCE_COUNT').subscribe(value => this.invalidSentenceCountString = value);
        this.translate.get('INVALID_QUERY_CORPUS').subscribe(value => this.invalidQueryCorpusString = value);
    }

    initCorpusService(): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            this.initCurrentCorpus().then();
            this.initCurrentTextRange();
            this.initUpdateInfo().then(() => {
                this.checkForUpdates().finally(() => {
                    this.checkAnnisResponse().then(() => {
                        this.restoreLastCorpus().then(() => {
                            return resolve();
                        });
                    });
                });
            }, () => {
                return reject();
            });
            this.initPhenomenonMap();
            this.translate.onLangChange.subscribe(() => {
                this.getTranslations();
            });
        });
    }

    initCurrentCorpus(): Promise<void> {
        return new Promise((resolve) => {
            this.currentCorpus = new ReplaySubject<CorpusMC>(1);
            if (!this.currentCorpusCache) {
                this.helperService.applicationState.pipe(take(1)).subscribe((state: ApplicationState) => {
                    const textData: TextData = state.currentSetup ? state.currentSetup : state.mostRecentSetup;
                    this.currentCorpusCache = textData ? textData.currentCorpus : null;
                    if (this.currentCorpusCache) {
                        this.currentCorpus.next(this.currentCorpusCache);
                    }
                    return resolve();
                });
            } else {
                this.currentCorpus.next(this.currentCorpusCache);
                return resolve();
            }
        });
    }

    initCurrentTextRange(): void {
        this.currentTextRange = new ReplaySubject<TextRange>(1);
        this.helperService.applicationState.pipe(take(1)).subscribe((state: ApplicationState) => {
            this.currentTextRangeCache = state.currentSetup.currentTextRange;
            this.currentTextRange.next(this.currentTextRangeCache);
        });
    }

    initPhenomenonMap(): void {
        // map the different phenomena to their respective Enum for processing and display/translation
        Object.keys(Phenomenon).forEach((key) => {
            if (key !== Phenomenon[Phenomenon.lemma]) {
                const pmc: PhenomenonMapContent = this.phenomenonMap[key];
                pmc.translationValues = {};
                const translationObject: object = pmc.translationObject;
                Object.keys(translationObject).forEach((k: string) => {
                    if (k !== k.toUpperCase()) {
                        this.translate.get(translationObject[k]).subscribe(v => pmc.translationValues[k] = v);
                    }
                });
            }
        });
    }

    initUpdateInfo(): Promise<void> {
        return new Promise<void>(resolve => {
            this.storage.get(configMC.localStorageKeyUpdateInfo).then((jsonString: string) => {
                if (jsonString) {
                    return resolve();
                }
                const ui: UpdateInfo = new UpdateInfo({
                    corpora: new Date().getTime(),
                    exerciseList: new Date().getTime()
                });
                this.storage.set(configMC.localStorageKeyUpdateInfo, JSON.stringify(ui)).then(() => {
                    return resolve();
                });
            });
        });
    }

    isTreebank(corpus: CorpusMC): boolean {
        return corpus.source_urn.includes('proiel');
    }

    public loadCorporaFromLocalStorage(): Promise<void> {
        return new Promise<void>(resolve => {
            this.storage.get(configMC.localStorageKeyCorpora).then((jsonString: string) => {
                if (jsonString) {
                    this.processCorpora(this.getCorpusListFromJSONstring(jsonString));
                }
                return resolve();
            });
        });
    }

    processAnnisResponse(ar: AnnisResponse, saveToCache: boolean = true): void {
        Object.keys(this.phenomenonMap).forEach((key: string) => {
            const pmc: PhenomenonMapContent = this.phenomenonMap[key];
            pmc.specificValues = {};
        });
        this.phenomenonMap.lemma.translationValues = {};
        this.processNodes(ar);
        const pointingLinks: LinkMC[] = ar.links.filter(x => x.annis_component_type === 'Pointing');
        pointingLinks.forEach((link: LinkMC) => {
            const dep: DependencyValue = this.helperService.dependencyMap[link.udep_deprel];
            if (dep) {
                const existingValue = this.phenomenonMap.dependency.specificValues[dep];
                this.phenomenonMap.dependency.specificValues[dep] = (existingValue ? existingValue : 0) + 1;
            }
        });
        // need to add root dependencies manually because they are tricky to handle
        const nodeIds: string[] = ar.nodes.map(x => x.id);
        const nodesWithDependencySet: Set<string> = new Set<string>(pointingLinks.map(x => x.target));
        const rootNodeIds: string[] = nodeIds.filter(x => !nodesWithDependencySet.has(x));
        this.phenomenonMap.dependency.specificValues[DependencyValue.root] = rootNodeIds.length;
        this.adjustQueryValue(this.exercise.queryItems[0], 0);
        // remove whitespace before punctuation
        this.currentText = ar.nodes.map(x => x.annis_tok).join(' ').replace(/[ ]([.,\/#!$%\^&\*;:{}=\-_`~()])/g, (x: string) => {
            return x.trim();
        });
        this.annisResponse = ar;
        if (saveToCache) {
            this.helperService.applicationState.pipe(take(1)).subscribe((as: ApplicationState) => {
                as.currentSetup.annisResponse = null;
                as.mostRecentSetup.currentUrn = this.currentUrn;
                as.mostRecentSetup.annisResponse = ar;
                this.helperService.saveApplicationState(as).then(() => {
                    as.currentSetup.currentUrn = this.currentUrn;
                    as.currentSetup.annisResponse = ar;
                });
            });
        }
    }

    processCorpora(corpusList: CorpusMC[]): void {
        this.availableCorpora = [];
        this.availableAuthors = [];
        corpusList.forEach((corpus: CorpusMC) => {
            corpus.citations = {};
            this.availableCorpora.push(corpus);
            if (this.isTreebank(corpus)) {
                corpus.author += ' (PROIEL)';
            }
            const existingAuthor: Author = this.availableAuthors.find(author => author.name === corpus.author);
            if (existingAuthor) {
                existingAuthor.corpora.push(corpus);
            } else {
                this.availableAuthors.push(new Author({
                    name: corpus.author,
                    corpora: [corpus]
                }));
            }
        });
        this.availableAuthors.sort((author1, author2) => {
            if (author1.name < author2.name) {
                return -1;
            } else if (author1.name > author2.name) {
                return 1;
            }
        });
        this.availableAuthors.forEach((author) => {
            author.corpora.sort((corpus1, corpus2) => {
                if (corpus1.title < corpus2.title) {
                    return -1;
                } else if (corpus1.title > corpus2.title) {
                    return 1;
                }
                return 0;
            });
        });
    }

    processNodes(ar: AnnisResponse): void {
        ar.nodes.forEach((node: NodeMC) => {
            let existingValue = this.phenomenonMap.lemma.specificValues[node.udep_lemma];
            this.phenomenonMap.lemma.specificValues[node.udep_lemma] = (existingValue ? existingValue : 0) + 1;
            this.phenomenonMap.lemma.translationValues[node.udep_lemma] = node.udep_lemma;
            if (node.udep_feats) {
                const featsParts: string[] = node.udep_feats.split('|');
                const casePart: string = featsParts.find(x => x.toLowerCase().includes(Phenomenon[Phenomenon.case]));
                if (casePart) {
                    const caseAbbreviation: string = casePart.split('=')[1];
                    const caseValue: CaseValue = this.helperService.caseMap[caseAbbreviation];
                    existingValue = this.phenomenonMap.case.specificValues[caseValue];
                    this.phenomenonMap.case.specificValues[caseValue] = (existingValue ? existingValue : 0) + 1;
                }
            }
            const pos: PartOfSpeechValue = this.helperService.partOfSpeechMap[node.udep_upostag];
            existingValue = this.phenomenonMap.partOfSpeech.specificValues[pos];
            this.phenomenonMap.partOfSpeech.specificValues[pos] = (existingValue ? existingValue : 0) + 1;
        });
    }

    restoreLastCorpus(): Promise<void> {
        return new Promise((resolve, reject) => {
            this.helperService.applicationState.pipe(take(1)).subscribe((state: ApplicationState) => {
                this.annisResponse = state.mostRecentSetup.annisResponse;
                this.currentUrn = state.mostRecentSetup.currentUrn;
                this.currentCorpusCache = state.mostRecentSetup.currentCorpus;
                this.currentTextRangeCache = state.mostRecentSetup.currentTextRange;
                this.isTextRangeCorrect = true;
                if (this.annisResponse && this.annisResponse.nodes.length) {
                    this.processAnnisResponse(this.annisResponse, false);
                    return resolve();
                } else if (this.currentText) {
                    // check if the data is already present
                    return resolve();
                } else {
                    const saveToCache: boolean = !state.mostRecentSetup.annisResponse || !state.mostRecentSetup.annisResponse.nodes.length;
                    this.getText(saveToCache).then(() => {
                        return resolve();
                    }, () => {
                        return reject();
                    });
                }
            });
        });
    }

    setCurrentCorpus(corpus: CorpusMC): void {
        this.currentCorpusCache = corpus;
        this.currentCorpus.next(this.currentCorpusCache);
        this.setCurrentTextRange(-1, null, new TextRange({start: ['', '', ''], end: ['', '', '']}));
        this.helperService.applicationState.pipe(take(1)).subscribe((state: ApplicationState) => {
            state.currentSetup.currentCorpus = corpus;
            this.helperService.applicationState.next(state);
        });
    }

    setCurrentTextRange(inputId: number = -1, newValue: string = null, tr: TextRange = null): void {
        if (tr) {
            this.currentTextRangeCache = tr;
        } else if (inputId >= 0) {
            const isStart: boolean = inputId < 4;
            const targetInputId = `input${inputId}`;
            if (newValue === null) {
                newValue = document.querySelector<HTMLInputElement>(`#${targetInputId}`).value;
            }
            const trIdx: number = inputId - (isStart ? 1 : 4);
            const relevantTextRangePart: string[] = isStart ? this.currentTextRangeCache.start : this.currentTextRangeCache.end;
            relevantTextRangePart[trIdx] = newValue;
        }
        this.currentTextRange.next(this.currentTextRangeCache);
    }

    updateBaseWord(query: QueryMC, queryIndex: number): void {
        if (!this.annisResponse || !this.annisResponse.frequency_analysis || !this.annisResponse.frequency_analysis.length) {
            return;
        }
        if (!queryIndex && this.exercise.type === ExerciseType.matching) {
            if (!this.getSortedQueryValues(this.exercise.queryItems[1], 1).length) {
                const fi: FrequencyItem = this.annisResponse.frequency_analysis.find(
                    x => x.values[0] === this.exercise.queryItems[0].values[0]);
                this.exercise.queryItems[1].phenomenon = Phenomenon[fi.phenomena[1]];
            }
            this.adjustQueryValue(this.exercise.queryItems[1], 1);
        }
    }
}
