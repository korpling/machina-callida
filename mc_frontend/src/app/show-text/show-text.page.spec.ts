import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {ShowTextPage} from './show-text.page';
import {HttpClientModule} from '@angular/common/http';
import {IonicStorageModule} from '@ionic/storage';
import {RouterModule} from '@angular/router';
import {TranslateTestingModule} from '../translate-testing/translate-testing.module';
import {FormsModule} from '@angular/forms';
import {APP_BASE_HREF} from '@angular/common';
import {AnnisResponse} from '../models/annisResponse';
import {NodeMC} from '../models/nodeMC';
import {VocabularyCorpus} from '../models/enum';
import Spy = jasmine.Spy;
import MockMC from '../models/mockMC';

describe('ShowTextPage', () => {
    let showTextPage: ShowTextPage;
    let fixture: ComponentFixture<ShowTextPage>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [ShowTextPage],
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
        })
            .compileComponents().then();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(ShowTextPage);
        showTextPage = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(showTextPage).toBeTruthy();
    });

    it('should generate a download link', (done) => {
        showTextPage.corpusService.initCurrentCorpus();
        showTextPage.helperService.applicationState.next(showTextPage.helperService.deepCopy(MockMC.applicationState));
        showTextPage.corpusService.currentText = 'text';
        fixture.detectChanges();
        const requestSpy: Spy = spyOn(showTextPage.helperService, 'makePostRequest').and.returnValue(Promise.resolve('a.b.c'));
        showTextPage.generateDownloadLink('').then(() => {
            let link: HTMLLinkElement = document.querySelector(showTextPage.downloadLinkSelector);
            expect(link.href.length).toBe(61);
            requestSpy.and.callFake(() => Promise.reject());
            link.style.display = 'none';
            fixture.detectChanges();
            showTextPage.generateDownloadLink('').then(() => {
            }, () => {
                link = document.querySelector(showTextPage.downloadLinkSelector);
                expect(link.style.display).toBe('none');
                done();
            });
        });
    });

    it('should get whitespace', () => {
        showTextPage.corpusService.annisResponse = new AnnisResponse({nodes: []});
        let result: string = showTextPage.getWhiteSpace(0);
        expect(result.length).toBe(0);
        showTextPage.corpusService.annisResponse.nodes = [new NodeMC(), new NodeMC()];
        result = showTextPage.getWhiteSpace(0);
        expect(result.length).toBe(1);
        showTextPage.corpusService.annisResponse.nodes[1].annis_tok = '.';
        result = showTextPage.getWhiteSpace(0);
        expect(result.length).toBe(0);
    });

    it('should be initialized', () => {
        showTextPage.vocService.currentReferenceVocabulary = null;
        showTextPage.ngOnInit();
        expect(showTextPage.vocService.currentReferenceVocabulary).toBe(VocabularyCorpus.bws);
    });
});
