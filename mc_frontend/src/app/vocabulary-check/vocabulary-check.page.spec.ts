import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {VocabularyCheckPage} from './vocabulary-check.page';
import {HttpClientModule} from '@angular/common/http';
import {IonicStorageModule} from '@ionic/storage';
import {RouterModule} from '@angular/router';
import {TranslateTestingModule} from '../translate-testing/translate-testing.module';
import {FormsModule} from '@angular/forms';
import {APP_BASE_HREF} from '@angular/common';
import MockMC from '../models/mockMC';
import Spy = jasmine.Spy;
import {Sentence} from '../models/sentence';

describe('VocabularyCheckPage', () => {
    let vocabularyCheckPage: VocabularyCheckPage;
    let fixture: ComponentFixture<VocabularyCheckPage>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [VocabularyCheckPage],
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
        fixture = TestBed.createComponent(VocabularyCheckPage);
        vocabularyCheckPage = fixture.componentInstance;
        vocabularyCheckPage.vocService.ngOnInit();
        fixture.detectChanges();
    });

    it('should create', (done) => {
        expect(vocabularyCheckPage).toBeTruthy();
        expect(vocabularyCheckPage.filterArray(['', 'a']).length).toBe(1);
        const navSpy: Spy = spyOn(vocabularyCheckPage.helperService, 'goToAuthorPage').and.returnValue(Promise.resolve(true));
        vocabularyCheckPage.chooseCorpus().then(() => {
            expect(navSpy).toHaveBeenCalledTimes(1);
            done();
        });
    });

    it('should check vocabulary', (done) => {
        vocabularyCheckPage.corpusService.initCurrentCorpus();
        vocabularyCheckPage.corpusService.initCurrentTextRange();
        vocabularyCheckPage.helperService.applicationState.next(vocabularyCheckPage.helperService.deepCopy(MockMC.applicationState));
        vocabularyCheckPage.vocService.frequencyUpperBound = -1;
        const getVocSpy: Spy = spyOn(vocabularyCheckPage.vocService, 'getVocabularyCheck')
            .and.returnValue(Promise.resolve([]));
        const navSpy: Spy = spyOn(vocabularyCheckPage.helperService, 'goToRankingPage').and.returnValue(Promise.resolve(true));
        vocabularyCheckPage.checkVocabulary().then(async () => {
            expect(getVocSpy).toHaveBeenCalledTimes(0);
            vocabularyCheckPage.vocService.frequencyUpperBound = 500;
            vocabularyCheckPage.corpusService.isTextRangeCorrect = false;
            await vocabularyCheckPage.checkVocabulary();
            expect(getVocSpy).toHaveBeenCalledTimes(0);
            vocabularyCheckPage.corpusService.isTextRangeCorrect = true;
            await vocabularyCheckPage.checkVocabulary();
            expect(navSpy).toHaveBeenCalledTimes(1);
            getVocSpy.and.callFake(() => Promise.reject());
            await vocabularyCheckPage.checkVocabulary();
            expect(navSpy).toHaveBeenCalledTimes(1);
            done();
        });
    });

    it('should process sentences', () => {
        vocabularyCheckPage.currentRankingUnits = [];
        const sentences: Sentence[] = Array(50).fill(null).map(x => new Sentence({matching_degree: 40}));
        sentences[0].matching_degree = 49;
        sentences[10].matching_degree = 50;
        sentences[14].matching_degree = 80;
        sentences[25].matching_degree = 5;
        vocabularyCheckPage.processSentences(sentences);
        expect(vocabularyCheckPage.currentRankingUnits.length).toBe(5);
    });
});
