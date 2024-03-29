/* tslint:disable:no-string-literal */
import {HttpClient, HttpErrorResponse, HttpParams} from '@angular/common/http';
import {Injectable, OnInit} from '@angular/core';
import {Vocabulary} from 'src/app/models/vocabulary';
import {HelperService} from 'src/app/helper.service';
import {TestResultMC} from 'src/app/models/testResultMC';
import {ToastController} from '@ionic/angular';
import configMC from '../configMC';
import {AnnisResponse, Sentence, VocabularyForm} from '../../openapi';
import {VocabularyMC} from '../../openapi';

@Injectable({
    providedIn: 'root'
})
export class VocabularyService implements OnInit {
    currentReferenceVocabulary: VocabularyMC = VocabularyMC.Bws;
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

    getMatchingSentences(queryUrn: string): Promise<Sentence[]> {
        return new Promise((resolve, reject) => {
            const url: string = configMC.backendBaseUrl + configMC.backendApiVocabularyPath;
            const vf: VocabularyForm = {
                frequency_upper_bound: this.frequencyUpperBound,
                query_urn: queryUrn,
                vocabulary: this.currentReferenceVocabulary
            };
            let params: HttpParams = new HttpParams();
            Object.keys(vf).forEach((key: string) => {
                params = params.set(key, vf[key]);
            });
            this.helperService.makeGetRequest(this.http, this.toastCtrl, url, params).then((result: Sentence[]) => {
                return resolve(result);
            }, (error: HttpErrorResponse) => {
                return reject(error);
            });
        });
    }

    getMean(sentences: Sentence[]): number {
        return sentences.map(x => x.matching_degree).reduce((a, b) => a + b) / sentences.length;
    }

    getOOVwords(queryUrn: string): Promise<AnnisResponse> {
        return new Promise(((resolve, reject) => {
            const url: string = configMC.backendBaseUrl + configMC.backendApiVocabularyPath;
            const vf: VocabularyForm = {
                frequency_upper_bound: this.frequencyUpperBound,
                query_urn: queryUrn,
                vocabulary: this.currentReferenceVocabulary
            };
            const formData: FormData = new FormData();
            Object.keys(vf).forEach((key: string) => formData.append(key, vf[key]));
            this.helperService.makePostRequest(this.http, this.toastCtrl, url, formData).then((result: AnnisResponse) => {
                return resolve(result);
            }, (error: HttpErrorResponse) => {
                return reject(error);
            });
        }));
    }

    getPossibleSubCount(): number {
        return this.getCurrentReferenceVocabulary().possibleSubcounts[0];
    }

    ngOnInit(): void {
        this.refVocMap[VocabularyMC.Agldt] = new Vocabulary({
            hasFrequencyOrder: true,
            totalCount: 7182,
            possibleSubcounts: []
        });
        this.refVocMap[VocabularyMC.Bws] = new Vocabulary({
            hasFrequencyOrder: false,
            totalCount: 1276,
            possibleSubcounts: [500, 1276]
        });
        this.refVocMap[VocabularyMC.Proiel] = new Vocabulary({
            hasFrequencyOrder: true,
            totalCount: 16402,
            possibleSubcounts: []
        });
        this.refVocMap[VocabularyMC.Viva] = new Vocabulary({
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
