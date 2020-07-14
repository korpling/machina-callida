import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {TextRangePage} from './text-range.page';
import {HttpClientModule} from '@angular/common/http';
import {IonicStorageModule} from '@ionic/storage';
import {RouterModule} from '@angular/router';
import {TranslateTestingModule} from '../translate-testing/translate-testing.module';
import {FormsModule} from '@angular/forms';
import {APP_BASE_HREF} from '@angular/common';
import {CorpusMC} from '../models/corpusMC';
import {Citation} from '../models/citation';
import Spy = jasmine.Spy;
import MockMC from '../models/mockMC';
import {take} from 'rxjs/operators';
import {CitationLevel} from '../models/enum';
import {TextRange} from '../models/textRange';
import {ReplaySubject} from 'rxjs';

describe('TextRangePage', () => {
    let textRangePage: TextRangePage;
    let fixture: ComponentFixture<TextRangePage>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [TextRangePage],
            imports: [
                FormsModule,
                HttpClientModule,
                IonicStorageModule.forRoot(),
                RouterModule.forRoot([]),
                TranslateTestingModule,
            ],
            providers: [
                {provide: APP_BASE_HREF, useValue: '/'},
            ],
            schemas: [CUSTOM_ELEMENTS_SCHEMA],
        }).compileComponents().then();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(TextRangePage);
        textRangePage = fixture.componentInstance;
        textRangePage.corpusService.currentCorpus = new ReplaySubject<CorpusMC>(1);
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(textRangePage).toBeTruthy();
    });

    it('should add level 3 references', (done) => {
        const addReferencesSpy: Spy = spyOn(textRangePage, 'addReferences').and.returnValue(Promise.resolve());
        textRangePage.addLevel3References([], {source_urn: ''}).then(() => {
            expect(addReferencesSpy).toHaveBeenCalledTimes(0);
            textRangePage.currentInputId = 2;
            const corpus: CorpusMC = {
                source_urn: '',
                citations: {1: new Citation({subcitations: {2: new Citation({subcitations: {3: new Citation()}})}})}
            };
            textRangePage.addLevel3References(['1', '2'], corpus).then(() => {
                expect(addReferencesSpy).toHaveBeenCalledTimes(0);
                corpus.citations['1'].subcitations['2'].subcitations = {};
                textRangePage.addLevel3References(['1', '2'], corpus).then(() => {
                    expect(addReferencesSpy).toHaveBeenCalledTimes(1);
                    done();
                });
            });
        });
    });

    it('should add missing citations', (done) => {
        function expectCitationLength(expectedLength: number) {
            expect(textRangePage.citationValuesStart.length).toBe(expectedLength);
            expect(textRangePage.citationValuesEnd.length).toBe(expectedLength);
        }

        function resetCitationValues(): void {
            textRangePage.citationValuesStart = [];
            textRangePage.citationValuesEnd = [];
        }

        textRangePage.corpusService.currentCorpus = new ReplaySubject<CorpusMC>(1);
        textRangePage.corpusService.currentCorpus.next({citations: {4: new Citation()}, source_urn: ''});
        resetCitationValues();
        const citationLabels: string[] = ['1'];
        textRangePage.addMissingCitations(citationLabels, citationLabels).then(() => {
            expectCitationLength(1);
            citationLabels.push('b');
            resetCitationValues();
            textRangePage.addMissingCitations(citationLabels, citationLabels).then(() => {
            }, () => {
                expectCitationLength(1);
                citationLabels[1] = '2';
                resetCitationValues();
                textRangePage.addMissingCitations(citationLabels, citationLabels).then(() => {
                    expectCitationLength(2);
                    citationLabels.push('3');
                    resetCitationValues();
                    textRangePage.addMissingCitations(citationLabels, citationLabels).then(() => {
                        expectCitationLength(3);
                        done();
                    });
                });
            });
        });
    });

    it('should add references', (done) => {
        const corpus: CorpusMC = {citations: {0: new Citation({subcitations: {}, label: ''})}, source_urn: ''};
        textRangePage.corpusService.currentCorpus = new ReplaySubject<CorpusMC>(1);
        textRangePage.corpusService.currentCorpus.next(corpus);
        const validReffSpy: Spy = spyOn(textRangePage.corpusService, 'getCTSvalidReff').and.callFake(() => Promise.reject());
        textRangePage.addReferences('', [null]).then(() => {
            expect(Object.keys(corpus.citations).length).toBe(1);
            textRangePage.addReferences('', [new Citation()]).then(() => {
            }, async () => {
                expect(Object.keys(corpus.citations).length).toBe(1);
                validReffSpy.and.returnValue(Promise.resolve(['1']));
                const citations: Citation[] = [new Citation({isNumeric: true, value: 0, label: '0'})];
                await textRangePage.addReferences('', citations);
                expect(corpus.citations['0'].subcitations['1'].label).toBe('1');
                validReffSpy.and.returnValue(Promise.resolve(['a']));
                await textRangePage.addReferences('', []);
                expect(corpus.citations.a.label).toBe('a');
                citations.push(new Citation({label: '1'}));
                await textRangePage.addReferences('', citations);
                expect(textRangePage.currentlyAvailableCitations.slice(-1)[0]).toBe('.1.a');
                done();
            });
        });
    });

    it('should apply autocomplete', (done) => {
        spyOn(textRangePage, 'showFurtherReferences').and.returnValue(Promise.resolve());
        textRangePage.currentInputId = 1;
        const input: HTMLInputElement = document.createElement('input');
        input.setAttribute('id', 'input2');
        document.body.appendChild(input);
        textRangePage.applyAutoComplete(true).then(() => {
            expect(document.activeElement).toBe(input);
            input.parentNode.removeChild(input);
            done();
        });
    });

    it('should check whether input is disabled', (done) => {
        textRangePage.corpusService.initCurrentTextRange();
        textRangePage.helperService.applicationState.next(textRangePage.helperService.deepCopy(MockMC.applicationState));
        textRangePage.corpusService.currentCorpus = new ReplaySubject<CorpusMC>(1);
        textRangePage.corpusService.currentCorpus.next({citations: {4: new Citation()}, source_urn: ''});
        textRangePage.checkInputDisabled().then(() => {
            textRangePage.isInputDisabled[0].pipe(take(1)).subscribe((isDisabled: boolean) => {
                expect(isDisabled).toBe(true);
                textRangePage.corpusService.currentCorpus.next({
                    source_urn: '',
                    citations: {1: new Citation({subcitations: {2: new Citation()}})}
                });
                textRangePage.checkInputDisabled().then(() => {
                    textRangePage.isInputDisabled[0].pipe(take(1)).subscribe((isDisabled2: boolean) => {
                        expect(isDisabled2).toBe(false);
                        done();
                    });
                });
            });
        });
    });

    it('should check the text range', (done) => {
        function expectRangeCheckResult(start: string[], end: string[], expectedResult: boolean): Promise<void> {
            return new Promise<void>(resolve => textRangePage.checkTextRange(start, end).then((result: boolean) => {
                expect(result).toBe(expectedResult);
                return resolve();
            }));
        }

        const corpus: CorpusMC = {
            source_urn: '',
            citations: {4: new Citation()},
            citation_level_2: CitationLevel.default.toString(),
            citation_level_3: CitationLevel.default.toString(),
        };
        textRangePage.corpusService.currentCorpus = new ReplaySubject<CorpusMC>(1);
        textRangePage.corpusService.currentCorpus.next(corpus);
        const citationLabels: string[] = ['1', '2', '3'];
        expectRangeCheckResult(citationLabels.slice(0, 1), [], false).then(() => {
            corpus.citation_level_2 = '';
            expectRangeCheckResult(citationLabels.slice(0, 2), [], false).then(() => {
                expectRangeCheckResult(citationLabels.slice(0, 2), citationLabels, false).then(() => {
                    corpus.citation_level_3 = '';
                    expectRangeCheckResult(citationLabels, citationLabels.slice(0, 2), false).then(() => {
                        const addCitSpy: Spy = spyOn(textRangePage, 'addMissingCitations').and.returnValue(Promise.resolve());
                        spyOn(textRangePage, 'compareCitationValues').and.returnValue(Promise.resolve(true));
                        expectRangeCheckResult(citationLabels, citationLabels, true).then(() => {
                            addCitSpy.and.callFake(() => Promise.reject());
                            expectRangeCheckResult(citationLabels, citationLabels, true).then(() => {
                                done();
                            });
                        });
                    });
                });
            });
        });
    });

    it('should compare citation values', (done) => {
        function expectComparisonResult(start: number[], end: number[], expectedResult: boolean): Promise<void> {
            textRangePage.citationValuesStart = start;
            textRangePage.citationValuesEnd = end;
            return new Promise<void>(resolve => textRangePage.compareCitationValues().then((result: boolean) => {
                expect(result).toBe(expectedResult);
                return resolve();
            }));
        }

        expectComparisonResult([0], [1], true).then(() => {
            expectComparisonResult([NaN], [1], true).then(() => {
                expectComparisonResult([2], [1], false).then(() => {
                    expectComparisonResult([1], [1], true).then(() => {
                        expectComparisonResult([1, 0], [1, 1], true).then(() => {
                            expectComparisonResult([1, 2], [1, 1], false).then(() => {
                                expectComparisonResult([1, 1], [1, 1], true).then(() => {
                                    expectComparisonResult([1, 1, 1], [1, 1, 0], false).then(() => {
                                        done();
                                    });
                                });
                            });
                        });
                    });
                });
            });
        });
    });

    it('should confirm the selection', (done) => {
        function expectNavigationCalled(spy: Spy, times: number = 1, skipText: boolean = false): Promise<void> {
            return new Promise<void>(resolve => {
                textRangePage.confirmSelection(skipText).then(() => {
                    expect(spy).toHaveBeenCalledTimes(times);
                    return resolve();
                });
            });
        }

        textRangePage.isTextRangeCheckRunning = true;
        textRangePage.citationValuesStart = [NaN];
        textRangePage.citationValuesEnd = [];
        const checkSpy: Spy = spyOn(textRangePage, 'checkTextRange').and.returnValue(Promise.resolve(false));
        expectNavigationCalled(checkSpy, 0).then(async () => {
            textRangePage.isTextRangeCheckRunning = false;
            textRangePage.corpusService.currentCorpus = new ReplaySubject<CorpusMC>(1);
            textRangePage.corpusService.currentCorpus.next({
                source_urn: '',
                citations: {4: new Citation()},
                citation_level_2: CitationLevel.default.toString()
            });
            textRangePage.corpusService.initCurrentTextRange();
            textRangePage.helperService.applicationState.next(textRangePage.helperService.deepCopy(MockMC.applicationState));
            const getTextSpy: Spy = spyOn(textRangePage.corpusService, 'getText').and.callFake(() => Promise.reject());
            await expectNavigationCalled(getTextSpy, 0);
            checkSpy.and.returnValue(Promise.resolve(true));
            const showTextSpy: Spy = spyOn(textRangePage.helperService, 'goToShowTextPage').and.returnValue(Promise.resolve(true));
            await expectNavigationCalled(showTextSpy, 0);
            getTextSpy.and.returnValue(Promise.resolve());
            await expectNavigationCalled(showTextSpy);
            textRangePage.helperService.isVocabularyCheck = true;
            const goToSpy: Spy = spyOn(textRangePage.helperService, 'goToPage')
                .and.returnValue(Promise.resolve(true));
            await expectNavigationCalled(goToSpy);
            textRangePage.citationValuesStart = [];
            await expectNavigationCalled(goToSpy, 2, true);
            done();
        });
    });

    it('should initialize the page', (done) => {
        textRangePage.corpusService.initCurrentTextRange();
        textRangePage.helperService.applicationState.next(textRangePage.helperService.deepCopy(MockMC.applicationState));
        textRangePage.initPage({
            source_urn: '', citation_level_2: CitationLevel.default.toString(),
            citations: {1: new Citation({label: '1'})}
        }).then(() => {
            textRangePage.corpusService.currentTextRange.pipe(take(1)).subscribe((tr: TextRange) => {
                expect(tr.start[0]).toBe('1');
                done();
            });
        });
    });

    it('should map citation labels', (done) => {
        function expectValueList(label: string, index: number, citLabels: string[], values: number[],
                                 expectedValue: number, targetIndex: number, isLength: boolean = false): Promise<void> {
            return new Promise<void>(resolve => {
                textRangePage.mapCitationLabelsToValues(label, index, citLabels, values).finally(() => {
                    expect(isLength ? values.length : values[targetIndex]).toBe(expectedValue);
                    return resolve();
                });
            });
        }

        const corpus: CorpusMC = {citations: {4: new Citation({subcitations: {}, value: 4})}, source_urn: ''};
        textRangePage.corpusService.currentCorpus = new ReplaySubject<CorpusMC>(1);
        textRangePage.corpusService.currentCorpus.next(corpus);
        const valueList: number[] = [];
        const citationLabels: string[] = ['4'];
        let idx = 0;
        const addReferencesSpy: Spy = spyOn(textRangePage, 'addReferences').and.returnValue(Promise.resolve());
        expectValueList('4', idx, [], valueList, 4, 0).then(async () => {
            addReferencesSpy.and.callFake(() => Promise.reject());
            idx++;
            await expectValueList('2', idx, citationLabels, valueList, 1, 0, true);
            addReferencesSpy.and.callFake(() => {
                return new Promise<void>(resolve => {
                    corpus.citations['4'].subcitations['2'] = new Citation({value: 2});
                    return resolve();
                });
            });
            await expectValueList('2', idx, citationLabels, valueList, 2, 1);
            await expectValueList('2', idx, citationLabels, valueList, 2, 2);
            corpus.citations['4'].subcitations = {};
            citationLabels.push('2');
            idx++;
            await expectValueList('0', idx, citationLabels, valueList, 3, 0, true);
            corpus.citations['4'].subcitations['2'] = new Citation({subcitations: {}});
            addReferencesSpy.and.callFake(() => Promise.reject());
            await expectValueList('3', idx, citationLabels, valueList, 3, 0, true);
            addReferencesSpy.and.callFake(() => {
                return new Promise<void>(resolve => {
                    corpus.citations['4'].subcitations['2'].subcitations['3'] = new Citation({value: 3});
                    return resolve();
                });
            });
            await expectValueList('3', idx, citationLabels, valueList, 3, 3);
            await expectValueList('3', idx, citationLabels, valueList, 5, 0, true);
            corpus.citations['4'].subcitations['2'].subcitations = {0: new Citation()};
            await expectValueList('3', idx, citationLabels, valueList, 5, 0, true);
            done();
        });
    });

    it('should be initialized', (done) => {
        const addReferencesSpy: Spy = spyOn(textRangePage, 'addReferences').and.callFake(() => Promise.reject());
        const initPageSpy: Spy = spyOn(textRangePage, 'initPage').and.returnValue(Promise.resolve());
        textRangePage.corpusService.currentCorpus = new ReplaySubject<CorpusMC>(1);
        textRangePage.corpusService.currentCorpus.next({citations: {}, source_urn: ''});
        textRangePage.ngOnInit().then(async () => {
            expect(initPageSpy).toHaveBeenCalledTimes(0);
            addReferencesSpy.and.returnValue(Promise.resolve());
            await textRangePage.ngOnInit();
            expect(initPageSpy).toHaveBeenCalledTimes(1);
            textRangePage.corpusService.currentCorpus.next({citations: {1: new Citation()}, source_urn: ''});
            await textRangePage.ngOnInit();
            expect(initPageSpy).toHaveBeenCalledTimes(2);
            done();
        });
    });

    it('should reset citations', (done) => {
        function expectTextRange(currentInputId: number, tr: TextRange, isStart: boolean, idx: number,
                                 expectedValue: string): Promise<void> {
            return new Promise<void>(resolve => {
                textRangePage.currentInputId = currentInputId;
                textRangePage.resetCitations().then(() => {
                    const target: string[] = isStart ? tr.start : tr.end;
                    expect(target[idx]).toBe(expectedValue);
                    return resolve();
                });
            });
        }

        textRangePage.corpusService.initCurrentTextRange();
        textRangePage.helperService.applicationState.next(textRangePage.helperService.deepCopy(MockMC.applicationState));
        textRangePage.corpusService.currentCorpus = new ReplaySubject<CorpusMC>(1);
        textRangePage.corpusService.currentCorpus.next({citations: {1: new Citation()}, source_urn: ''});
        textRangePage.resetCitations().then(() => {
            textRangePage.corpusService.currentTextRange.pipe(take(1)).subscribe((tr: TextRange) => {
                expect(tr.start[1]).toBeTruthy();
                expectTextRange(1, tr, true, 1, '').then(() => {
                    tr.start[2] = '2';
                    expectTextRange(2, tr, true, 2, '').then(() => {
                        expectTextRange(4, tr, false, 2, '').then(() => {
                            tr.end[2] = '2';
                            expectTextRange(5, tr, false, 2, '').then(() => {
                                done();
                            });
                        });
                    });
                });
            });
        });
    });

    it('should reset the current input ID', (done) => {
        textRangePage.currentInputId = 1;
        textRangePage.resetCurrentInputId().then(() => {
            expect(textRangePage.currentInputId).toBe(0);
            done();
        });
    });

    it('should show further references', (done) => {
        const addReferencesSpy: Spy = spyOn(textRangePage, 'addReferences').and.returnValue(Promise.resolve());
        const addLvl3Spy: Spy = spyOn(textRangePage, 'addLevel3References').and.returnValue(Promise.resolve());
        textRangePage.corpusService.initCurrentTextRange();
        textRangePage.helperService.applicationState.next(textRangePage.helperService.deepCopy(MockMC.applicationState));
        textRangePage.corpusService.currentCorpus = new ReplaySubject<CorpusMC>(1);
        textRangePage.corpusService.currentCorpus.next({
            citations: {2: new Citation({subcitations: {2: new Citation()}})}, source_urn: ''
        });
        textRangePage.showFurtherReferences(true).then(async () => {
            expect(addReferencesSpy).toHaveBeenCalledTimes(1);
            textRangePage.corpusService.setCurrentTextRange(0, null, new TextRange({end: [''], start: ['']}));
            await textRangePage.showFurtherReferences(false);
            expect(addLvl3Spy).toHaveBeenCalledTimes(1);
            textRangePage.corpusService.setCurrentTextRange(0, null, new TextRange({end: ['2'], start: ['2']}));
            textRangePage.corpusService.currentCorpus.next({
                citations: {2: new Citation({subcitations: {}})},
                citation_level_2: CitationLevel.default.toString(), source_urn: ''
            });
            await textRangePage.showFurtherReferences(false);
            expect(addReferencesSpy).toHaveBeenCalledTimes(1);
            expect(addLvl3Spy).toHaveBeenCalledTimes(2);
            done();
        });
    });
});
