import {TestBed} from '@angular/core/testing';

import {VocabularyService} from './vocabulary.service';
import {HttpClientTestingModule} from '@angular/common/http/testing';
import {IonicStorageModule} from '@ionic/storage';
import {TranslateTestingModule} from './translate-testing/translate-testing.module';
import {VocabularyCorpus} from './models/enum';
import {Sentence} from './models/sentence';
import {AnnisResponse} from './models/annisResponse';
import {HttpErrorResponse} from '@angular/common/http';
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
        const sentences: Sentence[] = [new Sentence({matching_degree: 3}), new Sentence({matching_degree: 7})];
        expect(vocabularyService.getMean(sentences)).toBe(5);
    });
    it('should get a vocabulary check', (done) => {
        const error: HttpErrorResponse = new HttpErrorResponse({status: 500});
        const requestSpy: Spy = spyOn(vocabularyService.helperService, 'makeGetRequest')
            .and.callFake(() => Promise.reject(error));
        // result: AnnisResponse | Sentence[]
        vocabularyService.getVocabularyCheck('', false).then(() => {
        }, async (response: HttpErrorResponse) => {
            expect(response.status).toBe(500);
            requestSpy.and.returnValue(Promise.resolve(new AnnisResponse()));
            const result: AnnisResponse | Sentence[] = await vocabularyService.getVocabularyCheck('', true);
            expect(result.hasOwnProperty('length')).toBe(false);
            done();
        });
    });

    it('should be initialized', () => {
        vocabularyService.ngOnInit();
        expect(Object.keys(vocabularyService.refVocMap).length).toBe(4);
        // vocabularyService.currentReferenceVocabulary = VocabularyCorpus.bws;
        expect(vocabularyService.getCurrentReferenceVocabulary().totalCount).toBe(1276);
        expect(vocabularyService.getPossibleSubCount()).toBe(500);
    });

    it('should update the reference range', () => {
        vocabularyService.frequencyUpperBound = 0;
        vocabularyService.ngOnInit();
        vocabularyService.currentReferenceVocabulary = VocabularyCorpus.agldt;
        vocabularyService.updateReferenceRange();
        expect(vocabularyService.frequencyUpperBound).toBe(500);
        vocabularyService.currentReferenceVocabulary = VocabularyCorpus.viva;
        vocabularyService.updateReferenceRange();
        expect(vocabularyService.frequencyUpperBound).toBe(1164);
    });
});
