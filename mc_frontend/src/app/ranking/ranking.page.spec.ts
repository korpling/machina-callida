import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {RankingPage} from './ranking.page';
import {HttpClientModule} from '@angular/common/http';
import {IonicStorageModule} from '@ionic/storage';
import {RouterModule} from '@angular/router';
import {TranslateTestingModule} from '../translate-testing/translate-testing.module';
import {APP_BASE_HREF} from '@angular/common';
import {Sentence} from '../models/sentence';
import Spy = jasmine.Spy;
import {AnnisResponse} from '../../../openapi';

describe('RankingPage', () => {
    let rankingPage: RankingPage;
    let fixture: ComponentFixture<RankingPage>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [RankingPage],
            imports: [
                HttpClientModule,
                IonicStorageModule.forRoot(),
                RouterModule.forRoot([]),
                TranslateTestingModule,
            ],
            providers: [
                {provide: APP_BASE_HREF, useValue: '/'},
            ],
            schemas: [CUSTOM_ELEMENTS_SCHEMA],
        })
            .compileComponents().then();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(RankingPage);
        rankingPage = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(rankingPage).toBeTruthy();
    });

    it('should show the text', (done) => {
        rankingPage.helperService.isVocabularyCheck = false;
        const ar: AnnisResponse = {graph_data: {nodes: [{id: 'id/id:1-2/id'}], links: []}};
        const vocCheckSpy: Spy = spyOn(rankingPage.vocService, 'getVocabularyCheck').and.returnValue(Promise.resolve(ar));
        spyOn(rankingPage.corpusService, 'processAnnisResponse');
        spyOn(rankingPage.helperService, 'goToShowTextPage').and.returnValue(Promise.resolve(true));
        rankingPage.showText([new Sentence({id: 1})]).then(() => {
            expect(rankingPage.helperService.isVocabularyCheck).toBe(true);
            vocCheckSpy.and.callFake(() => Promise.reject());
            rankingPage.helperService.isVocabularyCheck = false;
            rankingPage.showText([new Sentence({id: 1})]).then(() => {
            }, () => {
                expect(rankingPage.helperService.isVocabularyCheck).toBe(false);
                done();
            });
        });
    });
});
