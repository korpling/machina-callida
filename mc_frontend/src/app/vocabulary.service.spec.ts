import {TestBed} from '@angular/core/testing';

import {VocabularyService} from './vocabulary.service';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {IonicStorageModule} from '@ionic/storage';
import {TranslateTestingModule} from './translate-testing/translate-testing.module';
import {HttpErrorResponse, HttpParams} from '@angular/common/http';
import {AnnisResponse, Sentence, VocabularyForm, VocabularyMC} from '../../openapi';
import Spy = jasmine.Spy;

describe('VocabularyService', () => {
    let vocabularyService: VocabularyService;
    beforeEach(() => {
            TestBed.configureTestingModule({
                imports: [
                    HttpClientTestingModule,
                    IonicStorageModule.forRoot(),
                    TranslateTestingModule,
                ],
                providers: [],
            });
            vocabularyService = TestBed.inject(VocabularyService);
        }
    );

    it('should be created', () => {
        expect(vocabularyService).toBeTruthy();
        const sentences: Sentence[] = [{matching_degree: 3}, {matching_degree: 7}];
        expect(vocabularyService.getMean(sentences)).toBe(5);
    });
    it('should get a vocabulary check', (done) => {
        const error: HttpErrorResponse = new HttpErrorResponse({status: 500});
        const getSpy: Spy = spyOn(vocabularyService.helperService, 'makeGetRequest').and.callFake(() => Promise.reject(error));
        vocabularyService.getMatchingSentences('').then(() => {
        }, async (response: HttpErrorResponse) => {
            expect(response.status).toBe(500);
            getSpy.and.returnValue(Promise.resolve([]));
            const sentences: Sentence[] = await vocabularyService.getMatchingSentences('');
            expect(sentences.length).toBe(0);
            const params: HttpParams = getSpy.calls.argsFor(0)[3];
            const vfObj: object = {};
            params.keys().forEach((key: string) => vfObj[key] = params.get(key));
            const vf: VocabularyForm = vfObj as VocabularyForm;
            expect(vf.vocabulary).toBe(VocabularyMC.Bws);
            const postSpy: Spy = spyOn(vocabularyService.helperService, 'makePostRequest').and.returnValue(Promise.resolve({}));
            const result: AnnisResponse = await vocabularyService.getOOVwords('');
            expect(result.graph_data).toBeFalsy();
            postSpy.and.callFake(() => Promise.reject(error));
            vocabularyService.getOOVwords('').then(() => {
            }, (resp: HttpErrorResponse) => {
                expect(resp.status).toBe(500);
                done();
            });
        });
    });

    it('should be initialized', () => {
        vocabularyService.ngOnInit();
        expect(Object.keys(vocabularyService.refVocMap).length).toBe(4);
        expect(vocabularyService.getCurrentReferenceVocabulary().totalCount).toBe(1276);
        expect(vocabularyService.getPossibleSubCount()).toBe(500);
    });

    it('should update the reference range', () => {
        vocabularyService.frequencyUpperBound = 0;
        vocabularyService.ngOnInit();
        vocabularyService.currentReferenceVocabulary = VocabularyMC.Agldt;
        vocabularyService.updateReferenceRange();
        expect(vocabularyService.frequencyUpperBound).toBe(500);
        vocabularyService.currentReferenceVocabulary = VocabularyMC.Viva;
        vocabularyService.updateReferenceRange();
        expect(vocabularyService.frequencyUpperBound).toBe(1164);
    });
});
