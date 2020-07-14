/* tslint:disable:no-string-literal */
import {ApplicationState} from 'src/app/models/applicationState';
import {NavController, ToastController} from '@ionic/angular';
import {Citation} from 'src/app/models/citation';
import {HttpErrorResponse} from '@angular/common/http';
import {Component, OnInit} from '@angular/core';
import {CitationLevel} from 'src/app/models/enum';
import {TranslateService} from '@ngx-translate/core';
import {HelperService} from '../helper.service';
import {CorpusService} from 'src/app/corpus.service';
import {CorpusMC} from '../models/corpusMC';
import {BehaviorSubject} from 'rxjs';
import {take} from 'rxjs/operators';
import {TextRange} from '../models/textRange';
import configMC from '../../configMC';

@Component({
    selector: 'app-text-range',
    templateUrl: './text-range.page.html',
    styleUrls: ['./text-range.page.scss'],
})
export class TextRangePage implements OnInit {
    // TODO: rebuild the system so it works for any corpus of arbitrary citation depth
    public CitationLevel = CitationLevel;
    ObjectKeys = Object.keys;
    public currentlyAvailableCitations: string[] = [];
    public currentInputId = 0;
    public citationValuesStart: number[];
    public citationValuesEnd: number[];
    public isInputDisabled: { [isStart: number]: BehaviorSubject<boolean> } = {
        0: new BehaviorSubject<boolean>(true),
        1: new BehaviorSubject<boolean>(true)
    };
    public isTextRangeCheckRunning = false;

    constructor(public navCtrl: NavController,
                public corpusService: CorpusService,
                public toastCtrl: ToastController,
                public translateService: TranslateService,
                public helperService: HelperService) {
    }

    addLevel3References(relevantTextRangePart: string[], currentCorpus: CorpusMC): Promise<void> {
        return new Promise<void>(resolve => {
            if ([2, 3, 5, 6].indexOf(this.currentInputId) > -1) {
                const baseCit: Citation = currentCorpus.citations[relevantTextRangePart[0]];
                const relCit: Citation = baseCit.subcitations[relevantTextRangePart[1]];
                const hasLvl3: boolean = currentCorpus.citation_level_3 !== CitationLevel[CitationLevel.default];
                if (relevantTextRangePart[1] && !(relCit && Object.keys(relCit.subcitations).length) && hasLvl3) {
                    this.addReferences(currentCorpus.citation_level_3, [baseCit, relCit]).then(() => {
                        return resolve();
                    });
                } else {
                    return resolve();
                }
            } else {
                return resolve();
            }
        });
    }

    addMissingCitations(citationLabelsStart: string[], citationLabelsEnd: string[]): Promise<void> {
        return new Promise((resolve, reject) => {
            this.mapCitationLabelsToValues(citationLabelsStart[0], 0, citationLabelsStart, this.citationValuesStart).then(() => {
                this.mapCitationLabelsToValues(citationLabelsEnd[0], 0, citationLabelsEnd, this.citationValuesEnd).then(() => {
                    if (citationLabelsStart.length > 1) {
                        const cls1: string = citationLabelsStart[1];
                        this.mapCitationLabelsToValues(cls1, 1, citationLabelsStart, this.citationValuesStart).then(() => {
                            this.mapCitationLabelsToValues(citationLabelsEnd[1], 1, citationLabelsEnd, this.citationValuesEnd).then(() => {
                                if (citationLabelsStart.length > 2) {
                                    const cls2: string = citationLabelsStart[2];
                                    this.mapCitationLabelsToValues(cls2, 2, citationLabelsStart, this.citationValuesStart).then(() => {
                                        const cle2: string = citationLabelsEnd[2];
                                        this.mapCitationLabelsToValues(cle2, 2, citationLabelsEnd, this.citationValuesEnd).then(() => {
                                            return resolve();
                                        });
                                    });
                                } else {
                                    return resolve();
                                }
                            });
                        }, () => reject());
                    } else {
                        return resolve();
                    }
                });
            });
        });
    }

