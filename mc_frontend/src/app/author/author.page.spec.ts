import {CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {async, ComponentFixture, TestBed} from '@angular/core/testing';

import {AuthorPage} from './author.page';
import {FormsModule} from '@angular/forms';
import {RouterModule} from '@angular/router';
import {HttpClientModule} from '@angular/common/http';
import {IonicStorageModule} from '@ionic/storage';
import {TranslateTestingModule} from '../translate-testing/translate-testing.module';
import {APP_BASE_HREF} from '@angular/common';
import {Author} from '../models/author';
import {CorpusMC} from '../models/corpusMC';
import Spy = jasmine.Spy;
import MockMC from '../models/mockMC';

describe('AuthorPage', () => {
    let authorPage: AuthorPage;
    let fixture: ComponentFixture<AuthorPage>;

    beforeEach(async(() => {
        TestBed.configureTestingModule({
            declarations: [
                AuthorPage,
            ],
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
            .compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(AuthorPage);
        authorPage = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(authorPage).toBeTruthy();
    });

    it('should filter an author', () => {
        const result: boolean = AuthorPage.filterAuthor(new Author({name: 'name'}), 'b');
        expect(result).toBe(false);
    });

    it('should get authors', () => {
        authorPage.showOnlyTreebanks = true;
        authorPage.getAuthors('');
        expect(authorPage.authorsDisplayed).toBe(authorPage.baseAuthorList);
        authorPage.showOnlyTreebanks = false;
        authorPage.getAuthors('');
        expect(authorPage.authorsDisplayed).toBe(authorPage.corpusService.availableAuthors);
        authorPage.baseAuthorList.push(new Author({name: 'test'}));
        authorPage.getAuthors('test');
        expect(authorPage.authorsDisplayed.length).toBe(1);
    });

    it('should be initialized', () => {
        authorPage.corpusService.availableAuthors = [new Author({
            corpora: [new CorpusMC({source_urn: 'proiel'})],
            name: 'name'
        })];
        authorPage.ngOnInit();
        expect(authorPage.baseAuthorList.length).toBe(1);
    });

    it('should restore the last setup', (done) => {
        const restoreSpy: Spy = spyOn(authorPage.corpusService, 'restoreLastCorpus').and.callFake(() => Promise.reject());
        const showTextSpy: Spy = spyOn(authorPage.helperService, 'goToShowTextPage').and.returnValue(Promise.resolve(true));
        const vocCheckSpy: Spy = spyOn(authorPage.helperService, 'goToVocabularyCheckPage').and.returnValue(Promise.resolve(true));
        authorPage.helperService.isVocabularyCheck = false;
        authorPage.restoreLastSetup().then(() => {
        }, () => {
            expect(showTextSpy).toHaveBeenCalledTimes(0);
            restoreSpy.and.returnValue(Promise.resolve());
            authorPage.restoreLastSetup().then(() => {
                expect(showTextSpy).toHaveBeenCalledTimes(1);
                authorPage.helperService.isVocabularyCheck = true;
                authorPage.restoreLastSetup().then(() => {
                    expect(vocCheckSpy).toHaveBeenCalledTimes(1);
                    const a = 0;
                    done();
                });
            });
        });
    });

    it('should show corpora', () => {
        authorPage.helperService.applicationState.next(authorPage.helperService.deepCopy(MockMC.applicationState));
        spyOn(authorPage.helperService, 'goToAuthorDetailPage').and.returnValue(Promise.resolve(true));
        const author: Author = new Author({name: '', corpora: []});
        authorPage.showCorpora(author);
        expect(authorPage.corpusService.currentAuthor).toBe(author);
    });
});
