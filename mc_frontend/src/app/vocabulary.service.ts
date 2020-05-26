/* tslint:disable:no-string-literal */
import {HttpClient, HttpErrorResponse, HttpParams} from '@angular/common/http';
import {Injectable, OnInit} from '@angular/core';
import {VocabularyCorpus} from 'src/app/models/enum';
import {Vocabulary} from 'src/app/models/vocabulary';
import {Sentence} from 'src/app/models/sentence';
import {HelperService} from 'src/app/helper.service';
import {TestResultMC} from 'src/app/models/testResultMC';
import {ToastController} from '@ionic/angular';
import configMC from '../configMC';
import {AnnisResponse} from '../../openapi';

@Injectable({
    providedIn: 'root'
})
export class VocabularyService implements OnInit {
    currentReferenceVocabulary: VocabularyCorpus = VocabularyCorpus.bws;
    currentSentences: Sentence[] = [];
    currentTestResults: { [exerciseIndex: number]: TestResultMC } = {};
    desiredSentenceCount = 10;
    frequencyUpperBound = 500;
    ranking: Sentence[][] = [];
    refVocMap: { [refVoc: string]: Vocabulary } = {};

    constructor(public http: HttpClient,
                public toastCtrl: ToastController,
                public helperService: HelperService) {
        this.ngOnInit();
    }

    getCurrentReferenceVocabulary(): Vocabulary {
        return this.refVocMap[this.currentReferenceVocabulary];
    }

    getMean(sentences: Sentence[]): number {
        return sentences.map(x => x.matching_degree).reduce((a, b) => a + b) / sentences.length;
    }

    getPossibleSubCount(): number {
        return this.getCurrentReferenceVocabulary().possibleSubcounts[0];
    }

    getVocabularyCheck(queryUrn: string, showOOV: boolean): Promise<AnnisResponse | Sentence[]> {
        return new Promise(((resolve, reject) => {
            const url: string = configMC.backendBaseUrl + configMC.backendApiVocabularyPath;
            const params: HttpParams = new HttpParams()
                .set('vocabulary', VocabularyCorpus[this.currentReferenceVocabulary])
                .set('frequency_upper_bound', this.frequencyUpperBound.toString())
                .set('query_urn', queryUrn)
                .set('show_oov', showOOV ? '1' : '0');
            this.helperService.makeGetRequest(this.http, this.toastCtrl, url, params).then((result: AnnisResponse | Sentence[]) => {
                return resolve(result);
            }, (error: HttpErrorResponse) => {
                return reject(error);
            });
        }));
    }

    ngOnInit(): void {
        this.refVocMap[VocabularyCorpus.agldt] = new Vocabulary({
            hasFrequencyOrder: true,
            totalCount: 7182,
            possibleSubcounts: []
        });
        this.refVocMap[VocabularyCorpus.bws] = new Vocabulary({
            hasFrequencyOrder: false,
            totalCount: 1276,
            possibleSubcounts: [500, 1276]
        });
        this.refVocMap[VocabularyCorpus.proiel] = new Vocabulary({
            hasFrequencyOrder: true,
            totalCount: 16402,
            possibleSubcounts: []
        });
        this.refVocMap[VocabularyCorpus.viva] = new Vocabulary({
            hasFrequencyOrder: false,
            totalCount: 1164,
            possibleSubcounts: [1164]
        });
    }

    updateReferenceRange(): void {
        const hasFreq: boolean = this.getCurrentReferenceVocabulary().hasFrequencyOrder;
        this.frequencyUpperBound = hasFreq ? 500 : this.getPossibleSubCount();
    }
}