    addReferences(targetCitationLevel: string, relevantCitations: Citation[] = []): Promise<void> {
        return new Promise((resolve, reject) => {
            if (relevantCitations.some(x => !x)) {
                return resolve();
            }
            const urnLastPart: string = relevantCitations.map(x => x.isNumeric ? x.value.toString() : x.label).join('.');
            this.corpusService.currentCorpus.pipe(take(1)).subscribe((cc: CorpusMC) => {
                const fullUrn: string = cc.source_urn + (urnLastPart ? ':' + urnLastPart : '');
                this.corpusService.getCTSvalidReff(fullUrn).then((urnList: string[]) => {
                    const newCitations: Citation[] = [];
                    const replaceString: string = fullUrn + (urnLastPart ? '.' : ':');
                    urnList.forEach((urn) => {
                        const urnModified: string = urn.replace(replaceString, '');
                        const isNumeric: boolean = !isNaN(+urnModified);
                        newCitations.push(new Citation({
                            isNumeric,
                            level: targetCitationLevel,
                            label: urnModified,
                            value: (isNumeric ? +urnModified : newCitations.length + 1)
                        }));
                    });
                    newCitations.forEach((citation) => {
                        citation.subcitations = {};
                        if (relevantCitations.length === 0) {
                            cc.citations[citation.label] = citation;
                            this.currentlyAvailableCitations.push(citation.label);
                        } else if (relevantCitations.length === 1) {
                            cc.citations[relevantCitations[0].label].subcitations[citation.label] = citation;
                            const firstLabel: string = cc.citations[relevantCitations[0].label].label;
                            this.currentlyAvailableCitations.push(firstLabel.concat('.', citation.label));
                        } else if (relevantCitations.length === 2) {
                            const rc0Label: string = relevantCitations[0].label;
                            const rc1Label: string = relevantCitations[1].label;
                            cc.citations[rc0Label].subcitations[rc1Label].subcitations[citation.label] = citation;
                            const firstLabel: string = cc.citations[rc0Label].label;
                            const secondLabel: string = cc.citations[rc0Label].subcitations[rc1Label].label;
                            this.currentlyAvailableCitations.push(firstLabel.concat('.', secondLabel, '.', citation.label));
                        }
                    });
                    return resolve();
                }, async (error: HttpErrorResponse) => {
                    return reject(error);
                });
            });
        });
    }

    applyAutoComplete(isStart: boolean): Promise<void> {
        return new Promise<void>(resolve => {
            this.showFurtherReferences(isStart).then(() => {
                const oldId: number = this.currentInputId;
                this.currentInputId = 0;
                let nextIdx = oldId;
                let newEl: HTMLInputElement = null;
                while (nextIdx < Math.min(oldId + 4, 6) && !newEl) {
                    nextIdx++;
                    const newId: string = 'input' + nextIdx.toString();
                    newEl = document.getElementById(newId) as HTMLInputElement;
                }
                if (newEl) {
                    // adjust disabled state manually because the focus won't work otherwise and the automatic check comes too late
                    newEl.disabled = false;
                    newEl.focus();
                }
                return resolve();
            });
        });
    }

    checkInputDisabled(): Promise<void> {
        return new Promise<void>(resolve => {
            this.corpusService.currentCorpus.pipe(take(1)).subscribe((cc: CorpusMC) => {
                this.corpusService.currentTextRange.pipe(take(1)).subscribe((tr: TextRange) => {
                    Object.keys(this.isInputDisabled).forEach((isStart: string) => {
                        const baseCits: { [label: string]: Citation } = cc.citations;
                        const ctrPart: string[] = +isStart ? tr.start : tr.end;
                        if (!baseCits.hasOwnProperty(ctrPart[0])) {
                            this.isInputDisabled[+isStart].next(true);
                        } else {
                            this.isInputDisabled[+isStart].next(!baseCits[ctrPart[0]].subcitations.hasOwnProperty(ctrPart[1]));
                        }
                    });
                    return resolve();
                });
            });
        });
    }

    checkTextRange(citationLabelsStart: string[], citationLabelsEnd: string[]): Promise<boolean> {
        return new Promise(resolve => {
            citationLabelsStart = citationLabelsStart.filter(x => x);
            citationLabelsEnd = citationLabelsEnd.filter(x => x);
            this.corpusService.currentCorpus.pipe(take(1)).subscribe((cc: CorpusMC) => {
                if (cc.citation_level_2 === CitationLevel[CitationLevel.default]) {
                    if (citationLabelsStart.length !== 1 || citationLabelsEnd.length !== 1) {
                        return resolve(false);
                    }
                } else {
                    if (citationLabelsStart.length < 2 || citationLabelsEnd.length < 2) {
                        return resolve(false);
                    } else {
                        if (cc.citation_level_3 === CitationLevel[CitationLevel.default]) {
                            if (citationLabelsStart.length !== 2 || citationLabelsEnd.length !== 2) {
                                return resolve(false);
                            }
                        } else if (citationLabelsStart.length !== 3 || citationLabelsEnd.length !== 3) {
                            return resolve(false);
                        }
                    }
                }
                this.citationValuesEnd = [];
                this.citationValuesStart = [];
                this.addMissingCitations(citationLabelsStart, citationLabelsEnd).then(() => {
                    this.compareCitationValues().then((result: boolean) => resolve(result));
                }, () => {
                    // if the citation system does not work, we allow the user to choose the correct citations on his own
                    return resolve(true);
                });
            });
        });
    }


