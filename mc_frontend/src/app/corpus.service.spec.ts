import {fakeAsync, flushMicrotasks, TestBed} from '@angular/core/testing';

import {CorpusService} from './corpus.service';
import {IonicStorageModule} from '@ionic/storage';
import {RouterModule} from '@angular/router';
import {TranslateTestingModule} from './translate-testing/translate-testing.module';
import {APP_BASE_HREF} from '@angular/common';
import {HttpClientTestingModule, HttpTestingController} from '@angular/common/http/testing';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import {HelperService} from './helper.service';
import MockMC from './models/mockMC';
import {CaseValue, DependencyValue, ExerciseType, PartOfSpeechValue} from './models/enum';
import {ApplicationState} from './models/applicationState';
import {QueryMC} from './models/queryMC';
import {PhenomenonMapContent} from './models/phenomenonMap';
import {UpdateInfo} from './models/updateInfo';
import configMC from '../configMC';
import {TextData} from './models/textData';
import {CorpusMC} from './models/corpusMC';
import {Author} from './models/author';
import {take} from 'rxjs/operators';
import {TextRange} from './models/textRange';
import Spy = jasmine.Spy;
import {AnnisResponse, NodeMC} from '../../openapi';
import {Phenomenon} from '../../openapi';
import {Subscription} from 'rxjs';

