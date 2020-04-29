import {NavController, ToastController} from '@ionic/angular';
import {Component} from '@angular/core';
import {VocabularyCorpus, VocabularyCorpusTranslation} from 'src/app/models/enum';
import {VocabularyService} from 'src/app/vocabulary.service';
import {HttpClient, HttpErrorResponse} from '@angular/common/http';
import {Sentence} from 'src/app/models/sentence';
import {TranslateService} from '@ngx-translate/core';
import {HelperService} from '../helper.service';
import {ExerciseService} from 'src/app/exercise.service';
import {CorpusService} from 'src/app/corpus.service';
import {CorpusMC} from '../models/corpusMC';
import {take} from 'rxjs/operators';
import {TextRange} from '../models/textRange';

@Component({
    selector: 'app-vocabulary-check',
    templateUrl: './vocabulary-check.page.html',
    styleUrls: ['./vocabulary-check.page.scss'],
})
export class VocabularyCheckPage {
    ObjectKeys = Object.keys;
    VocabularyCorpus = VocabularyCorpus;
    VocabularyCorpusTranslation = VocabularyCorpusTranslation;
    public adaptPassages = true;
    public currentRankingUnits: Sentence[][];

    constructor(public navCtrl: NavController,
                public vocService: VocabularyService,
                public toastCtrl: ToastController,
                public translate: TranslateService,
                public corpusService: CorpusService,
                public http: HttpClient,
                public exerciseService: ExerciseService,
                public helperService: HelperService) {
    }

    checkVocabulary(): Promise<void> {
        return new Promise<void>((resolve) => {
            this.corpusService.currentCorpus.pipe(take(1)).subscribe(async (cc: CorpusMC) => {
                this.corpusService.currentTextRange.pipe(take(1)).subscribe(async (tr: TextRange) => {
                    if (this.vocService.desiredSentenceCount < 0 || this.vocService.frequencyUpperBound < 0) {
                        this.helperService.showToast(this.toastCtrl, this.corpusService.invalidSentenceCountString).then();
                        return resolve();
                    } else if (!cc || tr.start.length === 0 || tr.end.length === 0 || !this.corpusService.isTextRangeCorrect) {
                        this.helperService.showToast(this.toastCtrl, this.corpusService.invalidQueryCorpusString).then();
                        return resolve();
                    }
                    this.vocService.currentSentences = [];
                    this.currentRankingUnits = [];
                    this.vocService.ranking = [];
                    // remove old sentence boundaries
                    this.corpusService.currentUrn = this.corpusService.currentUrn.split('@')[0];
                    this.vocService.getVocabularyCheck(this.corpusService.currentUrn, false).then((sentences: Sentence[]) => {
                        this.processSentences(sentences);
                        this.helperService.goToRankingPage(this.navCtrl).then();
                        return resolve();
                    }, async (error: HttpErrorResponse) => {
                        return resolve();
                    });
                });
            });
        });
    }

    chooseCorpus(): Promise<boolean> {
        return this.helperService.goToAuthorPage(this.navCtrl);
    }

    filterArray(array: string[]): string[] {
        return array.filter(x => x);
    }

    processSentences(sentences: Sentence[]): void {
        if (sentences.length > this.vocService.desiredSentenceCount) {
            this.currentRankingUnits.push([]);
            sentences.forEach((sent: Sentence) => {
                const lastIndex: number = this.currentRankingUnits.length - 1;
                if (this.currentRankingUnits[lastIndex].length < this.vocService.desiredSentenceCount) {
                    this.currentRankingUnits[lastIndex].push(sent);
                } else {
                    if (this.adaptPassages && this.currentRankingUnits[lastIndex][0].matching_degree < sent.matching_degree) {
                        this.currentRankingUnits[lastIndex].splice(0, 1);
                        this.currentRankingUnits[lastIndex].push(sent);
                    } else {
                        this.currentRankingUnits.push([sent]);
                    }
                }
            });
        } else {
            this.currentRankingUnits.push(sentences);
        }
        this.currentRankingUnits.sort((a, b) => {
            const meanA = this.vocService.getMean(a);
            const meanB = this.vocService.getMean(b);
            return meanA > meanB ? -1 : (meanA < meanB ? 1 : 0);
        });
        this.vocService.currentSentences = sentences;
        this.vocService.ranking = this.currentRankingUnits;
    }
}