    compareCitationValues(): Promise<boolean> {
        return new Promise((resolve) => {
            const citationValuesStart: number[] = this.citationValuesStart;
            const citationValuesEnd: number[] = this.citationValuesEnd;
            if (citationValuesStart[0] < citationValuesEnd[0]) {
                return resolve(true);
            } else if (citationValuesStart.concat(citationValuesEnd).some(x => isNaN(x))) {
                // there are non-numeric citation values involved, so we cannot easily compare them
                return resolve(true);
            } else if (citationValuesStart[0] === citationValuesEnd[0]) {
                if (citationValuesStart.length > 1) {
                    if (citationValuesStart[1] < citationValuesEnd[1]) {
                        return resolve(true);
                    } else if (this.citationValuesStart[1] === citationValuesEnd[1]) {
                        if (citationValuesStart.length > 2) {
                            return resolve(citationValuesStart[2] <= citationValuesEnd[2]);
                        } else {
                            return resolve(true);
                        }
                    } else {
                        return resolve(false);
                    }
                } else {
                    return resolve(true);
                }
            } else {
                return resolve(false);
            }
        });
    }

    confirmSelection(skipText: boolean = false): Promise<void> {
        return new Promise<void>((resolve) => {
            if (this.isTextRangeCheckRunning) {
                return resolve();
            }
            this.isTextRangeCheckRunning = true;
            this.corpusService.currentTextRange.pipe(take(1)).subscribe((tr: TextRange) => {
                const citationLabelsStart: string[] = tr.start;
                const citationLabelsEnd: string[] = tr.end;
                this.checkTextRange(citationLabelsStart, citationLabelsEnd).then((isTextRangeCorrect: boolean) => {
                    this.isTextRangeCheckRunning = false;
                    if (!isTextRangeCorrect) {
                        this.helperService.showToast(this.toastCtrl, this.corpusService.invalidTextRangeString).then();
                        return resolve();
                    }
                    this.corpusService.currentCorpus.pipe(take(1)).subscribe((cc: CorpusMC) => {
                        const newUrnBase: string = cc.source_urn + ':';
                        if (this.citationValuesStart.concat(this.citationValuesEnd).some(x => isNaN(x))) {
                            this.corpusService.currentUrn = newUrnBase + tr.start.filter(x => x).join('.') + '-' +
                                tr.end.filter(x => x).join('.');
                        } else {
                            this.corpusService.currentUrn = newUrnBase + this.citationValuesStart.join('.') + '-' +
                                this.citationValuesEnd.join('.');
                        }
                        this.helperService.applicationState.pipe(take(1)).subscribe((state: ApplicationState) => {
                            state.currentSetup.currentTextRange = tr;
                            this.corpusService.isTextRangeCorrect = true;
                            this.corpusService.getText().then(() => {
                                if (skipText) {
                                    this.helperService.goToPage(this.navCtrl, configMC.pageUrlExerciseParameters).then();
                                } else if (this.helperService.isVocabularyCheck) {
                                    this.helperService.goToPage(this.navCtrl, configMC.pageUrlVocabularyCheck).then();
                                } else {
                                    this.helperService.goToShowTextPage(this.navCtrl).then();
                                }
                                return resolve();
                            }, () => {
                                return resolve();
                            });
                        });
                    });
                });
            });
        });
    }

    initPage(currentCorpus: CorpusMC): Promise<void> {
        return new Promise<void>(resolve => {
            if (currentCorpus.citation_level_2 === CitationLevel[CitationLevel.default]) {
                const firstKey: string = Object.keys(currentCorpus.citations)[0];
                const randomLabel: string = currentCorpus.citations[firstKey].label;
                this.corpusService.currentTextRange.pipe(take(1)).subscribe((tr: TextRange) => {
                    tr.start[0] = tr.end[0] = randomLabel;
                    return resolve();
                });
            }
            return resolve();
        });
    }