describe('CorpusService', () => {
    let httpClient: HttpClient;
    let httpTestingController: HttpTestingController;
    let corpusService: CorpusService;
    let helperService: HelperService;
    beforeEach(async () => {
        TestBed.configureTestingModule({
            imports: [
                HttpClientTestingModule,
                IonicStorageModule.forRoot(),
                RouterModule.forRoot([]),
                TranslateTestingModule,
            ],
            providers: [
                {provide: APP_BASE_HREF, useValue: '/'},
                HelperService,
            ],
        });
        httpClient = TestBed.inject(HttpClient);
        httpTestingController = TestBed.inject(HttpTestingController);
        corpusService = TestBed.inject(CorpusService);
        helperService = TestBed.inject(HelperService);
    });

    it('should be created', () => {
        expect(corpusService).toBeTruthy();
    });

    it('should adjust translations', (done) => {
        spyOn(helperService, 'makeGetRequest').and.returnValue(Promise.resolve(MockMC.apiResponseFrequencyAnalysisGet));
        spyOn(corpusService, 'getSortedQueryValues').and.returnValue([PartOfSpeechValue.adjective.toString()]);
        helperService.applicationState.next(helperService.deepCopy(MockMC.applicationState) as ApplicationState);
        corpusService.exercise.type = ExerciseType.matching;
        corpusService.annisResponse = {frequency_analysis: []};
        corpusService.adjustTranslations().then(() => {
            expect(corpusService.exercise.queryItems.length).toBe(2);
            corpusService.exercise.type = ExerciseType.cloze;
            corpusService.adjustTranslations().then(() => {
                expect(corpusService.exercise.queryItems.length).toBe(1);
                done();
            });
        });
    });

    it('should check for an existing ANNIS response', (done) => {
        helperService.applicationState.error(0);
        corpusService.checkAnnisResponse().then(() => {
        }, () => {
            expect(corpusService.annisResponse).toBeFalsy();
            helperService.applicationState.next(new ApplicationState());
            corpusService.checkAnnisResponse().then(() => {
            }, () => {
                expect(corpusService.annisResponse).toBeFalsy();
                helperService.applicationState.next(helperService.deepCopy(MockMC.applicationState) as ApplicationState);
                corpusService.checkAnnisResponse().then(() => {
                    expect(corpusService.annisResponse).toBeTruthy();
                    corpusService.checkAnnisResponse().then(() => {
                        expect(corpusService.annisResponse).toBeTruthy();
                        done();
                    }, () => {
                    });
                }, () => {
                });
            });
        });
    });

    it('should check for updates', (done) => {
        const updateInfoSpy: Spy = spyOn(corpusService.storage, 'get').withArgs(configMC.localStorageKeyUpdateInfo)
            .and.returnValue(Promise.resolve(JSON.stringify(null)));
        const getCorporaSpy: Spy = spyOn(corpusService, 'getCorpora').and.callFake(() => Promise.reject());
        corpusService.checkForUpdates().then(() => {
        }, () => {
            expect(getCorporaSpy).toHaveBeenCalledTimes(1);
            expect(corpusService.availableCorpora).toBeFalsy();
            updateInfoSpy.and.returnValue(Promise.resolve(JSON.stringify(new UpdateInfo({corpora: 0}))));
            getCorporaSpy.and.returnValue(Promise.resolve());
            corpusService.checkForUpdates().then(() => {
                expect(getCorporaSpy).toHaveBeenCalledTimes(2);
                expect(corpusService.availableCorpora).toBeFalsy();
                done();
            });
        });
    });

    it('should get corpora', (done) => {
        corpusService.availableCorpora = [];
        const requestSpy: Spy = spyOn(helperService, 'makeGetRequest').and.returnValue(Promise.resolve(null));
        const localStorageSpy: Spy = spyOn(corpusService, 'loadCorporaFromLocalStorage').and.returnValue(Promise.resolve());
        spyOn(corpusService.storage, 'get').withArgs(configMC.localStorageKeyUpdateInfo).and.returnValue(
            Promise.resolve(JSON.stringify(new UpdateInfo())));
        corpusService.getCorpora().then(() => {
            expect(localStorageSpy).toHaveBeenCalledTimes(1);
            expect(corpusService.availableCorpora.length).toBe(0);
            requestSpy.and.callFake(() => Promise.reject());
            corpusService.getCorpora().then(() => {
            }, () => {
                expect(localStorageSpy).toHaveBeenCalledTimes(2);
                expect(corpusService.availableCorpora.length).toBe(0);
                requestSpy.and.returnValue(Promise.resolve(MockMC.apiResponseCorporaGet));
                corpusService.getCorpora().then(() => {
                    expect(corpusService.availableCorpora.length).toBe(1);
                    done();
                });
            });
        });
    });

    it('should get CTS text passage', (done) => {
        const spy: Spy = spyOn(helperService, 'makeGetRequest').and.returnValue(Promise.reject(
            new HttpErrorResponse({status: 500})));
        corpusService.getCTStextPassage('').then(() => {
        }, (error: HttpErrorResponse) => {
            expect(error.status).toBe(500);
            spy.and.returnValue(Promise.resolve(
                (helperService.deepCopy(MockMC.applicationState) as ApplicationState).mostRecentSetup.annisResponse));
            corpusService.getCTStextPassage('').then((ar: AnnisResponse) => {
                expect(ar.graph_data.nodes.length).toBe(1);
                done();
            });
        });
    });

    it('should get CTS valid reff', (done) => {
        const spy: Spy = spyOn(helperService, 'makeGetRequest').and.returnValue(Promise.reject(1));
        corpusService.getCTSvalidReff('').then(() => {
        }, (error: number) => {
            expect(error).toBe(1);
            spy.and.returnValue(Promise.resolve(['']));
            corpusService.getCTSvalidReff('').then((reff: string[]) => {
                expect(reff.length).toBe(1);
                done();
            });
        });
    });

    it('should get a frequency analysis', (done) => {
        const spy: Spy = spyOn(helperService, 'makeGetRequest').and.callFake(() => Promise.reject());
        corpusService.annisResponse = {frequency_analysis: []};
        corpusService.getFrequencyAnalysis().then(() => {
        }, () => {
            expect(spy).toHaveBeenCalledTimes(1);
            spy.and.returnValue(Promise.resolve(MockMC.apiResponseFrequencyAnalysisGet));
            corpusService.getFrequencyAnalysis().then(() => {
                expect(spy).toHaveBeenCalledTimes(2);
                corpusService.getFrequencyAnalysis().then(() => {
                    expect(corpusService.annisResponse.frequency_analysis.length).toBe(1);
                    done();
                });
            });
        });
    });

    it('should get sorted query values', () => {
        corpusService.exercise.type = ExerciseType.cloze;
        const query: QueryMC = new QueryMC({phenomenon: Phenomenon.Upostag});
        let result: string[] = corpusService.getSortedQueryValues(query, 0);
        expect(result.length).toBe(0);
        const pmc: PhenomenonMapContent = corpusService.phenomenonMap[query.phenomenon];
        pmc.specificValues = {a: 0, b: 1, c: 2};
        pmc.translationValues = {a: 'a', b: 'c', c: 'b'};
        result = corpusService.getSortedQueryValues(query, 0);
        expect(result.length).toBe(3);
        corpusService.exercise.type = ExerciseType.matching;
        corpusService.annisResponse = {
            frequency_analysis: [{
                values: [PartOfSpeechValue.adjective.toString(), 'a'],
                phenomena: [Phenomenon.Upostag, Phenomenon.Upostag]
            }, {
                values: [PartOfSpeechValue.adjective.toString(), 'b'],
                phenomena: [Phenomenon.Upostag, Phenomenon.Upostag]
            }, {
                values: [PartOfSpeechValue.adjective.toString(), 'c'],
                phenomena: [Phenomenon.Upostag, Phenomenon.Upostag]
            }]
        };
        result = corpusService.getSortedQueryValues(query, 1);
        expect(result.length).toBe(3);
        corpusService.annisResponse.frequency_analysis.forEach(fi => fi.phenomena = [Phenomenon.Upostag]);
        corpusService.annisResponse.frequency_analysis[0].values[0] = 'a';
        corpusService.annisResponse.frequency_analysis[1].values[0] = 'b';
        corpusService.annisResponse.frequency_analysis[2].values[0] = 'c';
        result = corpusService.getSortedQueryValues(query, 0);
        expect(result.length).toBe(3);
    });

    it('should get text', (done) => {
        helperService.isVocabularyCheck = true;
        corpusService.getText().then(() => {
            expect(corpusService.currentText).toBeFalsy();
            helperService.isVocabularyCheck = false;
            const spy: Spy = spyOn(corpusService, 'getCTStextPassage').and.callFake(() => Promise.reject());
            corpusService.getText().then(() => {
            }, () => {
                expect(corpusService.currentText).toBeFalsy();
                spy.and.returnValue(Promise.resolve(MockMC.apiResponseTextGet));
                helperService.applicationState.next(helperService.deepCopy(MockMC.applicationState) as ApplicationState);
                corpusService.getText().then(() => {
                    expect(corpusService.currentText).toBeTruthy();
                    done();
                });
            });
        });
    });

    it('should initialize the corpus service', (done) => {
        const restoreSpy: Spy = spyOn(corpusService, 'restoreLastCorpus').and.returnValue(Promise.resolve());
        const updateInfoSpy: Spy = spyOn(corpusService, 'initUpdateInfo').and.callFake(() => Promise.reject());
        helperService.applicationState.next(helperService.deepCopy(MockMC.applicationState) as ApplicationState);
        corpusService.initCorpusService().then(() => {
        }, () => {
            corpusService.translate.onLangChange.next();
            expect(restoreSpy).toHaveBeenCalledTimes(0);
            updateInfoSpy.and.returnValue(Promise.resolve());
            const getCorporaSpy: Spy = spyOn(corpusService, 'getCorpora').and.returnValue(Promise.resolve());
            corpusService.initCorpusService().then(() => {
                expect(getCorporaSpy).toHaveBeenCalledTimes(1);
                expect(restoreSpy).toHaveBeenCalledTimes(1);
                done();
            });
        });
    });

    it('should initialize the current corpus', fakeAsync(() => {
        helperService.applicationState.next(new ApplicationState());
        let corpus: CorpusMC = {source_urn: ''};
        const subscriptions: Subscription[] = [];

        function initCorpus(): void {
            subscriptions.forEach((sub: Subscription, idx: number, subList: Subscription[]) => {
                sub.unsubscribe();
                delete subList[idx];
            });
            corpusService.initCurrentCorpus().then(() => {
                subscriptions.push(corpusService.currentCorpus.subscribe((cc: CorpusMC) => {
                    corpus = cc;
                }));
            });
            flushMicrotasks();
        }

        initCorpus();
        expect(corpus.source_urn).toBeFalsy();
        helperService.applicationState.next(helperService.deepCopy(MockMC.applicationState) as ApplicationState);
        initCorpus();
        expect(corpus.source_urn).toBeTruthy();
        corpus = undefined;
        initCorpus();
        expect(corpus).toBeTruthy();
    }));

    it('should initialize the update information', (done) => {
        const updateInfoSpy: Spy = spyOn(corpusService.storage, 'get').withArgs(configMC.localStorageKeyUpdateInfo);
        updateInfoSpy.and.returnValue(Promise.resolve(''));
        corpusService.initUpdateInfo().then(() => {
            updateInfoSpy.and.callThrough();
            corpusService.storage.get(configMC.localStorageKeyUpdateInfo).then((jsonString: string) => {
                expect(jsonString).toBeTruthy();
                const setSpy: Spy = spyOn(corpusService.storage, 'set').and.returnValue(Promise.resolve());
                corpusService.initUpdateInfo().then(() => {
                    expect(setSpy).toHaveBeenCalledTimes(0);
                    done();
                });
            });
        });
    });

    it('should load corpora from local storage', (done) => {
        corpusService.availableCorpora = [];
        spyOn(corpusService.storage, 'get').withArgs(configMC.localStorageKeyCorpora).and.returnValue(
            Promise.resolve(JSON.stringify([{source_urn: 'urn'}])));
        corpusService.loadCorporaFromLocalStorage().then(() => {
            expect(corpusService.availableCorpora.length).toBe(1);
            done();
        });
    });

    it('should process an ANNIS response', () => {
        const ar: AnnisResponse = {
            graph_data: {
                links: [{annis_component_type: 'Pointing', udep_deprel: 'nsubj'}],
                nodes: [{annis_tok: 'tok .'}]
            }
        };
        corpusService.processAnnisResponse(ar);
        expect(corpusService.phenomenonMap.dependency.specificValues[DependencyValue.subject]).toBe(1);
        ar.graph_data.links.push(ar.graph_data.links[0]);
        corpusService.processAnnisResponse(ar);
        expect(corpusService.phenomenonMap.dependency.specificValues[DependencyValue.subject]).toBe(2);
    });

    it('should process corpora', () => {
        const corpusList: CorpusMC[] = [
            {author: '', source_urn: 'proiel'},
            {author: 'b', source_urn: 'b', title: 't1'},
            {author: 'b', source_urn: 'b', title: 't1'},
            {author: 'b', source_urn: 'c', title: 't3'},
            {author: 'b', source_urn: 'e', title: 't2'},
            {author: 'a', source_urn: 'd'},
        ];
        corpusService.availableAuthors = [new Author({name: ' PROIEL', corpora: []})];
        corpusService.processCorpora(corpusList);
        expect(corpusList[0].author.length).toBeGreaterThan(0);
        expect(corpusService.availableAuthors[0].corpora.length).toBe(1);
    });

    it('should process nodes', () => {
        const node: NodeMC = {
            udep_lemma: 'lemma',
            udep_upostag: 'NOUN',
            udep_feats: `${Phenomenon.Feats}=Nom`
        };
        const ar: AnnisResponse = {graph_data: {nodes: [node, {...node}], links: []}};
        corpusService.phenomenonMap.lemma = new PhenomenonMapContent({specificValues: {}, translationValues: {}});
        corpusService.phenomenonMap.feats = new PhenomenonMapContent({specificValues: {}, translationValues: {}});
        corpusService.phenomenonMap.upostag = new PhenomenonMapContent({
            specificValues: {},
            translationValues: {}
        });
        corpusService.processNodes(ar);
        expect(corpusService.phenomenonMap.lemma.specificValues[node.udep_lemma]).toBe(2);
        expect(corpusService.phenomenonMap.feats.specificValues[CaseValue.nominative]).toBe(2);
        expect(corpusService.phenomenonMap.upostag.specificValues[PartOfSpeechValue.noun]).toBe(2);
    });

    it('should restore the last corpus', (done) => {
        helperService.applicationState.next(new ApplicationState({mostRecentSetup: new TextData()}));
        corpusService.currentText = '';
        const getTextSpy: Spy = spyOn(corpusService, 'getText').and.callFake(() => Promise.reject());
        corpusService.restoreLastCorpus().then(() => {
        }, () => {
            expect(getTextSpy).toHaveBeenCalledTimes(1);
            getTextSpy.and.returnValue(Promise.resolve());
            helperService.applicationState.next(new ApplicationState({
                mostRecentSetup: new TextData({
                    annisResponse: {graph_data: {nodes: [], links: []}}
                })
            }));
            corpusService.restoreLastCorpus().then(() => {
                expect(getTextSpy).toHaveBeenCalledTimes(2);
                corpusService.currentText = 'text';
                corpusService.restoreLastCorpus().then(() => {
                    expect(getTextSpy).toHaveBeenCalledTimes(2);
                    helperService.applicationState.next(helperService.deepCopy(MockMC.applicationState) as ApplicationState);
                    corpusService.restoreLastCorpus().then(() => {
                        expect(corpusService.annisResponse.graph_data.nodes.length).toBe(1);
                        done();
                    });
                });
            });
        });
    });

    it('should save a new corpus', (done) => {
        corpusService.initCurrentTextRange();
        corpusService.initCurrentCorpus().then(() => {
            corpusService.setCurrentCorpus({source_urn: ''});
            corpusService.currentCorpus.pipe(take(1)).subscribe((corpus: CorpusMC) => {
                expect(corpus).toBeTruthy();
                done();
            });
        });
    });

    it('should set the current text range', () => {
        corpusService.initCurrentTextRange();
        const input: HTMLInputElement = document.createElement('input');
        input.setAttribute('id', 'input1');
        input.setAttribute('value', '1');
        document.querySelector('body').appendChild(input);
        corpusService.setCurrentTextRange(1);
        corpusService.setCurrentTextRange(4, '2');
        corpusService.currentTextRange.pipe(take(1)).subscribe((tr: TextRange) => {
            expect(tr.start[0]).toBe('1');
            expect(tr.end[0]).toBe('2');
        });
    });

    it('should update the base word', () => {
        const adjustSpy: Spy = spyOn(corpusService, 'adjustQueryValue');
        const queryValuesSpy: Spy = spyOn(corpusService, 'getSortedQueryValues').and.returnValue([]);
        corpusService.annisResponse = {
            frequency_analysis: helperService.deepCopy(MockMC.apiResponseFrequencyAnalysisGet)
        };
        corpusService.annisResponse.frequency_analysis[0].phenomena.push(Phenomenon.Feats);
        corpusService.exercise.type = ExerciseType.matching;
        corpusService.exercise.queryItems.push(new QueryMC());
        corpusService.updateBaseWord(new QueryMC(), 0);
        expect(adjustSpy).toHaveBeenCalledTimes(1);
        expect(queryValuesSpy).toHaveBeenCalledTimes(1);
        expect(corpusService.exercise.queryItems[1].phenomenon).toBe(Phenomenon.Feats);
    });
});