    public mapCitationLabelsToValues(label: string, index: number, citationLabels: string[], valueList: number[]): Promise<void> {
        return new Promise((resolve, reject) => {
            this.corpusService.currentCorpus.pipe(take(1)).subscribe((cc: CorpusMC) => {
                if (index === 0 && cc.citations[label]) {
                    valueList.push(cc.citations[label].value);
                    return resolve();
                } else if (index === 1) {
                    if (!cc.citations[citationLabels[index - 1]]) {
                        if (!!+label) {
                            valueList.push(+label);
                            return resolve();
                        } else {
                            return reject();
                        }
                    }
                    if (Object.keys(cc.citations[citationLabels[index - 1]].subcitations).length === 0) {
                        const relevantCitations: Citation[] = [cc.citations[citationLabels[index - 1]]];
                        this.addReferences(cc.citation_level_2, relevantCitations).then(() => {
                            valueList.push(cc.citations[citationLabels[index - 1]].subcitations[label].value);
                            return resolve();
                        }, () => {
                            return reject();
                        });
                    } else {
                        valueList.push(cc.citations[citationLabels[index - 1]].subcitations[label].value);
                        return resolve();
                    }
                } else if (index === 2) {
                    if (!cc.citations[citationLabels[index - 2]] ||
                        !cc.citations[citationLabels[index - 2]].subcitations[citationLabels[index - 1]]) {
                        if (!!+label) {
                            valueList.push(+label);
                            return resolve();
                        } else {
                            return reject();
                        }
                    }
                    const citation: Citation = cc.citations[citationLabels[index - 2]];
                    const subCitation: Citation = citation.subcitations[citationLabels[index - 1]];
                    if (Object.keys(subCitation.subcitations).length === 0) {
                        this.addReferences(cc.citation_level_3, [citation, subCitation]).then(() => {
                            valueList.push(subCitation.subcitations[label].value);
                            return resolve();
                        }, () => reject());
                    } else {
                        if (!subCitation.subcitations[label]) {
                            return reject();
                        }
                        valueList.push(subCitation.subcitations[label].value);
                        return resolve();
                    }
                } else if (!!+label) {
                    valueList.push(+label);
                    return resolve();
                }
            });
        });
    }

    ngOnInit(): Promise<void> {
        return new Promise<void>(resolve => {
            this.currentlyAvailableCitations = [];
            this.corpusService.isTextRangeCorrect = false;
            this.corpusService.currentCorpus.pipe(take(1)).subscribe((cc: CorpusMC) => {
                if (Object.keys(cc.citations).length === 0) {
                    this.addReferences(cc.citation_level_1).then(() => {
                        this.initPage(cc).then(() => {
                            return resolve();
                        });
                    }, () => {
                        return resolve();
                    });
                } else {
                    this.initPage(cc).then(() => {
                        return resolve();
                    });
                }
            });
        });
    }

    resetCitations(): Promise<void> {
        return new Promise<void>(resolve => {
            this.corpusService.currentCorpus.pipe(take(1)).subscribe((cc: CorpusMC) => {
                this.corpusService.currentTextRange.pipe(take(1)).subscribe((tr: TextRange) => {
                    switch (this.currentInputId) {
                        case 1:
                            if (cc.citation_level_2 !== CitationLevel[CitationLevel.default]) {
                                tr.start[1] = '';
                                tr.start[2] = '';
                            }
                            break;
                        case 2:
                            if (cc.citation_level_3 !== CitationLevel[CitationLevel.default]) {
                                tr.start[2] = '';
                            }
                            break;
                        case 4:
                            if (cc.citation_level_2 !== CitationLevel[CitationLevel.default]) {
                                tr.end[1] = '';
                                tr.end[2] = '';
                            }
                            break;
                        case 5:
                            if (cc.citation_level_3 !== CitationLevel[CitationLevel.default]) {
                                tr.end[2] = '';
                            }
                            break;
                        default:
                            break;
                    }
                });
                return resolve();
            });
        });
    }

    resetCurrentInputId(): Promise<void> {
        return new Promise<void>(resolve => {
            const oldId: number = this.currentInputId;
            // dirty hack to prevent the blur event from triggering before the click event
            setTimeout(() => {
                if (oldId === this.currentInputId) {
                    this.currentInputId = 0;
                }
                return resolve();
            }, 50);
        });
    }

    showFurtherReferences(isStart: boolean): Promise<void> {
        return new Promise<void>(resolve => {
            this.corpusService.currentTextRange.pipe(take(1)).subscribe((tr: TextRange) => {
                const relTextRangePart: string[] = isStart ? tr.start : tr.end;
                this.resetCitations().then(() => {
                    this.checkInputDisabled().then(() => {
                        if (!relTextRangePart[0]) {
                            return resolve();
                        }
                        this.corpusService.currentCorpus.pipe(take(1)).subscribe((cc: CorpusMC) => {
                            const baseCit: Citation = cc.citations[relTextRangePart[0]];
                            if (baseCit && (Object.keys(baseCit.subcitations).length ||
                                cc.citation_level_2 === CitationLevel[CitationLevel.default])) {
                                this.addLevel3References(relTextRangePart, cc).then(() => {
                                    return resolve();
                                });
                            } else {
                                this.addReferences(cc.citation_level_2, [baseCit]).finally(() => {
                                    this.addLevel3References(relTextRangePart, cc).then(() => {
                                        return resolve();
                                    });
                                });
                            }
                        });
                    });
                });
            });
        });
    }
}
